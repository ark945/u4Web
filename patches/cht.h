/*
 * U4 繁中化(cht):en→zh load-time lookup + CJK 16x16 點陣字 glyph 查詢。
 * 資產:cjk_font.bin / u4_cht.tab(由 u4-cht/tools 產生)。
 */
#ifndef CHT_H
#define CHT_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void chtInit(void);                              /* 載入資產(冪等) */
const char* chtLookup(const char* en, int len);  /* en→zh(NUL 結尾)或 NULL */
const uint8_t* chtGlyph(uint32_t codepoint);     /* dim*dim alpha(0/255)或 NULL */
int chtGlyphDim(void);                           /* glyph 邊長(16) */

#ifdef __cplusplus
}
#endif
#endif
