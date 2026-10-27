#pragma once
#include "tk_gfx.h"
#include "tk_model.h"
#include "tk_qr.h"
#include "tk_animation.h"
typedef struct { const uint16_t *pixels; const uint8_t *alpha; int w,h; } tk_picture_t;
typedef struct { tk_picture_t avatar,bust,welcome; tk_animation_t *animation; const tk_animation_bank_t *bank; } tk_ui_assets_t;
typedef struct { tk_qr_t qr; char qr_text[512]; uint32_t qr_revision; bool ble_unavailable; } tk_ui_t;
void tk_ui_frame(tk_ui_t *ui,ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *assets,int comparison);
