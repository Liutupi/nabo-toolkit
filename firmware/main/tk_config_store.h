#pragma once
#include "tk_config.h"
#include "esp_err.h"
esp_err_t tk_config_store_load(tk_custom_t *out,char json[TK_CFG_MAX+1],size_t *size);
// Caller has validated/canonicalized JSON. One versioned CRC envelope, no NVS erase.
esp_err_t tk_config_store_save(const char *json,size_t size);
