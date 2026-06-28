#!/usr/bin/env python3
"""Patch gpu_opengl.cpp GLSL shader version for WebGL2 compatibility.

WebGL2 only supports GLSL '#version 300 es', but the xu4 engine defaults to
'#version 330' (desktop OpenGL) or '#version 310 es' (Android/GLES).
This script injects an __EMSCRIPTEN__ preprocessor check so that when compiled
with Emscripten, the correct '#version 300 es' is used.
"""

import sys

filepath = sys.argv[1] if len(sys.argv) > 1 else 'xu4/src/gpu_opengl.cpp'

with open(filepath, 'r') as f:
    content = f.read()

old = '#ifdef ANDROID'
new = '''#ifdef __EMSCRIPTEN__
#define DVERSION    "#version 300 es\\n"
#define PRECISION_F "precision highp float;\\n"
#elif defined(ANDROID)'''

if old in content:
    content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}: GLSL version set to '300 es' for Emscripten")
else:
    print(f"Warning: pattern not found in {filepath}")
