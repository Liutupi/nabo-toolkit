#pragma once
#include "lvgl.h"
bool tk_cjk_descriptor(uint32_t id,lv_font_fmt_txt_glyph_dsc_t *out);
bool tk_cjk_get_glyph_dsc(const lv_font_t *font,lv_font_glyph_dsc_t *out,uint32_t code,uint32_t next);
const void *tk_cjk_get_bitmap(lv_font_glyph_dsc_t *dsc,lv_draw_buf_t *buffer);
