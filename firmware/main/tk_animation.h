#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define TK_ANIMATION_PIXELS (115*150)
enum {TK_AN_WELCOME,TK_AN_AVATAR,TK_AN_BASE,TK_AN_MACRO,TK_AN_PPT,TK_AN_MEET,TK_AN_MEDIA,TK_AN_CAM,TK_AN_COUNT};
typedef struct {const uint8_t *data;size_t bytes;} tk_animation_bank_t;
typedef struct {
    uint8_t pixels[TK_ANIMATION_PIXELS],history[4096];
    const uint8_t *clip,*palette;
    size_t clip_bytes;
    unsigned width,height,count,duration;
    int id,frame;
    bool loop,valid;
    uint32_t crc;
} tk_animation_t;
void tk_animation_init(tk_animation_t *a);
bool tk_animation_frame(tk_animation_t *a,const tk_animation_bank_t *bank,unsigned id,uint64_t elapsed);
