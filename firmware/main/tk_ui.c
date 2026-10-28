#include "tk_ui_internal.h"
#include <stdio.h>
#include <string.h>

const uint16_t tk_ui_accents[11]={UI_GOLD,UI_GOLD,0xfe69,0xf467,0x4e11,0x9bdd,0x4d1e,0xf476,0x4e19,0xc639,UI_GOLD};
static const char *const titles[]={"NABO 工具箱","NABO 工具箱","快捷键","PPT翻页","会议","媒体","拍照","名片","连接","设置","语音查找"};
static const lv_font_t *font(int n){return n==12?&tk_font_12:n==18?&tk_font_18:n==28?&tk_font_28:n==48?&tk_font_48:&tk_font_16;}
void ui_text(ag_t *g,const char *s,int x,int y,int size,uint16_t color,nt_align_t align){ag_text(g,font(size),s,x,y,align,color);}
void ui_fit(ag_t *g,const char *s,int x,int y,int width,int size,uint16_t color,nt_align_t align)
{
    char text[300];snprintf(text,sizeof(text),"%s",s);
    if(ag_text_width(font(size),text)>width){
        size_t n=strlen(text);
        while(n){
            n--;while(n && ((unsigned char)text[n]&0xc0)==0x80)n--;text[n]=0;
            if(n+4>sizeof(text))continue;
            char candidate[304];snprintf(candidate,sizeof(candidate),"%s…",text);
            if(ag_text_width(font(size),candidate)<=width){memcpy(text,candidate,strlen(candidate)+1);break;}
        }
    }
    ui_text(g,text,x,y,size,color,align);
}
void ui_bar(ag_t *g,const char *s){ag_rect(g,0,290,240,30,0,UI_INK,255,0,0);ui_fit(g,s,120,309,226,12,UI_PAPER,NT_ALIGN_CENTER);}
void ui_popup(ag_t *g,int h){ag_rect(g,0,0,240,320,0,UI_INK,153,0,0);ag_rect(g,24,156-h/2,192,h,14,UI_PAPER,255,UI_INK,2);}
void ui_picture(ag_t *g,const tk_picture_t *p,int x,int y){if(p && p->pixels)ag_bitmap_alpha(g,p->pixels,p->alpha,x,y,p->w,p->h);}
static void top(ag_t *g,const tk_state_t *s,int64_t now,bool unavailable)
{
    ag_rect(g,0,0,240,32,0,UI_INK,255,0,0);ui_fit(g,titles[s->page],10,23,124,16,UI_PAPER,NT_ALIGN_LEFT);
    char status[128];uint16_t color=UI_RED;
    if(unavailable)snprintf(status,sizeof(status),"蓝牙不可用");
    else if(s->pairing){snprintf(status,sizeof(status),"配对中 %llds",(long long)((s->pair_until-now+999)/1000));color=UI_GOLD;}
    else if(s->connected && s->slots[s->active].used){snprintf(status,sizeof(status),"%s",s->slots[s->active].name);color=UI_GREEN;}
    else snprintf(status,sizeof(status),"未连接");
    ag_circle(g,139,17,3,color,255,0,0);ui_fit(g,status,148,22,84,12,color,NT_ALIGN_LEFT);
    for(int x=0;x<240;x+=8)ag_rect(g,x,32,8,4,0,(x/8)&1?tk_ui_accents[s->page]:UI_INK,255,0,0);
}
static void menu(ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a)
{
    static const char *const names[]={"快捷键","PPT翻页","会议","媒体","拍照","名片","连接","设置"};
    static const char *const sub[]={"一键搞定","演讲计时","静音举手","音乐抖音","远程快门","扫码分享","设备切换","按你习惯"};
    ag_rect(g,0,36,240,68,0,UI_PANEL,255,0,0);ui_nabo(g,a,TK_AN_AVATAR,42,102,now);
    ag_rect(g,84,44,148,50,10,UI_PAPER,255,0,0);ui_text(g,"今天遥控什么？",94,66,16,UI_INK,NT_ALIGN_LEFT);
    char line[160];
    if(s->connected && s->slots[s->active].used)snprintf(line,sizeof(line),"已连 %s · %s",s->slots[s->active].name,tk_os_names[tk_model_os(s)]);
    else snprintf(line,sizeof(line),"还没连接设备");
    ui_fit(g,line,94,85,130,12,s->connected?UI_DIM:UI_RED,NT_ALIGN_LEFT);
    for(int i=0;i<8;i++){
        int x=(i%2)?124:8,y=110+(i/2)*44;bool selected=s->menu==i;uint16_t fg=selected?UI_INK:UI_PAPER;
        ag_rect(g,x,y,108,40,10,selected?UI_GOLD:UI_PAPER,255,selected?UI_INK:0,selected?2:0);
        ag_rect(g,x+3,y+8,4,24,0,tk_ui_accents[i+2],255,0,0);ag_circle(g,x+20,y+20,12,tk_ui_accents[i+2],255,0,0);
        ui_icon(g,i,x+20,y+20,UI_INK);
        ui_fit(g,names[i],x+38,y+19,64,16,UI_INK,NT_ALIGN_LEFT);ui_fit(g,sub[i],x+38,y+34,64,12,selected?fg:UI_DIM,NT_ALIGN_LEFT);
    }
    ui_bar(g,"↑↓ 选择 · OK 进入 · 长OK 语音");
}
static void voice(ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a)
{
    static const char *const states[]={"准备","请说口令","请说目标名称","已保存","未识别","操作失败","尚未录入","未找到分组","准备采音","歧义","口令太长","采音失败"};
    const int sel=s->voice_selected>=0 && s->voice_selected<TK_VOICE_TARGETS?s->voice_selected:0;
    const int status=s->voice_status>=0 && s->voice_status<12?s->voice_status:5;
    ag_rect(g,0,36,240,68,0,UI_PANEL,255,0,0);ui_nabo(g,a,TK_AN_AVATAR,42,102,s->voice_busy?0:now);
    ui_text(g,"本人录入",84,64,16,UI_PAPER,NT_ALIGN_LEFT);
    ui_fit(g,"按需聆听 · 不持续唤醒",84,85,148,12,UI_DIM,NT_ALIGN_LEFT);
    for(int i=0;i<TK_VOICE_TARGETS;i++){
        const int x=i%2?124:10,y=110+i/2*26;const bool selected=i==sel;
        const uint16_t fg=selected?UI_INK:UI_PAPER;
        ag_rect(g,x,y,106,24,6,selected?UI_GOLD:UI_PANEL,255,selected?UI_INK:0,selected?2:0);
        ui_text(g,tk_voice_names[i],x+10,y+18,16,fg,NT_ALIGN_LEFT);
        char count[12];snprintf(count,sizeof(count),"%d/3",s->voice_counts[i]);
        ui_text(g,count,x+96,y+18,12,selected?UI_INK:UI_DIM,NT_ALIGN_RIGHT);
    }
    const bool error=status==4 || status==5 || status==7 || status>=9;
    ag_rect(g,10,222,220,60,10,UI_PANEL,255,error?UI_RED:0,error?1:0);
    ui_fit(g,states[status],120,245,200,16,error?UI_RED:status==3?UI_GREEN:UI_PAPER,NT_ALIGN_CENTER);
    const char *hint=sel==6?"只进Typeless · 再按键":"长OK 为每个口令录入3次";
    if(status==1)hint="已录入口令任选一个";
    else if(status==2)hint="自然说一次所选名称";
    else if(status==3)hint=s->voice_counts[sel]<3?"长OK 继续录入":"OK 识别 · 长OK 重新录入";
    else if(status==4 || status==9)hint="请短OK 后再说一次";
    else if(status==5 || status==11)hint="请稍后重试";
    else if(status==6)hint="长OK 录入所选口令";
    else if(status==7)hint="配置页中恢复目标分组";
    else if(status==8)hint="请保持安静，稍后再说";
    else if(status==10)hint="请只说目标名称";
    ui_fit(g,hint,120,266,204,12,UI_DIM,NT_ALIGN_CENTER);
    ag_rect(g,0,290,240,30,0,UI_INK,255,0,0);
    ui_fit(g,s->voice_busy?"采音中 · 请稍候":"↑↓ 选择 · OK 识别 · 长OK 录入",120,301,228,12,UI_PAPER,NT_ALIGN_CENTER);
    ui_text(g,"长↑ 返回",120,315,12,UI_PAPER,NT_ALIGN_CENTER);
}
static void settings(ag_t *g,const tk_state_t *s)
{
    static const char *const names[]={"按键提示音","开机语音","演讲时长","自动休眠","息屏遥控","关于"};
    static const char *const hints[]={"演讲翻页时始终不响","那波，陪你遥控万物！","PPT 计时的目标时长","计时、倒数、配对时不休眠","短键照常发送 · 长OK只亮屏","离线 · 蓝牙键盘 · 不联网"};
    static const int talk[]={5,10,15,20,30,45,60},sleep[]={5,15,30,0};
    char values[6][64];snprintf(values[0],64,"%s",s->beep?"开":"关");snprintf(values[1],64,"%s",s->voice?"开":"关");
    snprintf(values[2],64,"%d 分钟",talk[s->talk]);if(sleep[s->sleep])snprintf(values[3],64,"%d 分钟",sleep[s->sleep]);else snprintf(values[3],64,"连接时不休眠");
    snprintf(values[4],64,"%s",s->remote_dim?"开":"关");snprintf(values[5],64,"工具箱开发版");
    for(int i=0;i<6;i++){int y=42+i*36;bool sel=s->set_sel==i;ag_rect(g,10,y,220,32,8,sel?UI_GOLD:UI_PANEL,255,sel?UI_INK:0,sel?2:0);ui_text(g,names[i],20,y+22,16,sel?UI_INK:UI_PAPER,NT_ALIGN_LEFT);ui_fit(g,values[i],220,y+22,116,16,sel?UI_INK:UI_DIM,NT_ALIGN_RIGHT);}
    const char *hint=s->set_sel==4 && !s->remote_dim?"遥控时保持亮屏":hints[s->set_sel];
    ui_fit(g,hint,120,275,224,12,UI_DIM,NT_ALIGN_CENTER);ui_bar(g,"↑↓ 选择 · OK 修改 · 长按↑ 返回");
}
void tk_ui_frame(tk_ui_t *ui,ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a,int comparison)
{
    if(s->screen_off){ag_begin(g,44);ag_rect(g,0,0,240,320,0,0,255,0,0);return;}
    ag_begin(g,s->page*4+(s->card_zoom?1:0));ag_rect(g,0,0,240,320,0,UI_BG,255,0,0);
    if(s->page==TK_PAGE_BOOT)ui_boot(g,s,now,a);
    else{
        top(g,s,now,ui->ble_unavailable);
        if(s->page==TK_PAGE_MENU)menu(g,s,now,a);
        else if(s->page==TK_PAGE_VOICE)voice(g,s,now,a);
        else if(s->page==TK_PAGE_SET)settings(g,s);
        else if(s->page==TK_PAGE_CONN)ui_connections(g,s,now,comparison);
        else if(s->page==TK_PAGE_CARD)ui_card(ui,g,s,now,a);
        else ui_tools(g,s,now,a);
    }
    if(s->toast){bool tool=s->page>=TK_PAGE_MACRO && s->page<=TK_PAGE_CAM;int width=tool?138:224;
        ag_rect(g,8,256,width,26,8,s->toast_error?UI_RED:UI_PANEL,255,0,0);
        ui_fit(g,s->toast_text,14,274,width-12,12,UI_PAPER,NT_ALIGN_LEFT);
    }
    if(s->os_pick){ui_popup(g,200);ui_text(g,"这是什么设备？",120,88,16,UI_INK,NT_ALIGN_CENTER);
        for(int i=0;i<4;i++){bool sel=s->os_sel==i;ag_rect(g,40,100+i*32,160,30,8,sel?UI_GOLD:UI_PAPER,255,0,0);ui_text(g,tk_os_names[i],120,121+i*32,16,UI_INK,NT_ALIGN_CENTER);}
        ui_text(g,"↑↓ 选择 · OK 确定",120,246,12,UI_DIM,NT_ALIGN_CENTER);
    }
}
