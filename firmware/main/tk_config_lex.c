#include "tk_config.h"
#include <string.h>

static bool utf8(const unsigned char **p,const unsigned char *end,uint32_t *code)
{
    if(*p>=end)return false;
    unsigned c=*(*p)++,n=0;uint32_t v=c,min=0;
    if(c<128){*code=c;return true;}
    if(c>=0xc2 && c<=0xdf){n=1;v=c&31;min=0x80;}
    else if(c>=0xe0 && c<=0xef){n=2;v=c&15;min=0x800;}
    else if(c>=0xf0 && c<=0xf4){n=3;v=c&7;min=0x10000;}else return false;
    for(unsigned i=0;i<n;i++){if(*p>=end || (**p&0xc0)!=0x80)return false;v=(v<<6)|(*(*p)++&63);}
    if(v<min || v>0x10ffff || (v>=0xd800 && v<=0xdfff))return false;
    *code=v;return true;
}
bool tk_config_string(const char *s,unsigned count,size_t capacity,bool empty,bool newline)
{
    if(!s || (!empty && !*s))return false;
    size_t n=strlen(s);if(n>=capacity)return false;
    const unsigned char *p=(const unsigned char *)s,*end=p+n;unsigned chars=0;uint32_t code;
    while(p<end){if(!utf8(&p,end,&code) || (code<32 && !(newline && code==10)) || code==127 || ++chars>count)return false;}
    return true;
}
static int hex(unsigned char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;}
const char *tk_config_lex(const char *json,size_t size)
{
    if(!json || !size || size>TK_CFG_MAX || memchr(json,0,size))return "size";
    if(size>=3 && !memcmp(json,"\xef\xbb\xbf",3))return "json";
    const unsigned char *p=(const unsigned char *)json,*end=p+size;uint32_t code;
    while(p<end)if(!utf8(&p,end,&code))return "utf8";
    unsigned depth=0;bool quoted=false;
    for(size_t i=0;i<size;i++){
        unsigned char c=(unsigned char)json[i];
        if(quoted){
            if(c=='"')quoted=false;
            else if(c=='\\'){
                if(++i>=size)return "json";
                if(json[i]=='u'){
                    if(i+4>=size)return "json";
                    unsigned value=0;for(int k=0;k<4;k++){int h=hex(json[++i]);if(h<0)return "json";value=value*16+(unsigned)h;}
                    if(!value)return "json";
                }else if(!strchr("\"\\/bfnrt",json[i]))return "json";
            }else if(c<32)return "json";
        }else{
            if(c=='"')quoted=true;
            else if(c=='{' || c=='['){if(++depth>8)return "depth";}
            else if(c=='}' || c==']'){if(!depth)return "json";depth--;}
            else if(c=='.' || c=='-' || c=='+' || c=='e' || c=='E')return "number";
            else if(c>='0' && c<='9'){size_t start=i;while(i+1<size && json[i+1]>='0' && json[i+1]<='9')i++;if(i>start && c=='0')return "number";}
        }
    }return quoted || depth?"json":NULL;
}
uint32_t tk_config_crc(const void *data,size_t size)
{
    const uint8_t *p=data;uint32_t c=0xffffffff;
    for(size_t i=0;i<size;i++){c^=p[i];for(int k=0;k<8;k++)c=(c>>1)^(0xedb88320u&(0u-(c&1u)));}return ~c;
}
