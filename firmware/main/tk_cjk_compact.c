#include "tk_cjk_compact.h"
#include <string.h>
static unsigned lookup(const lv_font_fmt_txt_dsc_t *f,uint32_t code)
{
    for(unsigned i=0;i<f->cmap_num;i++){
        const lv_font_fmt_txt_cmap_t *m=&f->cmaps[i];
        if(code<m->range_start || code-m->range_start>=m->range_length)continue;
        unsigned n=code-m->range_start;
        if(m->type==LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY)return m->glyph_id_start+n;
        if(m->type==LV_FONT_FMT_TXT_CMAP_FORMAT0_FULL)return m->glyph_id_start+((const uint8_t *)m->glyph_id_ofs_list)[n];
        for(unsigned j=0;j<m->list_length;j++)if(m->unicode_list[j]==n)return m->glyph_id_start+(m->type==LV_FONT_FMT_TXT_CMAP_SPARSE_TINY?j:((const uint16_t *)m->glyph_id_ofs_list)[j]);
    }return 0;
}
bool tk_cjk_get_glyph_dsc(const lv_font_t *font,lv_font_glyph_dsc_t *out,uint32_t code,uint32_t next)
{
    (void)next;unsigned id=lookup(font->dsc,code);lv_font_fmt_txt_glyph_dsc_t d;
    if(!id || !tk_cjk_descriptor(id,&d))return false;
    memset(out,0,sizeof(*out));out->resolved_font=font;out->adv_w=(d.adv_w+8)/16;out->box_w=d.box_w;out->box_h=d.box_h;
    out->ofs_x=d.ofs_x;out->ofs_y=d.ofs_y;out->format=LV_FONT_GLYPH_FORMAT_A1;out->gid.index=id;return true;
}
const void *tk_cjk_get_bitmap(lv_font_glyph_dsc_t *dsc,lv_draw_buf_t *buffer)
{
    (void)buffer;lv_font_fmt_txt_glyph_dsc_t d;
    if(!tk_cjk_descriptor(dsc->gid.index,&d))return NULL;
    const lv_font_fmt_txt_dsc_t *f=dsc->resolved_font->dsc;return f->glyph_bitmap+d.bitmap_index;
}
