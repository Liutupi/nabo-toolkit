#pragma once
#include "tk_model.h"
void tk_model_toast(tk_state_t *s, int64_t now, const char *text, bool error);
void tk_model_beep(tk_effects_t *out, const tk_state_t *s, int frequency, int ms);
void tk_model_cue(tk_effects_t *out, int frequency, int ms);
bool tk_model_send(tk_effects_t *out, tk_state_t *s, int64_t now, const tk_binding_t *binding, const char *label, int key);
void tk_model_tools(tk_state_t *s, tk_key_t key, int64_t now, tk_effects_t *out);
void tk_model_connection(tk_state_t *s, tk_key_t key, int64_t now, tk_effects_t *out);
void tk_model_os_pick(tk_state_t *s, tk_key_t key, int64_t now, tk_effects_t *out);
void tk_model_settings(tk_state_t *s, tk_key_t key, tk_effects_t *out);
void tk_model_shoot(tk_state_t *s, int64_t now, tk_effects_t *out);
void tk_model_pair_success(tk_state_t *s, const char *name);
