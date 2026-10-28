#pragma once
#include "tk_model.h"
#include "esp_err.h"

// UI-task adapter. The worker never touches the model or emits HID.
esp_err_t tk_voice_bridge_init(tk_state_t *model);
void tk_voice_bridge_tick(tk_state_t *model,int64_t now,bool allowed,bool keep_muted);
bool tk_voice_bridge_busy(void);
bool tk_voice_bridge_command(tk_state_t *model,const char *text,int64_t now,bool allowed,tk_effects_t *scratch);
