#pragma once
#include "tk_ui.h"
#include "tk_fonts.h"
#define UI_BG 0x1107
#define UI_PANEL 0x2189
#define UI_INK 0x1927
#define UI_PAPER 0xef3b
#define UI_GOLD 0xfd70
#define UI_DIM 0x7bef
#define UI_RED 0xe28a
#define UI_GREEN 0x4e11
extern const uint16_t tk_ui_accents[11];
void ui_text(ag_t *g,const char *s,int x,int y,int size,uint16_t color,nt_align_t align);
void ui_fit(ag_t *g,const char *s,int x,int y,int width,int size,uint16_t color,nt_align_t align);
void ui_bar(ag_t *g,const char *s);
void ui_popup(ag_t *g,int height);
void ui_picture(ag_t *g,const tk_picture_t *p,int x,int y);
void ui_nabo(ag_t *g,const tk_ui_assets_t *a,unsigned id,int cx,int bottom,int64_t elapsed);
void ui_boot(ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a);
void ui_icon(ag_t *g,unsigned id,int cx,int cy,uint16_t color);
void ui_tools(ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a);
void ui_connections(ag_t *g,const tk_state_t *s,int64_t now,int comparison);
void ui_card(tk_ui_t *ui,ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a);
