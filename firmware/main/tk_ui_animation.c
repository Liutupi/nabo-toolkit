#include "tk_ui_internal.h"
void ui_nabo(ag_t *g,const tk_ui_assets_t *a,unsigned id,int cx,int bottom,int64_t elapsed)
{
#ifdef TK_F3
    if(a->animation && a->bank){
        if(tk_animation_frame(a->animation,a->bank,id,elapsed<0?0:(uint64_t)elapsed)){
            tk_animation_t *p=a->animation;
            ag_indexed(g,p->pixels,p->palette,cx-(int)p->width/2,bottom-(int)p->height,p->width,p->height,p->crc^(id<<24));
        }else g->overflow=true;
        return;
    }
#else
    (void)elapsed;
#endif
    const tk_picture_t *p=id==TK_AN_AVATAR?&a->avatar:id==TK_AN_WELCOME?&a->welcome:&a->bust;
    ui_picture(g,p,cx-p->w/2,bottom-p->h);
}
void ui_icon(ag_t *g,unsigned id,int x,int y,uint16_t c)
{
    switch(id){
    case 0: // keyboard
        ag_rect(g,x-9,y-6,18,12,2,c,255,0,0);
        for(int i=0;i<4;i++)ag_rect(g,x-6+i*4,y-3,2,2,0,UI_PANEL,255,0,0);
        ag_rect(g,x-5,y+2,10,2,0,UI_PANEL,255,0,0);break;
    case 1: // presentation board
        ag_rect(g,x-9,y-8,18,12,1,c,255,0,0);ag_rect(g,x-1,y+4,2,6,0,c,255,0,0);
        ag_rect(g,x-6,y+9,12,2,0,c,255,0,0);break;
    case 2: // meeting microphone
        ag_rect(g,x-3,y-9,6,12,3,c,255,0,0);ag_rect(g,x-7,y,14,7,4,UI_PANEL,255,c,2);
        ag_rect(g,x-1,y+6,2,4,0,c,255,0,0);break;
    case 3: // music note
        ag_rect(g,x+3,y-9,3,15,0,c,255,0,0);ag_rect(g,x-4,y-9,10,3,0,c,255,0,0);
        ag_circle(g,x,y+6,5,c,255,0,0);break;
    case 4: // camera
        ag_rect(g,x-9,y-5,18,13,2,c,255,0,0);ag_rect(g,x-5,y-8,8,3,1,c,255,0,0);
        ag_circle(g,x,y+1,4,UI_PANEL,255,0,0);break;
    case 5: // card
        ag_rect(g,x-9,y-7,18,14,2,c,255,0,0);ag_circle(g,x-4,y-1,3,UI_PANEL,255,0,0);
        ag_rect(g,x+1,y-3,5,2,0,UI_PANEL,255,0,0);ag_rect(g,x+1,y+1,5,2,0,UI_PANEL,255,0,0);break;
    case 6: // connection signal
        ag_circle(g,x,y+6,2,c,255,0,0);ag_circle(g,x,y,6,UI_PANEL,255,c,2);
        ag_rect(g,x-8,y+2,16,2,0,UI_PANEL,255,0,0);break;
    default: // settings
        ag_circle(g,x,y,9,c,255,0,0);ag_circle(g,x,y,4,UI_PANEL,255,0,0);break;
    }
}
static int ease(int t,int duration,int distance)
{
    if(t<=0)return 0;
    if(t>=duration)return distance;
    int r=duration-t;return distance-(int)((int64_t)distance*r*r*r/duration/duration/duration);
}
void ui_boot(ag_t *g,const tk_state_t *s,int64_t now,const tk_ui_assets_t *a)
{
    int t=(int)(now-s->boot_start);
#ifdef TK_F3
    if(t>0){
        ag_circle(g,120,178,t<150?5*t/150:5,tk_ui_accents[8],255,0,0);
        for(int k=0;k<3;k++){
            int local=t<400?t-k*100:(t-400-k*400)%1200;
            int duration=t<400?300:1200;
            if(local>0 && local<duration){
                uint16_t color=nt_blend565(UI_BG,tk_ui_accents[8],(duration-local)*(t<400?230:90)/duration);
                ag_circle(g,120,178,8+94*local/duration,0,0,color,2);
            }
        }
    }
    static const int points[8][2]={{120,104},{172,126},{194,178},{172,230},{120,252},{68,230},{46,178},{68,126}};
    for(int i=0;i<8;i++)if(t>400+i*60){
        int radius=ease(t-400-i*60,180,15);bool flash=t>=2200 && t<2350;
        ag_circle(g,points[i][0],points[i][1],radius,flash?0xffff:tk_ui_accents[i+2],255,UI_INK,2);
        if(radius==15)ui_icon(g,i,points[i][0],points[i][1],UI_INK);
    }
    if(t>700){int y=-10+ease(t-700,350,52);ui_text(g,"NABO",112,y,28,0xffff,NT_ALIGN_RIGHT);ui_text(g,"工具箱",118,y-2,18,UI_GOLD,NT_ALIGN_LEFT);}
    if(t>1050)ui_text(g,"陪你遥控万物",120,74,16,UI_PAPER,NT_ALIGN_CENTER);
#else
    ui_text(g,"NABO 工具箱",120,43,18,UI_PAPER,NT_ALIGN_CENTER);ui_text(g,"陪你遥控万物",120,72,16,UI_GOLD,NT_ALIGN_CENTER);
#endif
    ui_text(g,"按任意键跳过",120,314,12,UI_DIM,NT_ALIGN_CENTER);
    if(t>=1400)ui_nabo(g,a,TK_AN_WELCOME,120,470-ease(t-1400,300,150),t-1400);
}
