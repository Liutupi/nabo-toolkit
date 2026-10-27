#include "tk_hid_map.h"
#include <stdio.h>
#include <string.h>
#include "tk_hid_data.inc"

const tk_packet_t *tk_hid_resolve(const tk_binding_t *b, tk_os_t os)
{
    if (!b || os < TK_OS_MAC || os > TK_OS_ANDROID) return NULL;
    const tk_packet_t *p = &b->family[os == TK_OS_MAC || os == TK_OS_IOS ? 0 : 1];
    return p->kind ? p : NULL;
}
void tk_hid_key_name(unsigned u, char *out, size_t size)
{
    if (!size) return;
    if (u >= 4 && u <= 0x1d) snprintf(out,size,"%c",'A'+u-4);
    else if (u >= 0x1e && u <= 0x26) snprintf(out,size,"%u",u-0x1d);
    else if (u == 0x27) snprintf(out,size,"0");
    else if (u >= 0x3a && u <= 0x45) snprintf(out,size,"F%u",u-0x39);
    else if (u >= 0x68 && u <= 0x73) snprintf(out,size,"F%u",u-0x68+13);
    else {
        const char *name = NULL;
        switch (u) {
        case 0x28:name="Enter";break;case 0x29:name="Esc";break;case 0x2a:name="Backspace";break;
        case 0x2b:name="Tab";break;case 0x2c:name="Space";break;case 0x2f:name="[";break;case 0x30:name="]";break;
        case 0x46:name="PrtSc";break;case 0x4b:name="PgUp";break;case 0x4c:name="Del";break;case 0x4e:name="PgDn";break;
        case 0x4f:name="→";break;case 0x50:name="←";break;case 0x51:name="↓";break;case 0x52:name="↑";break;
        }
        if (name) snprintf(out,size,"%s",name); else snprintf(out,size,"%02x",u);
    }
}
static void part(char *out, size_t size, const char *s)
{
    size_t used = strlen(out);
    if (used < size) snprintf(out+used,size-used,"%s%s",used?"+":"",s);
}
void tk_hid_chord(const tk_packet_t *p, tk_os_t os, char *out, size_t size)
{
    if (!size) return;
    out[0]=0;
    if (!p) return;
    if (p->kind == TK_PACKET_MEDIA) {
        const char *s="MEDIA";
        switch(p->usage) {case 0xcd:s="播放/暂停";break;case 0xb5:s="下一曲";break;case 0xb6:s="上一曲";break;case 0xe9:s="音量+";break;case 0xea:s="音量−";break;}
        snprintf(out,size,"%s",s);return;
    }
    if (p->kind == TK_PACKET_TEXT) {const char *s=p->text?p->text:"";snprintf(out,size,strlen(s)>10?"输入 \"%.9s…\"":"输入 \"%s\"",s);return;}
    bool apple=os==TK_OS_MAC || os==TK_OS_IOS;
    static const unsigned bits[]={1,16,4,64,2,32,8,128};
    const char *names[]={"Ctrl","右Ctrl",apple?"Option":"Alt",apple?"右Option":"右Alt","Shift","右Shift",apple?"Cmd":"Win",apple?"右Cmd":"右Win"};
    for (int i=0;i<8;i++) if ((unsigned)p->mod & bits[i]) part(out,size,names[i]);
    if (p->usage) {char name[20];tk_hid_key_name(p->usage,name,sizeof(name));part(out,size,name);}
}
bool tk_hid_char(unsigned char ch, tk_packet_t *p)
{
    *p=(tk_packet_t){.kind=TK_PACKET_KEY};
    if (ch>='a' && ch<='z') p->usage=4+ch-'a';
    else if (ch>='A' && ch<='Z') {p->usage=4+ch-'A';p->mod=2;}
    else if (ch>='1' && ch<='9') p->usage=0x1e + ch-'1';
    else if (ch=='0') p->usage=0x27;
    else {
        const char *lo="-=[]\\;'`,./",*hi="_+{}|:\"~<>?",*digits="!@#$%^&*()";
        const char *at=strchr(lo,ch);
        if (at && ch) {static const int codes[]={0x2d,0x2e,0x2f,0x30,0x31,0x33,0x34,0x35,0x36,0x37,0x38};p->usage=codes[at-lo];}
        else if ((at=strchr(hi,ch)) && ch) {static const int codes[]={0x2d,0x2e,0x2f,0x30,0x31,0x33,0x34,0x35,0x36,0x37,0x38};p->usage=codes[at-hi];p->mod=2;}
        else if ((at=strchr(digits,ch)) && ch) {p->usage=at-digits==9?0x27:0x1e + (int)(at-digits);p->mod=2;}
        else if(ch==' ')p->usage=0x2c;
        else if(ch=='\n')p->usage=0x28;
        else return false;
    }
    return true;
}
unsigned tk_hid_report(const tk_packet_t *p, uint8_t out[8])
{
    memset(out,0,8);
    if (!p) return 0;
    if (p->kind==TK_PACKET_MEDIA) {out[0]=p->usage;out[1]=p->usage>>8;return 2;}
    if (p->kind!=TK_PACKET_KEY) return 0;
    out[0]=p->mod;out[2]=p->usage;return 8;
}
