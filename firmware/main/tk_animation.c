#include "tk_animation.h"
#include <string.h>
static unsigned u16(const uint8_t *p){return p[0]|(unsigned)p[1]<<8;}
static uint32_t u32(const uint8_t *p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint32_t crc32(const uint8_t *p,unsigned size)
{
    uint32_t c=~0u;
    while(size--){c^=*p++;for(int k=0;k<8;k++)c=(c>>1)^(0xedb88320u&(0u-(c&1u)));}return ~c;
}
void tk_animation_init(tk_animation_t *a){memset(a,0,sizeof(*a));a->id=a->frame=-1;}
static bool select_clip(tk_animation_t *a,const tk_animation_bank_t *bank,unsigned id)
{
    if(!bank || !bank->data || bank->bytes<80 || id>=TK_AN_COUNT)return false;
    const uint8_t *b=bank->data;
    if(memcmp(b,"TKAB1\0\0\0",8) || u32(b+8)!=TK_AN_COUNT || u32(b+12)!=bank->bytes)return false;
    uint32_t expected=80,start=0,length=0;
    for(unsigned i=0;i<TK_AN_COUNT;i++){
        uint32_t offset=u32(b+16+i*8),size=u32(b+20+i*8);
        if(offset!=expected || size>bank->bytes-offset || offset>bank->bytes)return false;
        if(i==id){start=offset;length=size;}expected=offset+size;
    }
    if(expected!=bank->bytes || length<172)return false;
    const uint8_t *p=b+start;
    unsigned w=u16(p+8),h=u16(p+10),count=u16(p+12),duration=u32(p+16),loop=u32(p+20);
    if(memcmp(p,"TKANI1\0\0",8) || !w || !h || w>115 || h>150 || w*h>TK_ANIMATION_PIXELS || !count || count>64 || u16(p+14)!=64 || !duration || loop>1 || 152+count*20>length)return false;
    expected=152+count*20;uint32_t previous=0;
    for(unsigned i=0;i<count;i++){
        const uint8_t *e=p+152+i*20;uint32_t at=u32(e),off=u32(e+4),size=u32(e+8),key=u32(e+16);
        if((!i && (at || key!=1)) || (i && at<=previous) || at>=duration || key>1 || off!=expected || off>length || size>length-off)return false;
        expected=off+size;previous=at;
    }
    if(expected!=length)return false;
    a->clip=p;a->palette=p+24;a->clip_bytes=length;a->width=w;a->height=h;a->count=count;a->duration=duration;a->loop=loop;a->id=(int)id;a->frame=-1;
    return true;
}
static bool pixel(tk_animation_t *a,unsigned *out,unsigned size,unsigned value,bool key)
{
    if(*out>=size || value>63)return false;
    a->history[*out&4095]=value;
    if(key)a->pixels[*out]=value;else a->pixels[*out]^=value;
    ++*out;return true;
}
static bool decode_frame(tk_animation_t *a,unsigned frame)
{
    const uint8_t *e=a->clip+152+frame*20,*p=a->clip+u32(e+4),*end=p+u32(e+8);
    unsigned out=0,size=a->width*a->height;bool key=u32(e+16)==1;
    while(p<end){
        unsigned token=*p++;
        if(token<128){
            unsigned n=token+1,bits=0,used=0;
            for(unsigned i=0;i<n;i++){
                if(used<6){if(p>=end)return false;bits|=(unsigned)*p++<<used;used+=8;}
                if(!pixel(a,&out,size,bits&63,key))return false;
                bits>>=6;used-=6;
            }
            if(bits)return false;
        }else{
            unsigned n=((token>>4)&7)+3;if(p>=end)return false;
            unsigned distance=((token&15)<<8|*p++)+1;
            if(n==10){if(p>=end)return false;n+=*p++;}
            if(distance>out || n>size-out)return false;
            for(unsigned i=0;i<n;i++)if(!pixel(a,&out,size,a->history[(out-distance)&4095],key))return false;
        }
    }
    a->crc=crc32(a->pixels,size);return out==size && a->crc==u32(e+12);
}
bool tk_animation_frame(tk_animation_t *a,const tk_animation_bank_t *bank,unsigned id,uint64_t elapsed)
{
    if(!a)return false;
    if(a->id!=(int)id || !a->valid){if(!select_clip(a,bank,id)){a->valid=false;return false;}}
    unsigned time=a->loop?(unsigned)(elapsed%a->duration):(elapsed>=a->duration?a->duration-1:(unsigned)elapsed),target=0;
    while(target+1<a->count && time>=u32(a->clip+152+(target+1)*20))target++;
    if(a->frame>(int)target)a->frame=-1;
    // Seek from the nearest key frame; replay the exact original delta sequence.
    int first=a->frame+1;
    for(int i=(int)target;i>first;i--)if(u32(a->clip+152+i*20+16)){first=i;break;}
    for(int i=first;i<=(int)target;i++){
        if(!decode_frame(a,(unsigned)i)){a->valid=false;a->frame=-1;return false;}a->frame=i;
    }
    a->valid=true;return true;
}
