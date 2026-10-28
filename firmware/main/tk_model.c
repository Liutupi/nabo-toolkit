#include "tk_model_internal.h"
#include <stdio.h>
#include <string.h>

const char *const tk_page_names[11]={"boot","menu","macro","ppt","meet","media","cam","card","conn","set","voice"};
const char *const tk_key_names[6]={"up","down","ok","long_up","long_down","long_ok"};
const char *const tk_voice_names[TK_VOICE_TARGETS]={"读书","抖音","音乐","名片","拍照","截图","语音输入"};
static const int menu_pages[]={TK_PAGE_MACRO,TK_PAGE_PPT,TK_PAGE_MEET,TK_PAGE_MEDIA,TK_PAGE_CAM,TK_PAGE_CARD,TK_PAGE_CONN,TK_PAGE_SET};
static const int sleep_minutes[]={5,15,30,0};
const tk_card_t tk_default_cards[]={
    {"名片","NABO","AI Passport 小助手","https://ai-passport.folotoy.cn"},
    {"Wi-Fi","NABO-Guest","手机相机扫码直接连上","WIFI:T:WPA;S:NABO-Guest;P:nabo2026;;"},
    {"主页","github.com/Liutupi","我的开源项目","https://github.com/Liutupi"}};
void tk_model_init(tk_state_t *s, int64_t now)
{
    memset(s,0,sizeof(*s));s->page=TK_PAGE_BOOT;s->last_input=s->boot_start=now;
    s->confirm_del=-1;s->beep=s->voice=true;s->talk=1;s->sleep=3;s->ppt_pages=1;s->card_count=3;
    s->remote_dim=true;s->screen_since=-1;s->media_select=true;
    memcpy(s->cards,tk_default_cards,sizeof(tk_default_cards));
}
tk_os_t tk_model_os(const tk_state_t *s)
{
    return s->active>=0 && s->active<3 && s->slots[s->active].used ? (tk_os_t)s->slots[s->active].os : TK_OS_WIN;
}
void tk_model_toast(tk_state_t *s, int64_t now, const char *text, bool error)
{
    if(error)tk_model_screen_reset(s,now);
    s->toast=true;snprintf(s->toast_text,sizeof(s->toast_text),"%s",text);s->toast_error=error;s->toast_until=now+(error?1500:1200);
}
static tk_effect_t *effect(tk_effects_t *out, int type)
{
    if(out->count>=TK_EFFECT_MAX){out->overflow=true;return NULL;}
    tk_effect_t *e=&out->items[out->count++];memset(e,0,sizeof(*e));e->type=type;return e;
}
void tk_model_beep(tk_effects_t *out, const tk_state_t *s, int f, int ms)
{
    if(!s->beep)return;
    tk_model_cue(out,f,ms?ms:40);
}
void tk_model_cue(tk_effects_t *out,int f,int ms){tk_effect_t *e=effect(out,TK_EFFECT_BEEP);if(e){e->frequency=f;e->ms=ms;}}
static void packet(tk_effects_t *out, const tk_packet_t *p, const char *label)
{
    tk_effect_t *e=effect(out,TK_EFFECT_HID);if(!e)return;
    e->kind=p->kind;e->mod=p->mod;e->usage=p->usage;e->length=tk_hid_report(p,e->bytes);
    snprintf(e->label,sizeof(e->label),"%s",label);
}
bool tk_model_send(tk_effects_t *out, tk_state_t *s, int64_t now, const tk_binding_t *b, const char *label, int key)
{
    if(!s->connected){tk_model_toast(s,now,"未连接 · 去菜单选「连接」",true);return false;}
    const tk_packet_t *p=tk_hid_resolve(b,tk_model_os(s));
    if(!p){tk_model_toast(s,now,"这个设备没有对应快捷键",true);return false;}
    char chord[96], description[192], toast[256];tk_hid_chord(p,tk_model_os(s),chord,sizeof(chord));
    snprintf(description,sizeof(description),"%s · %s",label,chord);
    if(p->kind==TK_PACKET_TEXT){
        const unsigned char *text=(const unsigned char *)(p->text?p->text:"");tk_packet_t q;int count=0;
        for(const unsigned char *c=text;*c;c++)if(tk_hid_char(*c,&q))count++;
        if(count>TK_EFFECT_MAX-out->count){out->overflow=true;tk_model_toast(s,now,"文字太长，稍后再试",true);return false;}
        for(const unsigned char *c=text;*c;c++)if(tk_hid_char(*c,&q))packet(out,&q,description);
    }else{
        if(out->count==TK_EFFECT_MAX){out->overflow=true;return false;}
        packet(out,p,description);
    }
    snprintf(toast,sizeof(toast),"→ %s  %s",chord,label);tk_model_toast(s,now,toast,false);
    s->react=true;s->react_key=key;s->react_until=now+500;
    if(key>=0){s->hit=true;s->hit_key=key;s->hit_until=now+250;}
    return true;
}
int64_t tk_model_ppt_elapsed(const tk_state_t *s,int64_t now){return s->ppt_acc+(s->ppt_running?now-s->ppt_start:0);}
static bool screen_eligible(const tk_state_t *s)
{
    return s->remote_dim && s->connected && !s->pairing && !s->os_pick &&
        (s->page==TK_PAGE_MACRO || (s->page==TK_PAGE_MEDIA && !s->media_select));
}
void tk_model_screen_reset(tk_state_t *s,int64_t now){s->screen_off=false;s->screen_since=now;}
static void screen_sync(tk_state_t *s,int64_t now,bool reset)
{
    if(!screen_eligible(s)){s->screen_off=false;s->screen_since=-1;return;}
    if(reset || s->screen_since<0)tk_model_screen_reset(s,now);
    if(now-s->screen_since>=30000)s->screen_off=true;
}
static bool voice_blocked(const tk_state_t *s){return s->pairing || s->os_pick || s->confirm_del>=0;}
static void voice_token(tk_state_t *s){if(++s->voice_token==0)++s->voice_token;}
static void voice_cancel(tk_state_t *s){voice_token(s);s->voice_busy=false;s->voice_operation=TK_VOICE_NONE;}
bool tk_model_voice_open(tk_state_t *s,int64_t now)
{
    if(!s || s->page!=TK_PAGE_MENU || voice_blocked(s))return false;
    voice_cancel(s);s->voice_status=TK_VOICE_READY;s->page=TK_PAGE_VOICE;
    s->toast=s->react=s->hit=false;s->cam_end=0;s->burst_left=0;s->last_input=now;
    screen_sync(s,now,true);return true;
}
bool tk_model_voice_templates(tk_state_t *s,const uint8_t counts[TK_VOICE_TARGETS])
{
    if(!s || !counts)return false;
    // Runtime snapshots may place this byte array at an unaligned address.
    // Volatile byte access prevents a compiler from widening this to word I/O.
    const volatile uint8_t *source=counts;uint8_t values[TK_VOICE_TARGETS];
    for(int i=0;i<TK_VOICE_TARGETS;i++){values[i]=source[i];if(values[i]>3)return false;}
    volatile uint8_t *destination=s->voice_counts;
    for(int i=0;i<TK_VOICE_TARGETS;i++)destination[i]=values[i];
    return true;
}
static bool voice_pending(const tk_state_t *s,uint32_t token)
{
    return s && s->page==TK_PAGE_VOICE && s->voice_busy && s->voice_token==token && !voice_blocked(s);
}
bool tk_model_voice_progress(tk_state_t *s,uint32_t token,int status,int64_t now)
{
    if(!voice_pending(s,token) || (status!=TK_VOICE_LISTENING && status!=TK_VOICE_RECORDING && status!=TK_VOICE_PREPARING) ||
       (status==TK_VOICE_LISTENING && s->voice_operation!=TK_VOICE_RECOGNIZE) ||
       (status==TK_VOICE_RECORDING && s->voice_operation!=TK_VOICE_ENROLL))return false;
    s->voice_status=status;s->last_input=now;return true;
}
bool tk_model_voice_result(tk_state_t *s,uint32_t token,int outcome,int target,int count,int64_t now)
{
    if(!voice_pending(s,token) || outcome<TK_VOICE_RESULT_ENROLLED || outcome>TK_VOICE_RESULT_CAPTURE_ERROR)return false;
    if(outcome<=TK_VOICE_RESULT_MATCHED && (target<0 || target>=TK_VOICE_TARGETS))return false;
    if(outcome==TK_VOICE_RESULT_ENROLLED && (s->voice_operation!=TK_VOICE_ENROLL || target!=s->voice_selected || count<1 || count>3))return false;
    if(outcome==TK_VOICE_RESULT_MATCHED && (s->voice_operation!=TK_VOICE_RECOGNIZE || !s->voice_counts[target]))return false;
    s->voice_busy=false;s->voice_operation=TK_VOICE_NONE;s->last_input=now;
    if(outcome==TK_VOICE_RESULT_ENROLLED){s->voice_counts[target]=(uint8_t)count;s->voice_status=TK_VOICE_SAVED;return true;}
    if(outcome!=TK_VOICE_RESULT_MATCHED){
        const int statuses[]={0,0,TK_VOICE_REJECTED,TK_VOICE_ERROR,TK_VOICE_AMBIGUOUS,TK_VOICE_TOO_LONG,TK_VOICE_CAPTURE_ERROR};
        s->voice_status=statuses[outcome];return true;
    }
    int group=-1;
    if(target==0 || target==5 || target==6){
        for(int i=0;i<tk_model_macro_count(s);i++){
            const char *name=tk_model_macro_name(s,i);
            bool match=target==0?(!strcmp(name,"微信读书") || !strcmp(name,"读书")):
                target==5?!strcmp(name,"截图"):(!strcmp(name,"Typeless") || !strcmp(name,"语音输入"));
            if(match){group=i;break;}
        }
        if(group<0){s->voice_status=TK_VOICE_MISSING_GROUP;tk_model_toast(s,now,target==0?"没有「微信读书」分组":target==5?"没有「截图」分组":"没有「Typeless」分组",true);return true;}
    }
    s->voice_status=TK_VOICE_READY;s->toast=s->react=s->hit=false;s->cam_end=0;s->burst_left=0;
    if(target==0 || target==5 || target==6){s->page=TK_PAGE_MACRO;s->menu=0;s->macro_group=group;}
    else if(target==1 || target==2){s->page=TK_PAGE_MEDIA;s->menu=3;s->media_mode=target==1?1:0;s->media_select=false;}
    else if(target==3){s->page=TK_PAGE_CARD;s->menu=5;s->card_zoom=false;}
    else{s->page=TK_PAGE_CAM;s->menu=4;}
    screen_sync(s,now,true);return true;
}
static void voice_press(tk_state_t *s,tk_key_t key)
{
    if(s->voice_busy)return;
    if(key==TK_UP || key==TK_DOWN){s->voice_selected=(s->voice_selected+(key==TK_UP?TK_VOICE_TARGETS-1:1))%TK_VOICE_TARGETS;s->voice_status=TK_VOICE_READY;}
    else if(key==TK_OK || key==TK_LONG_OK){
        if(voice_blocked(s))return;
        bool any=false;for(int i=0;i<TK_VOICE_TARGETS;i++)if(s->voice_counts[i])any=true;
        if(key==TK_OK && !any){s->voice_status=TK_VOICE_UNTRAINED;return;}
        voice_token(s);s->voice_busy=true;s->voice_operation=key==TK_OK?TK_VOICE_RECOGNIZE:TK_VOICE_ENROLL;
        s->voice_status=TK_VOICE_PREPARING;s->toast=false;
    }
}
static void dispatch_press(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    out->count=0;out->overflow=false;
    if(key<TK_UP || key>TK_LONG_OK)return;
    s->last_input=now;
    if(s->os_pick){tk_model_os_pick(s,key,now,out);return;}
    if(s->page==TK_PAGE_BOOT){s->page=TK_PAGE_MENU;return;}
    if(s->page==TK_PAGE_MENU){
        if(key==TK_UP || key==TK_DOWN){s->menu=(s->menu+(key==TK_UP?7:1))%8;tk_model_beep(out,s,660,40);}
        else if(key==TK_OK){s->page=menu_pages[s->menu];s->toast=false;if(s->page==TK_PAGE_MEDIA)s->media_select=true;tk_model_beep(out,s,880,40);}
        else if(key==TK_LONG_OK)tk_model_voice_open(s,now);
        return;
    }
    if(key==TK_LONG_UP){
        if(s->page==TK_PAGE_VOICE)voice_cancel(s);
        if(s->pairing){s->pairing=false;tk_model_toast(s,now,"已停止配对",false);}
        else if(s->page==TK_PAGE_CARD && s->card_zoom)s->card_zoom=false;
        else if(s->page==TK_PAGE_MEDIA && !s->media_select){s->media_select=true;s->toast=false;}
        else{s->cam_end=0;s->burst_left=0;s->confirm_del=-1;s->page=TK_PAGE_MENU;s->toast=false;}
        tk_model_beep(out,s,523,40);return;
    }
    if(s->page==TK_PAGE_CONN)tk_model_connection(s,key,now,out);
    else if(s->page==TK_PAGE_SET)tk_model_settings(s,key,out);
    else if(s->page==TK_PAGE_VOICE)voice_press(s,key);
    else tk_model_tools(s,key,now,out);
}
void tk_model_press(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *out)
{
    out->count=0;out->overflow=false;if(key<TK_UP || key>TK_LONG_OK)return;
    if(s->voice_busy && (s->page!=TK_PAGE_VOICE || voice_blocked(s)))voice_cancel(s);
    screen_sync(s,now,false);
    if(s->screen_off && key==TK_LONG_OK){s->last_input=now;tk_model_screen_reset(s,now);return;}
    int page=s->page;bool selecting=s->media_select;
    dispatch_press(s,key,now,out);
    screen_sync(s,now,s->page!=page || key==TK_LONG_UP ||
        (s->page==TK_PAGE_MACRO && (key==TK_LONG_OK || key==TK_LONG_DOWN)) ||
        (s->page==TK_PAGE_MEDIA && selecting!=s->media_select));
}
void tk_model_tick(tk_state_t *s,int64_t now,tk_effects_t *out)
{
    out->count=0;out->overflow=false;
    if(s->voice_busy && (s->page!=TK_PAGE_VOICE || voice_blocked(s)))voice_cancel(s);
    if(s->page==TK_PAGE_BOOT){
        int64_t elapsed=now-s->boot_start;
        if(!s->boot_voiced && elapsed>=1400){s->boot_voiced=true;if(s->voice)effect(out,TK_EFFECT_VOICE);}
        if(elapsed>=5500)s->page=TK_PAGE_MENU;
    }
    if(s->cam_end>0){
        int left=(int)((s->cam_end-now+999)/1000);
        if(now>=s->cam_end){s->cam_end=0;tk_model_shoot(s,now,out);}
        else if(left<s->cam_last_sec){s->cam_last_sec=left;tk_effect_t *e=effect(out,TK_EFFECT_BEEP);if(e){e->frequency=988;e->ms=60;}}
    }
    while(s->burst_left>0 && now>=s->next_shot){
        tk_model_shoot(s,now,out);s->burst_left--;s->next_shot+=600;if(!s->connected)s->burst_left=0;
    }
    if(s->pairing && now>=s->pair_until){s->pairing=false;tk_model_toast(s,now,"配对超时",true);}
    if(s->toast && now>=s->toast_until)s->toast=false;
    if(s->react && now>=s->react_until)s->react=false;
    if(s->hit && now>=s->hit_until)s->hit=false;
    screen_sync(s,now,false);
}
void tk_model_event(tk_state_t *s,const char *event,int64_t now,const char *arg)
{
    if(!strcmp(event,"paired") && s->pairing)tk_model_pair_success(s,arg);
    else if(!strcmp(event,"passkey") && s->pairing && arg){
        size_t n=strlen(arg);bool valid=n==6;uint32_t code=0;
        for(size_t i=0;i<n;i++){if(arg[i]<'0'||arg[i]>'9')valid=false;else code=code*10+(unsigned)(arg[i]-'0');}
        if(valid){s->passkey_valid=true;s->passkey=code;}
    }else if(!strcmp(event,"disconnect"))s->connected=false;
    else if(!strcmp(event,"reconnect") && !s->pairing && s->slots[s->active].used)s->connected=true;
    else if(!strcmp(event,"wake")){voice_cancel(s);s->page=TK_PAGE_BOOT;s->boot_start=now;s->boot_voiced=false;s->os_pick=false;s->last_input=now;s->connected=false;s->pairing=false;}
    screen_sync(s,now,!strcmp(event,"wake"));
}
bool tk_model_sleep_due(const tk_state_t *s,int64_t now)
{
    if(s->ppt_running || s->cam_end>0 || s->pairing || s->voice_busy)return false;
    int minutes=sleep_minutes[s->sleep];
    if(!minutes){if(s->connected)return false;minutes=5;}
    return now-s->last_input>=(int64_t)minutes*60000;
}
