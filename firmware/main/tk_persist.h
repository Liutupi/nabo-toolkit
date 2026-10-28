#pragma once
#include "tk_model.h"
#include "esp_err.h"
esp_err_t tk_persist_load(tk_state_t *state);
esp_err_t tk_persist_save(const tk_state_t *state);
// Independent record: changing screen policy never rewrites legacy settings.
esp_err_t tk_persist_save_remote(const tk_state_t *state);
