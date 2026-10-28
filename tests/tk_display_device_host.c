// Adapter sequencing only; no real display, Bluetooth, ADC, USB or NVS access.
#include "tk_f1_device.h"
#include "tk_ui.h"
#include "bsp_display.h"
#include "esp_heap_caps.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include <stdlib.h>
#include <string.h>

const tk_ui_assets_t tk_f1_assets={0};
static char s_events[2048];
static unsigned s_count,s_frames,s_sends,s_fences,s_invalidates;
static int s_light,s_fail;
static int64_t s_time;
static void event(char value){if(s_count<sizeof(s_events)-1){s_events[s_count++]=value;s_events[s_count]=0;}}
void *heap_caps_malloc(size_t size,unsigned flags){(void)flags;return malloc(size);}
void *bsp_display_panel(void){return (void *)1;}
void *bsp_display_io(void){return (void *)2;}
void bsp_display_backlight(uint8_t percent){s_light=percent;event(percent?'L':'D');}
esp_err_t esp_lcd_panel_draw_bitmap(void *panel,int x,int y,int x1,int y1,const void *pixels)
{(void)panel;(void)x;(void)y;(void)x1;(void)y1;(void)pixels;s_sends++;event('S');return ESP_OK;}
esp_err_t esp_lcd_panel_io_tx_param(void *io,int cmd,const void *param,size_t size)
{(void)io;(void)cmd;(void)param;(void)size;s_fences++;event('F');return ESP_OK;}
int64_t esp_timer_get_time(void){s_time+=100;return s_time;}
void ag_init(ag_t *g,uint16_t *a,uint16_t *b,ag_send_fn send,void *ctx)
{memset(g,0,sizeof(*g));g->strip[0]=a;g->strip[1]=b;g->send=send;g->ctx=ctx;}
void ag_invalidate(ag_t *g){g->full=true;s_invalidates++;event('I');}
void tk_ui_frame(tk_ui_t *ui,ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *assets,int comparison)
{(void)ui;(void)s;(void)now;(void)assets;(void)comparison;s_frames++;g->overflow=s_fail!=0;event('R');}
void ag_flush(ag_t *g){g->send(g->ctx,0,0,240,8,g->strip[0]);event('C');g->full=false;}
void tk_display_host_reset(void){s_count=s_frames=s_sends=s_fences=s_invalidates=0;s_events[0]=0;s_fail=0;}
int tk_display_host_draw(int dark,int fail,int64_t now)
{tk_state_t s={0};s.screen_off=dark!=0;s_fail=fail;return tk_f1_ui_draw(&s,now,0,true);}
const char *tk_display_host_events(void){return s_events;}
unsigned tk_display_host_frames(void){return s_frames;}
unsigned tk_display_host_sends(void){return s_sends;}
unsigned tk_display_host_fences(void){return s_fences;}
unsigned tk_display_host_invalidates(void){return s_invalidates;}
int tk_display_host_light(void){return s_light;}
