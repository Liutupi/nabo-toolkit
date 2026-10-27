#include "tk_config_serial.h"
#include "nvs.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void reply(tk_config_serial_t *s,const char *line){if(s->reply)s->reply(s->context,line);}
static void abort_rx(tk_config_serial_t *s){memset(s->incoming,0,sizeof(s->incoming));s->receiving=false;s->received=s->expected=0;}
static void error(tk_config_serial_t *s,const char *code){char line[80];abort_rx(s);snprintf(line,sizeof(line),"tk.cfg.err %s",code);reply(s,line);}
static bool decimal(const char *p,size_t *n)
{
    if(!*p)return false;
    *n=0;for(;*p;p++){if(*p<'0'||*p>'9' || *n>TK_CFG_MAX)return false;*n=*n*10+(unsigned)(*p-'0');}return *n>0 && *n<=TK_CFG_MAX;
}
static int value(char c){static const char table[]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";const char *at=strchr(table,c);return at && c?(int)(at-table):-1;}
static int decode(const char *p,uint8_t out[48])
{
    size_t size=strlen(p);if(!size || size>64 || size%4)return -1;
    int used=0;
    for(size_t i=0;i<size;i+=4){
        int a=value(p[i]),b=value(p[i+1]),c=p[i+2]=='='?0:value(p[i+2]),d=p[i+3]=='='?0:value(p[i+3]);
        bool two=p[i+2]=='=',one=p[i+3]=='=';
        if(a<0 || b<0 || c<0 || d<0 || (two && !one) || ((two||one) && i+4!=size) || (two && (b&15)) || (!two && one && (c&3)))return -1;
        out[used++]=(uint8_t)((a<<2)|(b>>4));if(!two)out[used++]=(uint8_t)((b<<4)|(c>>2));if(!one)out[used++]=(uint8_t)((c<<6)|d);
    }return used;
}
static void encode(const uint8_t *p,size_t size,char *out)
{
    static const char table[]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";unsigned n=0;
    for(size_t i=0;i<size;i+=3){uint32_t v=(uint32_t)p[i]<<16;if(i+1<size)v|=(uint32_t)p[i+1]<<8;if(i+2<size)v|=p[i+2];
        out[n++]=table[v>>18];out[n++]=table[(v>>12)&63];out[n++]=i+1<size?table[(v>>6)&63]:'=';out[n++]=i+2<size?table[v&63]:'=';}
    out[n]=0;
}
static bool checksum(const char *p,uint32_t *out)
{
    if(strlen(p)!=8)return false;
    *out=0;
    for(int i=0;i<8;i++){unsigned char c=p[i];int n=c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;if(n<0)return false;*out=(*out<<4)|(unsigned)n;}return true;
}
esp_err_t tk_config_serial_init(tk_config_serial_t *s,tk_state_t *model,tk_config_reply_t sink,void *context)
{
    memset(s,0,sizeof(*s));s->model=model;s->reply=sink;s->context=context;tk_config_defaults(&s->current);
    s->size=tk_config_json(&s->current,s->json,sizeof(s->json));if(!s->size)return ESP_ERR_INVALID_SIZE;
    esp_err_t e=tk_config_store_load(&s->current,s->json,&s->size);tk_model_apply_config(model,&s->current);
    return e==ESP_ERR_NVS_NOT_FOUND?ESP_OK:e;
}
static void commit(tk_config_serial_t *s,const char *argument)
{
    uint32_t expected;
    if(!s->receiving){error(s,"state");return;}
    if(s->received!=s->expected || !checksum(argument,&expected) || expected!=tk_config_crc(s->incoming,s->received)){error(s,"crc");return;}
    tk_custom_t *next=malloc(sizeof(*next));char *json=malloc(TK_CFG_MAX+1);
    if(!next || !json){free(next);free(json);error(s,"memory");return;}
    const char *code=tk_config_parse(next,s->incoming,s->received);size_t size=0;
    if(!code && !(size=tk_config_json(next,json,TK_CFG_MAX+1)))code="size";
    if(!code && tk_config_store_save(json,size)!=ESP_OK)code="storage";
    if(!code){
        s->current=*next;memcpy(s->json,json,size+1);s->size=size;tk_model_apply_config(s->model,&s->current);abort_rx(s);
        char line[80];snprintf(line,sizeof(line),"tk.cfg.ok %u %08lx",(unsigned)size,(unsigned long)tk_config_crc(json,size));reply(s,line);
    }else error(s,code);
    memset(next,0,sizeof(*next));memset(json,0,TK_CFG_MAX+1);free(next);free(json);
}
bool tk_config_serial_line(tk_config_serial_t *s,const char *line,int64_t now,bool writable)
{
    if(strncmp(line,">tk.cfg.",8))return false;
    if(!strcmp(line,">tk.cfg.abort")){abort_rx(s);s->reading=false;reply(s,"tk.cfg.aborted");return true;}
    if(s->receiving && (now-s->last_data>=10000 || now-s->started>=60000)){error(s,"timeout");return true;}
    if(!strcmp(line,">tk.cfg.invalid")){error(s,"line");return true;}
    if(!strcmp(line,">tk.cfg.read")){
        if(s->receiving || s->reading){error(s,"busy");return true;}
        s->reading=true;s->read_offset=0;char response[64];snprintf(response,sizeof(response),"tk.cfg.begin %u",(unsigned)s->size);reply(s,response);return true;
    }
    if(!writable){error(s,"test");return true;}
    if(s->reading){error(s,"busy");return true;}
    if(!strncmp(line,">tk.cfg.begin ",14)){
        if(s->receiving){error(s,"busy");return true;}
        size_t size;if(!decimal(line+14,&size)){error(s,"size");return true;}
        s->expected=size;s->received=0;s->receiving=true;s->started=s->last_data=now;
        char response[64];snprintf(response,sizeof(response),"tk.cfg.ready %u",(unsigned)size);reply(s,response);
    }else if(!strncmp(line,">tk.cfg.data ",13)){
        if(!s->receiving){error(s,"state");return true;}
        uint8_t bytes[48];int n=decode(line+13,bytes);
        if(n<0 || s->received+(unsigned)n>s->expected){error(s,"data");return true;}
        memcpy(s->incoming+s->received,bytes,(unsigned)n);s->received+=(unsigned)n;s->last_data=now;
        char response[64];snprintf(response,sizeof(response),"tk.cfg.more %u",(unsigned)s->received);reply(s,response);
    }else if(!strncmp(line,">tk.cfg.end ",12))commit(s,line+12);
    else error(s,"command");
    return true;
}
void tk_config_serial_tick(tk_config_serial_t *s,int64_t now,bool writable)
{
    if(s->receiving && (!writable || now-s->last_data>=10000 || now-s->started>=60000)){error(s,writable?"timeout":"test");return;}
    if(!s->reading)return;
    char line[96];
    if(s->read_offset==s->size){snprintf(line,sizeof(line),"tk.cfg.end %08lx",(unsigned long)tk_config_crc(s->json,s->size));s->reading=false;}
    else{char b64[65];size_t n=s->size-s->read_offset;if(n>48)n=48;encode((const uint8_t *)s->json+s->read_offset,n,b64);s->read_offset+=n;snprintf(line,sizeof(line),"tk.cfg.data %s",b64);}
    reply(s,line);
}
bool tk_config_serial_busy(const tk_config_serial_t *s){return s->receiving || s->reading;}
