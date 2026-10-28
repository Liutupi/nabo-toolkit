#pragma once
#include "esp_err.h"
#include <stddef.h>
#include <stdint.h>
typedef unsigned nvs_handle_t;
typedef struct {size_t used_entries,free_entries,total_entries,namespace_count,available_entries;} nvs_stats_t;
#define NVS_READONLY 0
#define NVS_READWRITE 1
esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle);
esp_err_t nvs_get_blob(nvs_handle_t handle,const char *key,void *data,size_t *size);
esp_err_t nvs_set_blob(nvs_handle_t handle,const char *key,const void *data,size_t size);
esp_err_t nvs_get_u8(nvs_handle_t handle,const char *key,uint8_t *value);
esp_err_t nvs_commit(nvs_handle_t handle);
esp_err_t nvs_erase_key(nvs_handle_t handle,const char *key);
esp_err_t nvs_get_stats(const char *partition,nvs_stats_t *stats);
void nvs_close(nvs_handle_t handle);
