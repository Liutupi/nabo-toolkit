#pragma once
#include "tk_config_store.h"
typedef void (*tk_config_reply_t)(void *context,const char *line);
typedef struct {
    tk_custom_t current;char json[TK_CFG_MAX+1],incoming[TK_CFG_MAX+1];
    size_t size,expected,received,read_offset;int64_t started,last_data;
    bool receiving,reading;tk_state_t *model;tk_config_reply_t reply;void *context;
} tk_config_serial_t;
esp_err_t tk_config_serial_init(tk_config_serial_t *s,tk_state_t *model,tk_config_reply_t reply,void *context);
bool tk_config_serial_line(tk_config_serial_t *s,const char *line,int64_t now,bool writable);
void tk_config_serial_tick(tk_config_serial_t *s,int64_t now,bool writable);
bool tk_config_serial_busy(const tk_config_serial_t *s);
