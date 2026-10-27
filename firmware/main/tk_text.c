#include "tk_text.h"
#include <string.h>
#ifdef TK_COMPACT_CJK
#include "tk_cjk_compact.h"
extern const lv_font_t tk_font_cjk;
#endif
static const lv_font_fmt_txt_glyph_dsc_t *descriptor(const lv_font_t *font,uint32_t id,lv_font_fmt_txt_glyph_dsc_t *temporary)
{
#ifdef TK_COMPACT_CJK
    if(font==&tk_font_cjk){tk_cjk_descriptor(id,temporary);return temporary;}
#else
    (void)temporary;
#endif
    const lv_font_fmt_txt_dsc_t *f=font->dsc;return &f->glyph_dsc[id];
}

// Adapted from nabo_dive_text.c. Reads lv_font_conv output directly (no LVGL glyph cache),
// so the game task can draw while LVGL refresh is paused.

static uint32_t next_utf8(const char** s) {
    const uint8_t* p = (const uint8_t*)*s;
    uint32_t c = *p++;
    if (c >= 0xF0 && p[0] && p[1] && p[2]) {
        c = ((c & 0x07) << 18) | ((p[0] & 0x3F) << 12) | ((p[1] & 0x3F) << 6) | (p[2] & 0x3F);
        p += 3;
    } else if (c >= 0xE0 && p[0] && p[1]) {
        c = ((c & 0x0F) << 12) | ((p[0] & 0x3F) << 6) | (p[1] & 0x3F);
        p += 2;
    } else if (c >= 0xC0 && p[0]) {
        c = ((c & 0x1F) << 6) | (p[0] & 0x3F);
        p += 1;
    }
    *s = (const char*)p;
    return c;
}

static int find_u16(const uint16_t* list, int n, uint32_t v) {
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (list[mid] == v)
            return mid;
        if (list[mid] < v)
            lo = mid + 1;
        else
            hi = mid - 1;
    }
    return -1;
}

static uint32_t glyph_id(const lv_font_fmt_txt_dsc_t* f, uint32_t letter) {
    for (uint16_t i = 0; i < f->cmap_num; ++i) {
        const lv_font_fmt_txt_cmap_t* m = &f->cmaps[i];
        if (letter < m->range_start)
            continue;
        uint32_t rcp = letter - m->range_start;
        if (rcp >= m->range_length)
            continue;
        switch (m->type) {
            case LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY:
                return m->glyph_id_start + rcp;
            case LV_FONT_FMT_TXT_CMAP_FORMAT0_FULL:
                return m->glyph_id_start + ((const uint8_t*)m->glyph_id_ofs_list)[rcp];
            case LV_FONT_FMT_TXT_CMAP_SPARSE_TINY: {
                int k = find_u16(m->unicode_list, m->list_length, rcp);
                if (k >= 0)
                    return m->glyph_id_start + k;
                break;
            }
            case LV_FONT_FMT_TXT_CMAP_SPARSE_FULL: {
                int k = find_u16(m->unicode_list, m->list_length, rcp);
                if (k >= 0)
                    return m->glyph_id_start + ((const uint16_t*)m->glyph_id_ofs_list)[k];
                break;
            }
            default:
                break;
        }
    }
    return 0;
}

static uint32_t locate(const lv_font_t *font,uint32_t code,const lv_font_t **actual) {
    const lv_font_t *next=font;uint32_t gid=0;
    for(int i=0;next && i<4;i++){*actual=next;gid=glyph_id(next->dsc,code);if(gid)return gid;next=next->fallback;}
    return *actual!=font?glyph_id((*actual)->dsc,0x25a1):0;
}
// Generated font user_data carries its nominal pixel size. A full CJK subset's
// bounding line_height includes exceptional glyphs and must not shrink normal Han text.
static int nominal(const lv_font_t *font) {
    uintptr_t size=(uintptr_t)font->user_data;
    return size>0 && size<=96?(int)size:font->line_height;
}
int nt_text_width(const lv_font_t* font, const char* s) {
    int w = 0;
    while (*s) {
        const lv_font_t *actual=font;uint32_t gid=locate(font,next_utf8(&s),&actual);
        lv_font_fmt_txt_glyph_dsc_t temporary;
        w += gid ? (int)((descriptor(actual,gid,&temporary)->adv_w+8)/16)*nominal(font)/nominal(actual) : font->line_height/3;
    }
    return w;
}

