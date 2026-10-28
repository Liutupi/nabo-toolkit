#include "tk_f1_device.h"
#include "tk_ui.h"
#include <stdlib.h>
#include "bsp_display.h"
#include "esp_heap_caps.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_timer.h"
extern const tk_ui_assets_t tk_f1_assets;
static ag_t *s_graphics;
static tk_ui_t *s_ui;
static uint16_t *s_strips[2];
static unsigned s_max_draw_us;
static bool s_display_dark=true;
unsigned tk_f1_ui_max_draw_us(void){return s_max_draw_us;}
int tk_f1_ui_animation_id(void){return tk_f1_assets.animation && tk_f1_assets.animation->valid?tk_f1_assets.animation->id:-1;}
int tk_f1_ui_animation_frame(void){return tk_f1_assets.animation && tk_f1_assets.animation->valid?tk_f1_assets.animation->frame:-1;}
static void send(void *context,int x,int y,int w,int h,uint16_t *pixels)
{
    (void)context;ESP_ERROR_CHECK(esp_lcd_panel_draw_bitmap(bsp_display_panel(),x,y,x+w,y+h,pixels));
    ESP_ERROR_CHECK(esp_lcd_panel_io_tx_param(bsp_display_io(),0,NULL,0)); // DMA fence before stripe reuse.
}
bool tk_f1_ui_open(void)
{
    s_graphics=calloc(1,sizeof(*s_graphics));s_ui=calloc(1,sizeof(*s_ui));
    for(int i=0;i<2;i++)s_strips[i]=heap_caps_malloc(240*AG_STRIP*2,MALLOC_CAP_DMA|MALLOC_CAP_INTERNAL);
    if(!s_graphics || !s_ui || !s_strips[0] || !s_strips[1]){
        free(s_graphics);free(s_ui);for(int i=0;i<2;i++)free(s_strips[i]);s_graphics=NULL;s_ui=NULL;return false;
    }
    ag_init(s_graphics,s_strips[0],s_strips[1],send,NULL);return true;
}
bool tk_f1_ui_draw(const tk_state_t *s,int64_t now,int comparison,bool ble_available)
{
    if(s->screen_off){
        if(!s_display_dark)bsp_display_backlight(0);
        s_display_dark=true;return true; // No rendering, sprite decoding or LCD traffic.
    }
    int64_t started=esp_timer_get_time();
    if(s_display_dark)ag_invalidate(s_graphics);
    s_ui->ble_unavailable=!ble_available;
    tk_ui_frame(s_ui,s_graphics,s,now,&tk_f1_assets,comparison);
    if(s_graphics->overflow)return false;
    ag_flush(s_graphics);unsigned elapsed=(unsigned)(esp_timer_get_time()-started);
    if(elapsed>s_max_draw_us)s_max_draw_us=elapsed;
    // send() fences each strip, so the entire new frame is visible before light.
    if(s_display_dark){bsp_display_backlight(80);s_display_dark=false;}
    return true;
}
