#include "tk_ui_internal.h"
#include <stdio.h>

static void row(ag_t *g,const tk_state_t *s,int index,const char *label,const tk_binding_t *binding,int key)
{
    int y=142+index*38;bool hit=s->hit && s->hit_key==key;uint16_t accent=tk_ui_accents[s->page];
    ag_rect(g,8,y+2,138,34,8,UI_INK,255,0,0);if(hit)y+=2;
    ag_rect(g,8,y,138,34,8,hit?accent:UI_PANEL,255,0,0);
    ag_rect(g,12,y+6,30,22,6,hit?UI_INK:UI_BG,255,0,0);
    ui_text(g,key==TK_OK?"OK":key==TK_UP?"↑":"↓",27,y+22,key==TK_OK?12:16,hit?accent:UI_PAPER,NT_ALIGN_CENTER);
    const tk_packet_t *p=tk_hid_resolve(binding,tk_model_os(s));char chord[96];tk_hid_chord(p,tk_model_os(s),chord,sizeof(chord));
    if(binding && p){ui_fit(g,label,50,y+16,88,16,hit?UI_INK:UI_PAPER,NT_ALIGN_LEFT);ui_fit(g,chord,50,y+30,88,12,hit?UI_INK:UI_DIM,NT_ALIGN_LEFT);}
    else ui_fit(g,label,50,y+23,88,16,hit?UI_INK:UI_PAPER,NT_ALIGN_LEFT);
}
static void rows(ag_t *g,const tk_state_t *s,const char *up,const char *ok,const char *down,const tk_binding_t *u,const tk_binding_t *o,const tk_binding_t *d)
{
    row(g,s,0,up,u,TK_UP);row(g,s,1,down,d,TK_DOWN);row(g,s,2,ok,o,TK_OK);
}
static void remote_bar(ag_t *g,const tk_state_t *s,const char *hint)
{
    if(!s->remote_dim){ui_bar(g,hint);return;}
    ag_rect(g,0,290,240,30,0,UI_INK,255,0,0);
    ui_text(g,"30秒息屏 · 长OK亮屏",120,301,12,UI_PAPER,NT_ALIGN_CENTER);
    ui_fit(g,hint,120,315,226,12,UI_PAPER,NT_ALIGN_CENTER);
}
static void media_choice(ag_t *g,const tk_state_t *s)
{
    static const char *const names[]={"音乐","抖音"},*const descriptions[]={"音量 · 播放 · 切歌","方向键 ↑ / → / ↓"};
    ui_text(g,"选择媒体玩法",12,53,12,UI_DIM,NT_ALIGN_LEFT);
    for(int i=0;i<2;i++){int y=66+i*78;bool selected=s->media_mode==i;
        ag_rect(g,10,y,136,64,10,selected?UI_GOLD:UI_PANEL,255,selected?UI_INK:0,selected?2:0);
        ag_rect(g,13,y+10,4,44,0,tk_ui_accents[TK_PAGE_MEDIA],255,0,0);
        ui_text(g,names[i],80,y+28,18,selected?UI_INK:UI_PAPER,NT_ALIGN_CENTER);
        ui_fit(g,descriptions[i],80,y+49,116,12,selected?UI_INK:UI_DIM,NT_ALIGN_CENTER);
    }
    ui_text(g,"选择后开始遥控",12,240,12,UI_DIM,NT_ALIGN_LEFT);ui_bar(g,"↑↓ 选择 · OK 进入 · 长↑ 返回");
}
void ui_tools(ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a)
{
    uint16_t accent=tk_ui_accents[s->page];char text[192];
    switch(s->page){
    case TK_PAGE_MACRO:{
        int count=tk_model_macro_count(s);tk_binding_t b[3];for(int i=0;i<3;i++)b[i]=tk_model_macro_binding(s,s->macro_group,i);
        snprintf(text,sizeof(text),"第 %d / %d 组",s->macro_group+1,count);ui_text(g,text,12,53,12,UI_DIM,NT_ALIGN_LEFT);
        for(int i=0;i<count;i++)ag_circle(g,170+i*10,49,3,i==s->macro_group?accent:UI_PANEL,255,0,0);
        ag_rect(g,12,62,216,44,10,UI_PANEL,255,accent,2);ui_text(g,tk_model_macro_name(s,s->macro_group),120,91,18,UI_PAPER,NT_ALIGN_CENTER);
        snprintf(text,sizeof(text),"%s 键位 · 配置页里可以改",tk_os_names[tk_model_os(s)]);ui_fit(g,text,12,125,216,12,UI_DIM,NT_ALIGN_LEFT);
        rows(g,s,b[0].label,b[1].label,b[2].label,&b[0],&b[1],&b[2]);
        remote_bar(g,s,"长OK 下组 · 长↓ 上组 · 长↑ 返回");break;}
    case TK_PAGE_PPT:{
        static const int minutes[]={5,10,15,20,30,45,60};int64_t elapsed=tk_model_ppt_elapsed(s,now),goal=(int64_t)minutes[s->talk]*60000;
        bool overtime=elapsed>goal;int64_t shown=(overtime?elapsed-goal:elapsed)/1000;
        ui_text(g,"演讲计时",12,53,12,UI_DIM,NT_ALIGN_LEFT);snprintf(text,sizeof(text),"已翻 %d 页",s->ppt_pages);ui_text(g,text,228,53,12,UI_DIM,NT_ALIGN_RIGHT);
        snprintf(text,sizeof(text),"%s%02lld:%02lld",overtime?"+":"",(long long)(shown/60),(long long)(shown%60));
        ui_text(g,text,120,101,48,overtime?UI_RED:goal-elapsed<=120000?accent:0xffff,NT_ALIGN_CENTER);
        ag_rect(g,16,114,208,8,4,UI_PANEL,255,0,0);int width=elapsed>=goal?208:(int)(elapsed*208/goal);if(width>0)ag_rect(g,16,114,width,8,4,overtime?UI_RED:accent,255,0,0);
        ui_text(g,s->ppt_running?"计时中 · 翻页继续计时":"翻页或长按 OK 开始",12,135,12,UI_DIM,NT_ALIGN_LEFT);
        rows(g,s,"上一页",s->ppt_black?"恢复画面":"黑屏","下一页",&tk_ppt_bindings[0],&tk_ppt_bindings[2],&tk_ppt_bindings[1]);
        if(s->ppt_black){ag_rect(g,150,144,82,20,5,UI_INK,255,0,0);ui_text(g,"黑屏中",191,159,12,UI_PAPER,NT_ALIGN_CENTER);}
        ui_bar(g,"长 OK 开始 · 长↓ 结束 · 长↑ 返回");break;
    }
    case TK_PAGE_MEET:{
        snprintf(text,sizeof(text),"会议软件 %d / 4",s->meet_app+1);ui_text(g,text,12,53,12,UI_DIM,NT_ALIGN_LEFT);
        ag_rect(g,12,62,216,44,10,UI_PANEL,255,accent,2);ui_text(g,tk_meeting_names[s->meet_app],120,91,18,UI_PAPER,NT_ALIGN_CENTER);
        bool desktop=tk_model_os(s)==TK_OS_MAC || tk_model_os(s)==TK_OS_WIN;
        if(desktop)snprintf(text,sizeof(text),"%s · 会议窗口要在最前面",tk_os_names[tk_model_os(s)]);else snprintf(text,sizeof(text),"会议快捷键只支持电脑");
        ui_fit(g,text,12,125,216,12,desktop?UI_DIM:UI_RED,NT_ALIGN_LEFT);
        rows(g,s,"摄像头切换","静音切换","举手",&tk_meeting_bindings[s->meet_app][1],&tk_meeting_bindings[s->meet_app][0],&tk_meeting_bindings[s->meet_app][2]);
        ui_bar(g,"长按 OK 换软件 · 长按↑ 返回");break;
    }
    case TK_PAGE_MEDIA:
        if(s->media_select){media_choice(g,s);break;}
        if(s->media_mode==1){
            ui_text(g,"抖音 · 键盘方向键",12,53,12,UI_DIM,NT_ALIGN_LEFT);
            ag_rect(g,12,62,216,44,10,UI_PANEL,255,accent,2);ui_text(g,"↑     →     ↓",120,91,18,0xffff,NT_ALIGN_CENTER);
            ui_fit(g,"右方向键可能快进，以App响应为准",120,128,216,12,UI_DIM,NT_ALIGN_CENTER);
            rows(g,s,"上个视频","向右 / 快进","下个视频",NULL,NULL,NULL);remote_bar(g,s,"长↑ 返回媒体选择");break;
        }
        ui_text(g,"音乐遥控",12,52,12,UI_DIM,NT_ALIGN_LEFT);
        ag_circle(g,120,88,30,accent,255,0,0);ui_text(g,"播放",120,94,16,UI_INK,NT_ALIGN_CENTER);
        ag_circle(g,56,88,18,UI_PANEL,255,accent,2);ui_text(g,"−",56,94,16,UI_PAPER,NT_ALIGN_CENTER);
        ag_circle(g,184,88,18,UI_PANEL,255,accent,2);ui_text(g,"+",184,94,16,UI_PAPER,NT_ALIGN_CENTER);
        ui_text(g,"音量",120,132,12,UI_DIM,NT_ALIGN_CENTER);rows(g,s,"音量 +","播放 / 暂停","音量 −",NULL,NULL,NULL);
        remote_bar(g,s,"长OK 下曲 · 长↓ 上曲 · 长↑ 选择");break;
    case TK_PAGE_CAM:{
        static const char *const delays[]={"不延时","3 秒","10 秒"};
        if(s->cam_end>0){
            int seconds=(int)((s->cam_end-now+999)/1000);snprintf(text,sizeof(text),"%d",seconds);
            ui_text(g,"准备拍照",120,85,18,UI_PAPER,NT_ALIGN_CENTER);ag_circle(g,82,165,46,accent,255,0,0);
            ui_text(g,text,82,183,48,UI_INK,NT_ALIGN_CENTER);ui_text(g,"再按 OK 取消",82,234,12,UI_DIM,NT_ALIGN_CENTER);
        }else{
            for(int i=0;i<3;i++){ag_rect(g,12+i*72,53,68,50,10,i==s->cam_delay?accent:UI_PANEL,255,0,0);ui_text(g,delays[i],46+i*72,84,16,i==s->cam_delay?UI_INK:UI_PAPER,NT_ALIGN_CENTER);}
            snprintf(text,sizeof(text),"已拍 %d 张 · 先打开手机相机",s->shots);ui_fit(g,text,12,126,216,12,UI_DIM,NT_ALIGN_LEFT);
            rows(g,s,"切换延时","拍照","五连拍",NULL,NULL,NULL);
            if(s->burst_left>0){snprintf(text,sizeof(text),"连拍中 %d / 5",5-s->burst_left);ui_text(g,text,82,280,12,accent,NT_ALIGN_CENTER);}
        }
        ui_bar(g,"↑延时 · OK拍 · ↓连拍 · 长↑返回");break;
    }
    default:break;
    }
    unsigned id=s->page==TK_PAGE_MACRO?TK_AN_MACRO:s->page==TK_PAGE_PPT?TK_AN_PPT:s->page==TK_PAGE_MEET?TK_AN_MEET:s->page==TK_PAGE_MEDIA?TK_AN_MEDIA:TK_AN_CAM;
    ui_nabo(g,a,id,194,286,now);
}
