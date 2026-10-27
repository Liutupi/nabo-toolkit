#pragma once
#include "tk_model.h"
#include "esp_err.h"
bool tk_f1_ui_open(void);
bool tk_f1_ui_draw(const tk_state_t *state,int64_t now,int comparison,bool ble_available);
unsigned tk_f1_ui_max_draw_us(void);
int tk_f1_ui_animation_id(void);
int tk_f1_ui_animation_frame(void);
esp_err_t tk_sound_open(void);
bool tk_sound_tone(unsigned frequency,unsigned ms);
bool tk_sound_idle(void);
void tk_sound_mute(bool muted);
bool tk_sound_prepare_sleep(void);
bool tk_sound_boot_voice(void);
void tk_sound_stop_voice(void);
typedef struct {unsigned writes,errors,nonzero,voice_starts,tone_starts;int last_error;bool muted;} tk_sound_stats_t;
tk_sound_stats_t tk_sound_stats(void);
