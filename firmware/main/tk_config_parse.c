#include "tk_config.h"
#include "cJSON.h"
#include <stdlib.h>
#include <string.h>
static const cJSON *field(const cJSON *o,const char *key){return cJSON_GetObjectItemCaseSensitive(o,key);}
static bool object(const cJSON *o,const char *const *allowed,unsigned count)
{
    if(!cJSON_IsObject(o))return false;
    unsigned seen=0;
    for(const cJSON *p=o->child;p;p=p->next){
        unsigned i=0;while(i<count && strcmp(p->string,allowed[i]))i++;
        if(i==count || (seen&(1u<<i)))return false;
        seen|=1u<<i;
    }return true;
}
static bool num(const cJSON *v,int lo,int hi){return cJSON_IsNumber(v) && v->valueint>=lo && v->valueint<=hi;}
static bool copy(const cJSON *v,char *out,unsigned chars,size_t bytes,bool empty,bool newline)
{
    if(!cJSON_IsString(v) || !tk_config_string(v->valuestring,chars,bytes,empty,newline))return false;
    strcpy(out,v->valuestring);return true;
}
static const char *slot(tk_cfg_slot_t *s,const cJSON *o)
{
    static const char *const keys[]={"label","mac","win","media","text"},*const combo[]={"mod","key"};
    if(!object(o,keys,5) || !copy(field(o,"label"),s->label,8,sizeof(s->label),true,false))return "label";
    const cJSON *m=field(o,"media"),*t=field(o,"text"),*a=field(o,"mac"),*b=field(o,"win");
    if(m){
        if(t || a || b || !num(m,1,1023))return "media";
        int n=m->valueint;if(n!=0xcd && n!=0xb5 && n!=0xb6 && n!=0xe9 && n!=0xea)return "media";
        s->kind=TK_PACKET_MEDIA;s->media=n;return NULL;
    }
    if(t){
        if(a || b || !copy(t,s->text,64,sizeof(s->text),true,true))return "text";
        for(const unsigned char *p=(const unsigned char *)s->text;*p;p++)if(*p>126)return "text";
        s->kind=TK_PACKET_TEXT;return NULL;
    }
    s->kind=TK_PACKET_KEY;
    for(unsigned i=0;i<2;i++){
        const cJSON *v=i?b:a;if(!v || cJSON_IsNull(v))continue;
        if(!object(v,combo,2) || !num(field(v,"mod"),0,255) || !num(field(v,"key"),0,0x73))return "key";
        int key=field(v,"key")->valueint;if(key>0 && key<4)return "key";
        s->mask|=1u<<i;s->mod[i]=field(v,"mod")->valueint;s->key[i]=key;
    }return NULL;
}
static const char *decode(tk_custom_t *s,const cJSON *root)
{
    static const char *const rootkeys[]={"v","groups","cards"},*const groupkeys[]={"name","up","ok","down"},*const cardkeys[]={"title","name","line","qr"};
    if(!object(root,rootkeys,3))return "keys";
    if(!num(field(root,"v"),1,1))return "version";
    const cJSON *groups=field(root,"groups"),*cards=field(root,"cards");
    if(!cJSON_IsArray(groups) || (s->group_count=cJSON_GetArraySize(groups))<1 || s->group_count>6)return "groups";
    if(!cJSON_IsArray(cards) || (s->card_count=cJSON_GetArraySize(cards))<1 || s->card_count>3)return "cards";
    for(int i=0;i<s->group_count;i++){
        const cJSON *g=cJSON_GetArrayItem(groups,i);tk_cfg_group_t *next=&s->groups[i];
        if(!object(g,groupkeys,4) || !copy(field(g,"name"),next->name,8,sizeof(next->name),false,false))return "name";
        for(int k=0;k<3;k++){const char *e=slot(&next->slots[k],field(g,groupkeys[k+1]));if(e)return e;}
    }
    for(int i=0;i<s->card_count;i++){
        const cJSON *c=cJSON_GetArrayItem(cards,i);tk_card_t *next=&s->cards[i];if(!object(c,cardkeys,4))return "keys";
        if(!copy(field(c,"title"),next->title,6,25,false,false) || !copy(field(c,"name"),next->name,24,sizeof(next->name),true,false) ||
           !copy(field(c,"line"),next->line,32,sizeof(next->line),true,false) || !copy(field(c,"qr"),next->qr,160,161,false,true))return "card";
    }return NULL;
}
const char *tk_config_parse(tk_custom_t *out,const char *json,size_t size)
{
    const char *error=tk_config_lex(json,size);if(error)return error;
    const char *end=NULL;cJSON *tree=cJSON_ParseWithLengthOpts(json,size,&end,false);
    if(!tree)return "json";
    while(end<json+size && (*end==' '||*end=='\t'||*end=='\n'||*end=='\r'))end++;
    if(end!=json+size){cJSON_Delete(tree);return "json";}
    tk_custom_t *next=calloc(1,sizeof(*next));if(!next){cJSON_Delete(tree);return "memory";}
    error=decode(next,tree);cJSON_Delete(tree);
    if(!error){char *canonical=malloc(TK_CFG_MAX+1);if(!canonical)error="memory";else{if(!tk_config_json(next,canonical,TK_CFG_MAX+1))error="size";free(canonical);}}
    if(!error)*out=*next;
    free(next);return error;
}
