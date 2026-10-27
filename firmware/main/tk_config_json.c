#include "tk_config.h"
#include <stdio.h>
#include <string.h>
typedef struct {char *out;size_t used,capacity;bool failed;} writer_t;
static void put(writer_t *w,const char *s)
{
    size_t size=strlen(s);if(w->used+size>=w->capacity){w->failed=true;return;}
    memcpy(w->out+w->used,s,size);w->used+=size;w->out[w->used]=0;
}
static void integer(writer_t *w,unsigned n){char s[16];snprintf(s,sizeof(s),"%u",n);put(w,s);}
static void string(writer_t *w,const char *s)
{
    put(w,"\"");for(const unsigned char *p=(const unsigned char *)s;*p;p++){
        char next[8]={(char)*p,0};if(*p=='"' || *p=='\\'){next[0]='\\';next[1]=(char)*p;next[2]=0;}
        else if(*p=='\n'){next[0]='\\';next[1]='n';next[2]=0;}
        else if(*p<32)snprintf(next,sizeof(next),"\\u%04x",*p);
        put(w,next);
    }put(w,"\"");
}
static void slot(writer_t *w,const tk_cfg_slot_t *s)
{
    put(w,"{\"label\":");string(w,s->label);
    if(s->kind==TK_PACKET_MEDIA){put(w,",\"media\":");integer(w,s->media);}
    else if(s->kind==TK_PACKET_TEXT){put(w,",\"text\":");string(w,s->text);}
    else for(unsigned i=0;i<2;i++){
        put(w,i?",\"win\":":",\"mac\":");
        if(!(s->mask&(1u<<i)))put(w,"null");
        else{put(w,"{\"mod\":");integer(w,s->mod[i]);put(w,",\"key\":");integer(w,s->key[i]);put(w,"}");}
    }put(w,"}");
}
size_t tk_config_json(const tk_custom_t *s,char *out,size_t capacity)
{
    if(!out || !capacity || !s || s->group_count<1 || s->group_count>6 || s->card_count<1 || s->card_count>3)return 0;
    writer_t w={out,0,capacity,false};out[0]=0;put(&w,"{\"v\":1,\"groups\":[");
    for(int i=0;i<s->group_count;i++){
        if(i)put(&w,",");
        put(&w,"{\"name\":");string(&w,s->groups[i].name);
        for(int k=0;k<3;k++){put(&w,k==0?",\"up\":":k==1?",\"ok\":":",\"down\":");slot(&w,&s->groups[i].slots[k]);}put(&w,"}");
    }put(&w,"],\"cards\":[");
    for(int i=0;i<s->card_count;i++){
        if(i)put(&w,",");
        const tk_card_t *c=&s->cards[i];put(&w,"{\"title\":");string(&w,c->title);put(&w,",\"name\":");string(&w,c->name);
        put(&w,",\"line\":");string(&w,c->line);put(&w,",\"qr\":");string(&w,c->qr);put(&w,"}");
    }put(&w,"]}");return w.failed || w.used>TK_CFG_MAX?0:w.used;
}
void tk_config_defaults(tk_custom_t *s)
{
    memset(s,0,sizeof(*s));s->group_count=6;s->card_count=3;memcpy(s->cards,tk_default_cards,sizeof(s->cards));
    for(int g=0;g<6;g++){
        snprintf(s->groups[g].name,sizeof(s->groups[g].name),"%s",tk_macro_names[g]);
        for(int k=0;k<3;k++){
            const tk_binding_t *b=&tk_macro_bindings[g][k];tk_cfg_slot_t *slot=&s->groups[g].slots[k];snprintf(slot->label,sizeof(slot->label),"%s",b->label);
            slot->kind=TK_PACKET_KEY;
            for(unsigned i=0;i<2;i++)if(b->family[i].kind==TK_PACKET_KEY){slot->mask|=1u<<i;slot->mod[i]=b->family[i].mod;slot->key[i]=b->family[i].usage;}
        }
    }
}
