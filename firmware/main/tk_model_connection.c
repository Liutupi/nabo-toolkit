#include "tk_model_internal.h"
#include <stdio.h>

static void remove_order(tk_state_t *s,int slot)
{
    int used=0;
    for(int i=0;i<s->bind_count;i++)if(s->bind_order[i]!=slot)s->bind_order[used++]=s->bind_order[i];
    s->bind_count=used;
}
void tk_model_pair_success(tk_state_t *s,const char *name)
{
    int slot=-1;for(int i=0;i<3;i++)if(!s->slots[i].used){slot=i;break;}
    if(slot<0)slot=s->bind_order[0];
    s->slots[slot].used=true;s->slots[slot].os=TK_OS_WIN;
    if(name && *name)snprintf(s->slots[slot].name,sizeof(s->slots[slot].name),"%s",name);
    else snprintf(s->slots[slot].name,sizeof(s->slots[slot].name),"新设备 %d",slot+1);
    remove_order(s,slot);s->bind_order[s->bind_count++]=slot;
    s->pairing=false;s->active=slot;s->connected=true;s->conn_sel=slot;
    s->os_pick=true;s->os_slot=slot;s->os_sel=1;
}
void tk_model_connection(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    if(s->confirm_del>=0){
        if(key==TK_OK){
            int slot=s->confirm_del;s->slots[slot].used=false;remove_order(s,slot);
            if(s->active==slot)s->connected=false;
            tk_model_toast(s,now,"已删除配对",false);
        }
        s->confirm_del=-1;return;
    }
    if(s->pairing){if(key==TK_OK){s->pairing=false;tk_model_toast(s,now,"已停止配对",false);}return;}
    int i=s->conn_sel;bool slot=i<3 && s->slots[i].used;char text[160];
    if(key==TK_UP || key==TK_DOWN){s->conn_sel=(i+(key==TK_UP?3:1))%4;tk_model_beep(out,s,660,40);}
    else if(key==TK_OK){
        if(i==3 || !slot){
            if(s->bind_count==3){snprintf(text,sizeof(text),"配对成功后替换 %s",s->slots[s->bind_order[0]].name);tk_model_toast(s,now,text,false);}
            s->connected=false;s->pairing=true;s->pair_until=now+60000;s->passkey_valid=false;
        }else{s->active=i;s->connected=true;snprintf(text,sizeof(text),"已连接 %s",s->slots[i].name);tk_model_toast(s,now,text,false);}
        tk_model_beep(out,s,880,40);
    }else if(key==TK_LONG_OK && slot){s->os_pick=true;s->os_slot=i;s->os_sel=s->slots[i].os;}
    else if(key==TK_LONG_DOWN && slot)s->confirm_del=i;
}
void tk_model_os_pick(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    if(key==TK_UP || key==TK_DOWN)s->os_sel=(s->os_sel+(key==TK_UP?3:1))%4;
    else if(key==TK_LONG_UP)s->os_pick=false;
    else if(key==TK_OK){
        s->slots[s->os_slot].os=s->os_sel;s->os_pick=false;char text[64];
        snprintf(text,sizeof(text),"设备类型：%s",tk_os_names[s->os_sel]);tk_model_toast(s,now,text,false);
    }
    tk_model_beep(out,s,660,40);
}
void tk_model_settings(tk_state_t *s,tk_key_t key,tk_effects_t *out)
{
    if(key==TK_UP || key==TK_DOWN)s->set_sel=(s->set_sel+(key==TK_UP?4:1))%5;
    else if(key==TK_OK){
        if(s->set_sel==0)s->beep=!s->beep;
        else if(s->set_sel==1)s->voice=!s->voice;
        else if(s->set_sel==2)s->talk=(s->talk+1)%7;
        else if(s->set_sel==3)s->sleep=(s->sleep+1)%4;
    }
    tk_model_beep(out,s,660,40);
}
