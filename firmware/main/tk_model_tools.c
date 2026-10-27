#include "tk_model_internal.h"
#include <stdio.h>

static void ppt_start(tk_state_t *s,int64_t now)
{
    s->ppt_running=true;s->ppt_start=now;s->ppt_acc=0;s->ppt_pages=1;s->ppt_black=false;
}
static void ppt(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    if(key==TK_UP || key==TK_DOWN){
        if(!tk_model_send(out,s,now,&tk_ppt_bindings[key==TK_UP?0:1],key==TK_UP?"上一页":"下一页",key))return;
        if(!s->ppt_running && tk_model_ppt_elapsed(s,now)==0)ppt_start(s,now);
        s->ppt_pages+=key==TK_UP?-1:1;if(s->ppt_pages<1)s->ppt_pages=1;
    }else if(key==TK_OK){
        if(tk_model_send(out,s,now,&tk_ppt_bindings[2],s->ppt_black?"恢复画面":"黑屏",key))s->ppt_black=!s->ppt_black;
    }else if(key==TK_LONG_OK){
        if(tk_model_send(out,s,now,&tk_ppt_bindings[4],"开始放映",TK_OK))ppt_start(s,now);
    }else if(key==TK_LONG_DOWN){
        if(tk_model_send(out,s,now,&tk_ppt_bindings[3],"结束放映",TK_DOWN) && s->ppt_running){
            s->ppt_acc=tk_model_ppt_elapsed(s,now);s->ppt_running=false;s->ppt_black=false;
        }
    }
}
static void meet(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    char text[160];
    if(key==TK_LONG_OK){s->meet_app=(s->meet_app+1)%4;snprintf(text,sizeof(text),"会议软件：%s",tk_meeting_names[s->meet_app]);tk_model_toast(s,now,text,false);tk_model_beep(out,s,880,40);return;}
    if(key>TK_OK)return;
    tk_os_t os=tk_model_os(s);
    if(os!=TK_OS_MAC && os!=TK_OS_WIN){tk_model_toast(s,now,"会议快捷键只支持电脑",true);return;}
    int field=key==TK_OK?0:key==TK_UP?1:2;
    const char *labels[]={"静音切换","摄像头切换","举手"};
    const tk_binding_t *b=&tk_meeting_bindings[s->meet_app][field];
    if(!tk_hid_resolve(b,os)){snprintf(text,sizeof(text),"%s没有%s快捷键",tk_meeting_names[s->meet_app],labels[field]);tk_model_toast(s,now,text,true);return;}
    tk_model_send(out,s,now,b,labels[field],key);
}
void tk_model_shoot(tk_state_t *s,int64_t now,tk_effects_t *out)
{
    if(tk_model_send(out,s,now,&tk_shutter_binding,"快门",TK_OK)){s->shots++;tk_model_cue(out,1568,120);}
}
static void camera(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    static const int delays[]={0,3,10};char text[64];bool counting=s->cam_end>0;
    if(key==TK_OK && counting){s->cam_end=0;tk_model_toast(s,now,"已取消",false);tk_model_beep(out,s,440,40);return;}
    if(counting || s->burst_left>0)return;
    if(key==TK_UP){
        s->cam_delay=(s->cam_delay+1)%3;
        if(delays[s->cam_delay])snprintf(text,sizeof(text),"延时 %d 秒",delays[s->cam_delay]);else snprintf(text,sizeof(text),"不延时");
        tk_model_toast(s,now,text,false);tk_model_beep(out,s,880,40);
    }else if(!s->connected && (key==TK_OK || key==TK_DOWN))tk_model_toast(s,now,"未连接 · 去菜单选「连接」",true);
    else if(key==TK_OK){
        int d=delays[s->cam_delay];
        if(!d)tk_model_shoot(s,now,out);
        else{s->cam_end=now+d*1000;s->cam_last_sec=d;tk_model_cue(out,988,60);}
    }else if(key==TK_DOWN){s->burst_left=5;s->next_shot=now;}
}
static void macro(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    if(key==TK_LONG_OK || key==TK_LONG_DOWN){
        int count=tk_model_macro_count(s);s->macro_group=(s->macro_group+(key==TK_LONG_OK?1:count-1))%count;
        char text[96];snprintf(text,sizeof(text),"第 %d 组 · %s",s->macro_group+1,tk_model_macro_name(s,s->macro_group));
        tk_model_toast(s,now,text,false);tk_model_beep(out,s,880,40);return;
    }
    if(key>TK_OK)return;
    tk_binding_t b=tk_model_macro_binding(s,s->macro_group,key==TK_UP?0:key==TK_OK?1:2);
    tk_model_send(out,s,now,&b,b.label,key);
}
void tk_model_tools(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    switch(s->page){
    case TK_PAGE_PPT:ppt(s,key,now,out);break;
    case TK_PAGE_MEET:meet(s,key,now,out);break;
    case TK_PAGE_MEDIA:{const tk_binding_t *b=&tk_media_bindings[key];if(tk_hid_resolve(b,tk_model_os(s)))tk_model_send(out,s,now,b,b->label,key>=3?key-3:key);break;}
    case TK_PAGE_CAM:camera(s,key,now,out);break;
    case TK_PAGE_MACRO:macro(s,key,now,out);break;
    case TK_PAGE_CARD:
        if(key==TK_OK){s->card_zoom=!s->card_zoom;tk_model_beep(out,s,880,40);}
        else if(!s->card_zoom && (key==TK_UP || key==TK_DOWN)){s->card_idx=(s->card_idx+(key==TK_UP?s->card_count-1:1))%s->card_count;tk_model_beep(out,s,660,40);}
        break;
    default:break;
    }
}