bool nt_text_layout(nt_glyph_pool_t* pool, nt_text_t* t, const lv_font_t* font, const char* s, int x, int y,
                    nt_align_t align) {
    int w = nt_text_width(font, s);
    if (align == NT_ALIGN_CENTER)
        x -= w / 2;
    else if (align == NT_ALIGN_RIGHT)
        x -= w;
    t->first = (uint16_t)pool->used;
    t->count = 0;
    t->w = (int16_t)w;
    t->x0 = (int16_t)x;
    t->x1 = (int16_t)(x + w);
    t->y0 = (int16_t)(y - font->line_height + font->base_line);
    t->y1 = (int16_t)(y + font->base_line);
    int pen = x;
    while (*s) {
        const lv_font_t *actual=font;uint32_t gid=locate(font,next_utf8(&s),&actual);
        const lv_font_fmt_txt_dsc_t *f=actual->dsc;int scale=nominal(font),denominator=nominal(actual);
        if (!gid) {
            pen += font->line_height / 3;
            continue;
        }
        lv_font_fmt_txt_glyph_dsc_t temporary;
        const lv_font_fmt_txt_glyph_dsc_t* g = descriptor(actual,gid,&temporary);
        if (g->box_w && g->box_h) {
            if (pool->used >= NT_GLYPH_POOL)
                return false;
            nt_glyph_t* out = &pool->g[pool->used++];
            t->count++;
            out->bitmap = &f->glyph_bitmap[g->bitmap_index];
            out->x = (int16_t)(pen + g->ofs_x*scale/denominator);
            out->w = (g->box_w*scale+denominator-1)/denominator;
            out->source_w = g->box_w;
            out->source_h=g->box_h;out->bpp=f->bpp;
            out->h=(g->box_h*scale+denominator-1)/denominator;
            out->y=(int16_t)(y-out->h-g->ofs_y*scale/denominator);
            if (out->x < t->x0) t->x0 = out->x;
            if (out->x + out->w > t->x1) t->x1 = (int16_t)(out->x + out->w);
            if (out->y < t->y0) t->y0 = out->y;
            if (out->y + out->h > t->y1) t->y1 = (int16_t)(out->y + out->h);
        }
        pen += (g->adv_w+8)/16*scale/denominator;
    }
    return true;
}

uint16_t nt_blend565(uint16_t dst, uint16_t src, int a) {
    int r = (((src >> 11) - (dst >> 11)) * a >> 8) + (dst >> 11);
    int g = ((((src >> 5) & 63) - ((dst >> 5) & 63)) * a >> 8) + ((dst >> 5) & 63);
    int b = (((src & 31) - (dst & 31)) * a >> 8) + (dst & 31);
    return (uint16_t)((r << 11) | (g << 5) | b);
}

void nt_text_row(const nt_glyph_pool_t* pool, const nt_text_t* t, int y, int x0, int x1, uint16_t* row,
                 uint16_t color) {
    if (y < t->y0 || y >= t->y1 || x1 <= t->x0 || x0 >= t->x1)
        return;
    for (int i = t->first; i < t->first + t->count; ++i) {
        const nt_glyph_t* g = &pool->g[i];
        int gy = y - g->y;
        if (gy < 0 || gy >= g->h)
            continue;
        int a = g->x > x0 ? g->x : x0, b = g->x + g->w < x1 ? g->x + g->w : x1;
        for (int x = a; x < b; ++x) {
            int source_x=(x-g->x)*g->source_w/g->w;
            int source_y=gy*g->source_h/g->h;
            unsigned bit=(unsigned)(source_y*g->source_w+source_x)*g->bpp;
            int maximum=(1<<g->bpp)-1;
            int v=(g->bitmap[bit>>3]>>(8-g->bpp-(bit&7)))&maximum;
            if (v)
                row[x - x0] = nt_blend565(row[x - x0], color, v * 256 / maximum);
        }
    }
}
