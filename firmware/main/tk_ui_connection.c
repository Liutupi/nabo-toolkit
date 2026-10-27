#include "tk_ui_internal.h"
#include <stdio.h>
void ui_connections(ag_t *g,const tk_state_t *s,int64_t now,int comparison)
{
    ui_text(g,"最多 3 台，同一时间连一台",12,53,12,UI_DIM,NT_ALIGN_LEFT);
    for(int i=0;i<4;i++){
        int y=62+i*50;bool sel=s->conn_sel==i;uint16_t fg=sel?UI_INK:UI_PAPER;
        ag_rect(g,10,y,220,44,10,sel?UI_GOLD:UI_PANEL,255,sel?UI_INK:0,sel?2:0);ag_rect(g,13,y+8,4,28,0,tk_ui_accents[TK_PAGE_CONN],255,0,0);
        if(i==3){ui_text(g,"+ 配对新设备",24,y+28,16,fg,NT_ALIGN_LEFT);continue;}
        char n[4];snprintf(n,sizeof(n),"%d",i+1);ag_circle(g,30,y+22,11,sel?UI_INK:UI_BG,255,0,0);ui_text(g,n,30,y+27,12,sel?UI_GOLD:UI_PAPER,NT_ALIGN_CENTER);
        if(!s->slots[i].used){ui_text(g,"空位",50,y+28,16,sel?UI_INK:UI_DIM,NT_ALIGN_LEFT);continue;}
        ui_fit(g,s->slots[i].name,50,y+20,100,16,fg,NT_ALIGN_LEFT);ui_text(g,tk_os_names[s->slots[i].os],50,y+36,12,sel?UI_INK:UI_DIM,NT_ALIGN_LEFT);
        bool current=i==s->active;ui_text(g,current?(s->connected?"已连接":"未连接"):"OK 连接",220,y+28,12,current?(s->connected?(sel?UI_INK:UI_GREEN):UI_RED):(sel?UI_INK:UI_DIM),NT_ALIGN_RIGHT);
    }
    ui_bar(g,"长 OK 类型 · 长↓ 删除 · 长↑ 返回");
    if(s->pairing){
        ui_popup(g,156);
        if(s->passkey_valid){
            ui_text(g,comparison?"核对两端数字":"配对码",120,108,18,UI_INK,NT_ALIGN_CENTER);
            char code[12];snprintf(code,sizeof(code),"%03lu %03lu",(unsigned long)(s->passkey/1000),(unsigned long)(s->passkey%1000));
            // Archivo Black digits fit all six without stretching the glyphs.
            ag_text_squeezed(g,&tk_font_48,code,120,165,NT_ALIGN_CENTER,tk_ui_accents[TK_PAGE_CONN],178);
            ui_text(g,comparison==2?"等待对端确认":comparison?"一致才短按工牌 OK":"在对端输入这 6 位数字",120,195,12,UI_INK,NT_ALIGN_CENTER);
            ui_text(g,comparison?"长按↑ 拒绝":"OK 取消 · 长按↑ 返回",120,224,12,UI_DIM,NT_ALIGN_CENTER);
        }else{
            ui_text(g,"配对中",120,108,18,UI_INK,NT_ALIGN_CENTER);char time[24];snprintf(time,sizeof(time),"%lld",(long long)((s->pair_until-now+999)/1000));
            ui_text(g,time,120,163,48,tk_ui_accents[TK_PAGE_CONN],NT_ALIGN_CENTER);
            ui_text(g,"在电脑或手机的蓝牙里选择",120,190,12,UI_INK,NT_ALIGN_CENTER);ui_text(g,"「NABO 工具箱」",120,208,16,UI_INK,NT_ALIGN_CENTER);ui_text(g,"OK 停止配对",120,228,12,UI_DIM,NT_ALIGN_CENTER);
        }
    }
    if(s->confirm_del>=0){ui_popup(g,100);char text[160];snprintf(text,sizeof(text),"删除「%s」？",s->slots[s->confirm_del].name);ui_fit(g,text,120,140,172,16,UI_INK,NT_ALIGN_CENTER);
        ui_text(g,"删除后要在对端重新配对",120,164,12,UI_DIM,NT_ALIGN_CENTER);ui_text(g,"OK 删除 · 其他键取消",120,186,12,UI_RED,NT_ALIGN_CENTER);
    }
}
