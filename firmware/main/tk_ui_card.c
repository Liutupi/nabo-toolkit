#include "tk_ui_internal.h"
#include <stdio.h>
#include <string.h>
void ui_card(tk_ui_t *ui,ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a)
{
    const tk_card_t *card=&s->cards[s->card_idx];
    if(strcmp(ui->qr_text,card->qr) || !ui->qr_revision){
        snprintf(ui->qr_text,sizeof(ui->qr_text),"%s",card->qr);ui->qr_revision++;
        tk_qr_encode(&ui->qr,card->qr);
    }
    if(s->card_zoom){ag_rect(g,0,0,240,320,0,0xffff,255,0,0);
        char title[160];snprintf(title,sizeof(title),"%s · %s",card->title,card->name);ui_fit(g,title,120,298,230,16,UI_INK,NT_ALIGN_CENTER);ui_text(g,"OK 还原",120,318,12,UI_DIM,NT_ALIGN_CENTER);
    }else{
        ag_rect(g,10,40,220,244,12,UI_PAPER,255,0,0);ag_rect(g,13,52,4,220,0,tk_ui_accents[TK_PAGE_CARD],255,0,0);ui_nabo(g,a,TK_AN_AVATAR,52,114,now);
        ag_rect(g,96,54,110,24,8,tk_ui_accents[TK_PAGE_CARD],255,0,0);ui_fit(g,card->title,151,72,102,12,UI_INK,NT_ALIGN_CENTER);
        ui_fit(g,card->name,96,98,118,18,UI_INK,NT_ALIGN_LEFT);ui_fit(g,card->line,96,117,122,12,UI_DIM,NT_ALIGN_LEFT);
        for(int i=0;i<s->card_count;i++)ag_circle(g,110+i*10,276,3,i==s->card_idx?tk_ui_accents[TK_PAGE_CARD]:UI_DIM,255,0,0);
        ui_bar(g,"↑↓ 换名片 · OK 放大 · 长按↑ 返回");
    }
    if(ui->qr.valid){int modules=tk_qr_size(&ui->qr)+8,maximum=s->card_zoom?232:144,scale=maximum/modules;
        if(scale>0)ag_qr(g,ui->qr.modules,(240-modules*scale)/2,s->card_zoom?40:126,scale,4,ui->qr_revision);
    }else ui_text(g,"二维码内容过长",120,200,16,UI_RED,NT_ALIGN_CENTER);
}
