#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct {const uint8_t *pcm;size_t frames,position;uint32_t phase,step;unsigned tone_left,tone_total;} tk_audio_mix_t;
void tk_audio_mix_init(tk_audio_mix_t *m,const uint8_t *pcm,size_t bytes);
void tk_audio_mix_voice(tk_audio_mix_t *m,bool play);
void tk_audio_mix_tone(tk_audio_mix_t *m,unsigned frequency,unsigned ms);
bool tk_audio_mix_fill(tk_audio_mix_t *m,int16_t *out,size_t frames);
