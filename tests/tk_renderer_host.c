#include "tk_ui.h"
#include "tk_fonts.h"
#include <stdlib.h>
#include <string.h>

// The production direct renderer reads font descriptors itself; LVGL callbacks
// are linker placeholders here and are never used for layout or pixels.
const void *lv_font_get_bitmap_fmt_txt(lv_font_glyph_dsc_t *d,lv_draw_buf_t *b){(void)d;(void)b;return NULL;}
bool lv_font_get_glyph_dsc_fmt_txt(const lv_font_t *f,lv_font_glyph_dsc_t *d,uint32_t c,uint32_t n){(void)f;(void)d;(void)c;(void)n;return false;}
typedef struct {ag_t gfx;tk_ui_t ui;tk_ui_assets_t assets;uint16_t strip[2][240*AG_STRIP],pixels[240*320];
#ifdef TK_F3
    tk_animation_t animation;
#endif
} host_t;
static void send(void *context,int x,int y,int w,int h,uint16_t *pixels)
{
    host_t *host=context;
    for(int j=0;j<h;j++)for(int i=0;i<w;i++){uint16_t c=pixels[j*w+i];host->pixels[(y+j)*240+x+i]=(uint16_t)(c<<8|c>>8);}
}
void *tk_render_new(const tk_ui_assets_t *assets)
{
    host_t *host=calloc(1,sizeof(*host));if(!host)return NULL;
    if(assets)host->assets=*assets;
#ifdef TK_F3
    tk_animation_init(&host->animation);host->assets.animation=&host->animation;
#endif
    ag_init(&host->gfx,host->strip[0],host->strip[1],send,host);return host;
}
void tk_render_free(void *host){free(host);}
bool tk_render_frame(void *context,const tk_state_t *s,int64_t now,bool full,int comparison)
{
    host_t *host=context;if(full)ag_invalidate(&host->gfx);
    tk_ui_frame(&host->ui,&host->gfx,s,now,&host->assets,comparison);ag_flush(&host->gfx);return !host->gfx.overflow;
}
const uint16_t *tk_render_pixels(void *context){return ((host_t *)context)->pixels;}
unsigned tk_render_bytes(void *context){return ((host_t *)context)->gfx.bytes;}
int tk_render_wordmark_width(void){return ag_text_width(&tk_font_28,"NABO");}
int tk_render_ops(void *context){return ((host_t *)context)->gfx.n;}
int tk_render_glyphs(void *context){return ((host_t *)context)->gfx.glyphs.used;}
int tk_render_fallback_glyphs(void *context){host_t *h=context;int n=0;for(int i=0;i<h->gfx.glyphs.used;i++)if(h->gfx.glyphs.g[i].bpp==1)n++;return n;}
int tk_render_fallback_height(void *context){host_t *h=context;int n=0;for(int i=0;i<h->gfx.glyphs.used;i++)if(h->gfx.glyphs.g[i].bpp==1 && h->gfx.glyphs.g[i].h>n)n=h->gfx.glyphs.g[i].h;return n;}
int tk_render_scaled_glyphs(void *context)
{
    host_t *host=context;int count=0;
    for(int i=0;i<host->gfx.glyphs.used;i++)if(host->gfx.glyphs.g[i].w<host->gfx.glyphs.g[i].source_w)count++;
    return count;
}
