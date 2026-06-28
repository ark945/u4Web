#!/usr/bin/env python3
"""Patch xu4 GLSL shaders, OpenGL code, and Faun support for WebGL2/Emscripten compatibility.

WebGL2 only supports GLSL '#version 300 es', but the xu4 engine defaults to
'#version 330' (desktop OpenGL) or '#version 310 es' (Android/GLES).

This script fixes:
1. gpu_opengl.cpp: Injects __EMSCRIPTEN__ preprocessor check for GLSL version.
2. gpu_opengl.cpp: Fixes GL_RGB internal format (invalid in WebGL2 with RGBA data).
3. External .glsl files: Removes trailing ';' after function closing braces.
4. External .glsl files: Removes 'f' suffix from float literals (invalid in GLSL ES).
5. faun/support/tmsg.c: Stubs sem_timedwait for single-threaded Emscripten builds to prevent link failures.
"""

import glob
import os
import re
import sys


def patch_gpu_opengl(filepath):
    """Add __EMSCRIPTEN__ check for GLSL version and fix GL format in gpu_opengl.cpp."""
    with open(filepath, 'r') as f:
        content = f.read()

    changed = False

    # 1) Add GLSL 300 es version for Emscripten
    old_version = '#ifdef ANDROID'
    new_version = (
        '#ifdef __EMSCRIPTEN__\n'
        '#define DVERSION    "#version 300 es\\n"\n'
        '#define PRECISION_F "precision highp float;\\n"\n'
        '#elif defined(ANDROID)'
    )
    if old_version in content and '__EMSCRIPTEN__' not in content:
        content = content.replace(old_version, new_version)
        print(f"  [OK] GLSL version set to '300 es' for Emscripten")
        changed = True

    # 2) Fix GL_RGB internal format: WebGL2 requires matching internal/external formats
    #    The check `#if defined(ANDROID) || defined(USE_GLES)` should also include Emscripten
    old_check = '#if defined(ANDROID) || defined(USE_GLES)'
    new_check = '#if defined(ANDROID) || defined(USE_GLES) || defined(__EMSCRIPTEN__)'
    if old_check in content:
        content = content.replace(old_check, new_check)
        print(f"  [OK] Added __EMSCRIPTEN__ to GLES format checks")
        changed = True

    if changed:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  Patched {filepath}")
    else:
        print(f"  No changes needed in {filepath}")


def patch_faun_tmsg(gpu_cpp_path):
    """Patch tmsg.c to stub sem_timedwait when compiled without pthreads."""
    tmsg_path = os.path.join(os.path.dirname(gpu_cpp_path), 'faun', 'support', 'tmsg.c')
    if not os.path.exists(tmsg_path):
        print(f"  [Info] tmsg.c not found at {tmsg_path}, skipping faun patch")
        return

    with open(tmsg_path, 'r') as f:
        content = f.read()

    stub = (
        '#include <semaphore.h>\n'
        '#if defined(__EMSCRIPTEN__) && !defined(__EMSCRIPTEN_PTHREADS__)\n'
        '#include <errno.h>\n'
        '#include <time.h>\n'
        'int sem_timedwait(sem_t *sem, const struct timespec *abs_timeout) {\n'
        '    if (sem_trywait(sem) == 0) return 0;\n'
        '    errno = ETIMEDOUT;\n'
        '    return -1;\n'
        '}\n'
        '#endif'
    )

    if '#include <semaphore.h>' in content and 'int sem_timedwait' not in content:
        content = content.replace('#include <semaphore.h>', stub)
        with open(tmsg_path, 'w') as f:
            f.write(content)
        print(f"  [OK] Stubbed sem_timedwait in {tmsg_path}")
    else:
        print(f"  [Info] No faun tmsg.c patch needed (already patched or include missing)")


def patch_shader_files(shader_dir):
    """Fix GLSL ES syntax issues in shader files."""
    patterns = [
        os.path.join(shader_dir, '**', '*.glsl'),
        os.path.join(shader_dir, '**', '*.gl'),
    ]

    count = 0
    for pattern in patterns:
        for filepath in glob.glob(pattern, recursive=True):
            with open(filepath, 'r') as f:
                content = f.read()

            original = content

            # Fix 1: Trailing semicolons after function closing braces
            # "};" is accepted by GLSL 330 but invalid in GLSL 300 es
            content = content.replace('};\n', '}\n')
            content = content.replace('};\r\n', '}\r\n')

            # Fix 2: Remove 'f' suffix from float literals (invalid in GLSL ES)
            # Match patterns like 0.001f, 1.0f, etc. but not inside words
            content = re.sub(r'(\b\d+\.\d+)f\b', r'\1', content)
            content = re.sub(r'(\b\d+\.)f\b', r'\1', content)

            if content != original:
                with open(filepath, 'w') as f:
                    f.write(content)
                basename = os.path.basename(filepath)
                print(f"  [OK] Fixed GLSL ES syntax in {basename}")
                count += 1

    if count == 0:
        print(f"  No shader files needed fixing in {shader_dir}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fix_webgl_shaders.py <gpu_opengl.cpp> [shader_dir]")
        sys.exit(1)

    gpu_cpp = sys.argv[1]
    print("Patching gpu_opengl.cpp...")
    patch_gpu_opengl(gpu_cpp)

    print("Patching faun/support/tmsg.c if present...")
    patch_faun_tmsg(gpu_cpp)

    if len(sys.argv) >= 3:
        shader_dir = sys.argv[2]
        print(f"Fixing shader files in {shader_dir}...")
        patch_shader_files(shader_dir)
