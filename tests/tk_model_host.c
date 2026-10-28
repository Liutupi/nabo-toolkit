// Host ABI helpers only. All state transitions and HID bytes use production code.
#include "tk_model.h"
#include <stdio.h>
#include <string.h>
size_t tk_host_state_size(void){return sizeof(tk_state_t);}
size_t tk_host_effects_size(void){return sizeof(tk_effects_t);}
void tk_host_demo(tk_state_t *s,int os)
{
    tk_model_init(s,0);
    s->slots[0].used=true;s->slots[0].os=os;snprintf(s->slots[0].name,96,"MacBook");
    s->slots[1].used=true;s->slots[1].os=TK_OS_IOS;snprintf(s->slots[1].name,96,"iPhone");
    s->bind_order[0]=0;s->bind_order[1]=1;s->bind_count=2;s->connected=true;
}
const tk_packet_t *tk_host_binding(int table,int row,int col,int os)
{
    const tk_binding_t *b=NULL;
    if(table==0 && row<5)b=&tk_ppt_bindings[row];
    else if(table==1 && row<4 && col<3)b=&tk_meeting_bindings[row][col];
    else if(table==2 && row<6)b=&tk_media_bindings[row];
    else if(table==3 && row<tk_macro_default_count && col<3)b=&tk_macro_bindings[row][col];
    else if(table==4)b=&tk_shutter_binding;
    else if(table==5 && row<6)b=&tk_douyin_bindings[row];
    return tk_hid_resolve(b,(tk_os_t)os);
}
