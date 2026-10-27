#pragma once
#include "tk_model.h"
// Errors are fixed ASCII codes, never rejected payloads or personal configuration.
const char *tk_config_parse(tk_custom_t *out,const char *json,size_t size);
size_t tk_config_json(const tk_custom_t *config,char *out,size_t capacity);
void tk_config_defaults(tk_custom_t *out);
uint32_t tk_config_crc(const void *data,size_t size);
const char *tk_config_lex(const char *json,size_t size);
bool tk_config_string(const char *s,unsigned count,size_t capacity,bool empty,bool newline);
