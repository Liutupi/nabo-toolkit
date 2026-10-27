#include "tk_config_serial.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
typedef struct {tk_state_t model;tk_config_serial_t wire;char lines[16384];size_t used;int error;} host_t;
static void response(void *context,const char *line){host_t *h=context;int n=snprintf(h->lines+h->used,sizeof(h->lines)-h->used,"%s\n",line);if(n>0 && (size_t)n<sizeof(h->lines)-h->used)h->used+=(size_t)n;}
void *tk_cfg_host_new(void){host_t *h=calloc(1,sizeof(*h));if(h){tk_model_init(&h->model,0);h->error=tk_config_serial_init(&h->wire,&h->model,response,h);}return h;}
void tk_cfg_host_free(void *h){free(h);}
int tk_cfg_host_error(void *h){return ((host_t *)h)->error;}
const char *tk_cfg_host_json(void *h){return ((host_t *)h)->wire.json;}
const char *tk_cfg_host_lines(void *h){return ((host_t *)h)->lines;}
void tk_cfg_host_clear(void *h){((host_t *)h)->used=0;((host_t *)h)->lines[0]=0;}
void tk_cfg_host_line(void *h,const char *line,int64_t now,bool writable){tk_config_serial_line(&((host_t *)h)->wire,line,now,writable);}
void tk_cfg_host_tick(void *h,int64_t now,bool writable){tk_config_serial_tick(&((host_t *)h)->wire,now,writable);}
tk_state_t *tk_cfg_host_state(void *h){return &((host_t *)h)->model;}
size_t tk_cfg_host_custom_size(void){return sizeof(tk_custom_t);}
