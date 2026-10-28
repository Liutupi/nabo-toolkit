#include "tk_voice_store.h"
#include "nvs.h"
#include <string.h>

static uint32_t crc(const uint8_t *p,unsigned n)
{
    uint32_t c=0xffffffff;for(unsigned i=0;i<n;i++){c^=p[i];for(int b=0;b<8;b++)c=(c>>1)^(0xedb88320u&(0u-(c&1)));}return ~c;
}
static uint32_t u32(const uint8_t *p){uint32_t n=0;for(unsigned i=0;i<4;i++)n|=(uint32_t)p[i]<<(8*i);return n;}
static void put32(uint8_t *p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static bool count_valid(unsigned n){return !n || (n>=VP_MIN_SPEECH_FRAMES && n<=VP_MAX_TEMPLATE_FRAMES);}
static void key(unsigned word,int slot,char name[7])
{
    if(slot<0){memcpy(name,"voice0",7);name[5]=(char)('0'+word);}
    else {memcpy(name,"vc0a",5);name[2]=(char)('0'+word);name[3]=(char)('a'+slot);}
}
static unsigned width(const uint8_t *p,unsigned d){return (p[36+d/2]>>(4*(d%2)))&15;}
static int value(const uint8_t *p,unsigned e,unsigned f,unsigned d,unsigned *bit)
{
    if(p[4]==1)return (int8_t)p[20+(e*VP_MAX_TEMPLATE_FRAMES+f)*VP_FEATURE_DIM+d];
    unsigned n=0;for(unsigned b=0;b<width(p,d);b++,(*bit)++)n|=((p[42+*bit/8]>>(*bit%8))&1u)<<b;
    return (int8_t)p[24+d]+(int)n;
}
static bool valid(const uint8_t *p,unsigned word,unsigned size)
{
    const uint8_t head[]={'T','K','V','1',0,1,(uint8_t)word,0,3,12,48,16,0x80,0x3e,0x40,0x01};
    if(size<24 || memcmp(p,head,4) || p[5]!=1 || p[6]!=word ||
       (p[7]!=VP_MAX_WORDS && !(p[7]==6 && word<6)) || memcmp(p+8,head+8,8) || p[16]>=3 ||
       u32(p+size-4)!=crc(p,size-4))return false;
    unsigned frames=0,bits=0;
    for(unsigned e=0;e<3;e++){if(!count_valid(p[17+e]))return false;frames+=p[17+e];}
    if(p[4]==1){if(size!=TK_VOICE_RECORD_BYTES)return false;}
    else if(p[4]==2){
        if(size<46 || !u32(p+20))return false;
        for(unsigned d=0;d<12;d++){unsigned n=width(p,d);if(n>8 || p[24+d]==0x80)return false;bits+=n;}
        bits*=frames;if(size!=46+(bits+7)/8)return false;
        if(bits%8 && (p[size-5]>>(bits%8)))return false;
    }else return false;
    unsigned bit=0;
    for(unsigned e=0;e<3;e++)for(unsigned f=0;f<48;f++)for(unsigned d=0;d<12;d++){
        if(f<p[17+e]){int n=value(p,e,f,d,&bit);if(n< -127 || n>127)return false;}
        else if(p[4]==1 && p[20+(e*48+f)*12+d])return false;
    }
    return true;
}
static esp_err_t read_record(unsigned word,int slot,uint8_t *p,unsigned *length)
{
    nvs_handle_t h;esp_err_t error=nvs_open("nabo_tk",NVS_READONLY,&h);if(error)return error;
    char name[7];key(word,slot,name);size_t size=TK_VOICE_RECORD_MAX;
    error=nvs_get_blob(h,name,p,&size);nvs_close(h);
    if(error==ESP_ERR_NVS_INVALID_LENGTH)error=ESP_ERR_INVALID_SIZE;
    if(error)return error;
    if(size>TK_VOICE_RECORD_MAX || !valid(p,word,(unsigned)size) || (slot>=0 && p[4]!=2))return ESP_ERR_INVALID_CRC;
    *length=(unsigned)size;return ESP_OK;
}
bool tk_voice_store_bad_record(esp_err_t error){return error==ESP_ERR_INVALID_CRC || error==ESP_ERR_INVALID_SIZE;}
// Read both journals before applying any caller output. A failed new slot can
// never cause a previously confirmed slot or legacy key to be overwritten.
static esp_err_t choose(unsigned word,uint8_t *p,uint8_t **selected,unsigned *size,int *slot)
{
    uint8_t *a=p,*b=p+TK_VOICE_RECORD_MAX;unsigned na=0,nb=0;
    esp_err_t ea=read_record(word,0,a,&na),eb=read_record(word,1,b,&nb);
    if(!ea || !eb){
        bool take_b=ea || (!eb && (int32_t)(u32(b+20)-u32(a+20))>0);
        *selected=take_b?b:a;*size=take_b?nb:na;*slot=take_b?1:0;return ESP_OK;
    }
    if(ea!=ESP_ERR_NVS_NOT_FOUND && !tk_voice_store_bad_record(ea))return ea;
    if(eb!=ESP_ERR_NVS_NOT_FOUND && !tk_voice_store_bad_record(eb))return eb;
    *selected=a;*slot=-1;esp_err_t legacy=read_record(word,-1,a,size);
    return legacy==ESP_ERR_NVS_NOT_FOUND && (tk_voice_store_bad_record(ea) || tk_voice_store_bad_record(eb))?ESP_ERR_INVALID_CRC:legacy;
}
static bool same(const uint8_t *p,const vp_template_t current[3],unsigned next,const uint8_t *legacy)
{
    if(p[16]!=next)return false;
    unsigned bit=0;
    for(unsigned e=0;e<3;e++){
        unsigned count=legacy?legacy[17+e]:current[e].count;
        if(p[17+e]!=count)return false;
        const vp_frame_t *frames=legacy?(const vp_frame_t *)(legacy+20+e*48*12):current[e].frame;
        for(unsigned f=0;f<count;f++)for(unsigned d=0;d<12;d++)
            if(value(p,e,f,d,&bit)!=frames[f].value[d])return false;
    }
    return true;
}
esp_err_t tk_voice_store_load(unsigned word,vp_template_t out[3],uint8_t *next,uint8_t p[TK_VOICE_STORE_SCRATCH_BYTES])
{
    if(word>=VP_MAX_WORDS || !out || !next || !p)return ESP_ERR_INVALID_ARG;
    uint8_t *selected;unsigned size;int slot;esp_err_t error=choose(word,p,&selected,&size,&slot);if(error)return error;
    memset(out,0,sizeof(vp_template_t)*3);unsigned bit=0;
    for(unsigned e=0;e<3;e++){
        out[e].count=selected[17+e];
        for(unsigned f=0;f<out[e].count;f++)for(unsigned d=0;d<12;d++)out[e].frame[f].value[d]=(int8_t)value(selected,e,f,d,&bit);
    }
    *next=selected[16];return ESP_OK;
}
esp_err_t tk_voice_store_scan(uint8_t counts[VP_MAX_WORDS],uint8_t *invalid_mask,vp_template_t word[3],uint8_t scratch[TK_VOICE_STORE_SCRATCH_BYTES])
{
    if(!counts || !invalid_mask || !word || !scratch)return ESP_ERR_INVALID_ARG;
    memset(counts,0,VP_MAX_WORDS);*invalid_mask=0;
    for(unsigned i=0;i<VP_MAX_WORDS;i++){
        uint8_t next;esp_err_t error=tk_voice_store_load(i,word,&next,scratch);
        if(error==ESP_ERR_NVS_NOT_FOUND)continue;
        if(tk_voice_store_bad_record(error)){*invalid_mask|=(uint8_t)(1u<<i);continue;}
        if(error)return error;
        for(unsigned e=0;e<3;e++)if(word[e].count)counts[i]++;
    }
    return ESP_OK;
}
static unsigned encode(unsigned word,const vp_template_t current[3],unsigned example,const vp_frame_t *frames,unsigned count,unsigned next,uint32_t generation,const uint8_t *legacy,uint8_t *p)
{
    const uint8_t head[]={'T','K','V','1',2,1,(uint8_t)word,VP_MAX_WORDS,3,12,48,16,0x80,0x3e,0x40,0x01};
    memset(p,0,TK_VOICE_RECORD_MAX);memcpy(p,head,16);p[16]=(uint8_t)next;put32(p+20,generation);
    int lo[12],hi[12];for(unsigned d=0;d<12;d++){lo[d]=127;hi[d]=-127;}
    for(unsigned e=0;e<3;e++){
        unsigned n=legacy?legacy[17+e]:e==example?count:current[e].count;if(!count_valid(n))return 0;p[17+e]=(uint8_t)n;
        const vp_frame_t *v=legacy?(const vp_frame_t *)(legacy+20+e*48*12):e==example?frames:current[e].frame;
        for(unsigned f=0;f<n;f++)for(unsigned d=0;d<12;d++){
            int x=v[f].value[d];if(x== -128)return 0;if(x<lo[d])lo[d]=x;if(x>hi[d])hi[d]=x;
        }
    }
    for(unsigned d=0;d<12;d++){
        unsigned n=0;while(hi[d]>=lo[d] && (1u<<n)<=(unsigned)(hi[d]-lo[d]))n++;
        p[24+d]=(uint8_t)lo[d];p[36+d/2]|=(uint8_t)(n<<(4*(d%2)));
    }
    unsigned bit=0;
    for(unsigned e=0;e<3;e++){
        const vp_frame_t *v=legacy?(const vp_frame_t *)(legacy+20+e*48*12):e==example?frames:current[e].frame;
        for(unsigned f=0;f<p[17+e];f++)for(unsigned d=0;d<12;d++){
            unsigned n=(unsigned)(v[f].value[d]-lo[d]);
            for(unsigned b=0;b<width(p,d);b++,bit++)p[42+bit/8]|=(uint8_t)(((n>>b)&1u)<<(bit%8));
        }
    }
    unsigned size=46+(bit+7)/8;put32(p+size-4,crc(p,size-4));return size;
}
static esp_err_t erase(nvs_handle_t h,unsigned word,int slot)
{
    char name[7];key(word,slot,name);esp_err_t error=nvs_erase_key(h,name);return error==ESP_ERR_NVS_NOT_FOUND?ESP_OK:error;
}
static esp_err_t retire(unsigned word,int active,bool legacy)
{
    nvs_handle_t h;esp_err_t error=nvs_open("nabo_tk",NVS_READWRITE,&h);
    if(!error){if(active>=0)error=erase(h,word,active);if(!error && legacy)error=erase(h,word,-1);nvs_close(h);}
    return error;
}
static esp_err_t write_new(unsigned word,int active,uint8_t *p,unsigned size,tk_voice_store_result_t *detail)
{
    int target=active==0?1:0;nvs_handle_t h;detail->write_error=nvs_open("nabo_tk",NVS_READWRITE,&h);
    if(!detail->write_error){
        // Never replace a confirmed key: SDK6.0.2 failed update cleanup can
        // remove the old version. The target is an independent inactive key.
        detail->write_error=erase(h,word,target);
        nvs_stats_t stats;if(!detail->write_error)detail->write_error=nvs_get_stats(NULL,&stats);
        if(!detail->write_error && stats.available_entries<(size+31)/32+6)detail->write_error=ESP_ERR_NVS_NOT_ENOUGH_SPACE;
        char name[7];key(word,target,name);
        if(!detail->write_error)detail->write_error=nvs_set_blob(h,name,p,size);
        if(!detail->write_error)detail->write_error=nvs_commit(h);
        nvs_close(h);
    }
    unsigned actual_size=0;detail->read_error=read_record(word,target,p+TK_VOICE_RECORD_MAX,&actual_size);
    detail->confirmed=!detail->read_error && actual_size==size && !memcmp(p,p+TK_VOICE_RECORD_MAX,size);
    return detail->confirmed?ESP_OK:detail->write_error?detail->write_error:detail->read_error?detail->read_error:ESP_ERR_INVALID_STATE;
}
esp_err_t tk_voice_store_save(unsigned word,const vp_template_t current[3],unsigned example,const vp_frame_t *frames,unsigned count,uint8_t p[TK_VOICE_STORE_SCRATCH_BYTES],tk_voice_store_result_t *result)
{
    tk_voice_store_result_t detail={0};if(result)*result=detail;
    if(word>=VP_MAX_WORDS || example>=3 || !current || !frames || !p || count<VP_MIN_SPEECH_FRAMES || count>48)return ESP_ERR_INVALID_ARG;
    uint8_t *old;unsigned old_size=0;int active=-1;esp_err_t previous=choose(word,p,&old,&old_size,&active);
    bool empty=true;for(unsigned e=0;e<3;e++)if(current[e].count)empty=false;
    if(previous && previous!=ESP_ERR_NVS_NOT_FOUND && !tk_voice_store_bad_record(previous)){
        detail.read_error=previous;detail.unknown=true;if(result)*result=detail;return previous;
    }
    if((previous && !empty) || (!previous && !same(old,current,example,NULL))){
        detail.unknown=true;if(result)*result=detail;return ESP_ERR_INVALID_STATE;
    }
    uint32_t generation=!previous && active>=0?u32(old+20)+1:1;if(!generation)generation=1;
    unsigned size=encode(word,current,example,frames,count,(example+1)%3,generation,NULL,p);if(!size)return ESP_ERR_INVALID_ARG;
    esp_err_t error=write_new(word,active,p,size,&detail);uint8_t *actual=p+TK_VOICE_RECORD_MAX;
    if(detail.confirmed){
        // Keep the new verified journal even if retiring the old copy fails.
        esp_err_t retired=retire(word,active,true);
        if(!detail.write_error)detail.write_error=retired;
        if(result)*result=detail;
        return ESP_OK;
    }
    bool absent=detail.read_error==ESP_ERR_NVS_NOT_FOUND || tk_voice_store_bad_record(detail.read_error);
    unsigned n=0;esp_err_t old_error=previous?previous:read_record(word,active,actual,&n);
    detail.unknown=!absent || (!previous && (old_error || !same(actual,current,example,NULL))) || (previous && !empty);
    if(result)*result=detail;
    return error;
}
esp_err_t tk_voice_store_compact_legacy(unsigned word,uint8_t p[TK_VOICE_STORE_SCRATCH_BYTES])
{
    if(word>=VP_MAX_WORDS || !p)return ESP_ERR_INVALID_ARG;
    uint8_t *old;unsigned size=0;int active=-1;esp_err_t error=choose(word,p,&old,&size,&active);
    if(error || active>=0)return error; // Already compact: no writes or retirement.
    if(old[4]!=1)return ESP_ERR_INVALID_CRC;
    uint32_t original_crc=u32(old+size-4);unsigned next=old[16];
    uint8_t *actual=p+TK_VOICE_RECORD_MAX;memmove(actual,old,size);
    size=encode(word,NULL,3,NULL,0,next,1,actual,p);if(!size)return ESP_ERR_INVALID_ARG;
    tk_voice_store_result_t detail={0};error=write_new(word,-1,p,size,&detail);if(error)return error;
    // Independently reread legacy and decode every new feature before deleting
    // the original. Reuse the expected buffer; no heap, stack bank or raw audio.
    error=read_record(word,-1,p,&size);if(error)return error;
    if(u32(p+size-4)!=original_crc || !same(actual,NULL,next,p)){
        (void)retire(word,0,false);return ESP_ERR_INVALID_STATE; // Keep proven legacy, discard untrusted candidate only.
    }
    return retire(word,-1,true);
}
