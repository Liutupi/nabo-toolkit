#include "tk_model.h"
#include <string.h>
int tk_model_macro_count(const tk_state_t *s){return s->config?s->config->group_count:tk_macro_default_count;}
const char *tk_model_macro_name(const tk_state_t *s,int group){return s->config?s->config->groups[group].name:tk_macro_names[group];}
tk_binding_t tk_model_macro_binding(const tk_state_t *s,int group,int column)
{
    if(!s->config)return tk_macro_bindings[group][column];
    const tk_cfg_slot_t *slot=&s->config->groups[group].slots[column];tk_binding_t b={.label=slot->label};
    for(int i=0;i<2;i++){
        if(slot->kind==TK_PACKET_TEXT)b.family[i]=(tk_packet_t){.kind=TK_PACKET_TEXT,.text=slot->text};
        else if(slot->kind==TK_PACKET_MEDIA)b.family[i]=(tk_packet_t){.kind=TK_PACKET_MEDIA,.usage=slot->media};
        else if(slot->mask&(1u<<i))b.family[i]=(tk_packet_t){.kind=TK_PACKET_KEY,.mod=slot->mod[i],.usage=slot->key[i]};
    }return b;
}
void tk_model_apply_config(tk_state_t *s,const tk_custom_t *config)
{
    s->config=config;s->card_count=config?config->card_count:3;
    memcpy(s->cards,config?config->cards:tk_default_cards,(size_t)s->card_count*sizeof(tk_card_t));
    int count=tk_model_macro_count(s);if(s->macro_group>=count)s->macro_group=count-1;
    if(s->card_idx>=s->card_count)s->card_idx=s->card_count-1;
}
