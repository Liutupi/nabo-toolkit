#include "tk_qr.h"
#include "qrcodegen.h"
#include <stdlib.h>
#include <string.h>
bool tk_qr_encode(tk_qr_t *q,const char *text)
{
    q->valid=false;
    if(!text || strlen(text)>511)return false;
    uint8_t *scratch=malloc(TK_QR_BYTES);
    if(!scratch)return false;
    q->valid=qrcodegen_encodeText(text,scratch,q->modules,qrcodegen_Ecc_MEDIUM,1,10,qrcodegen_Mask_AUTO,true);
    free(scratch);return q->valid;
}
int tk_qr_size(const tk_qr_t *q){return q->valid?qrcodegen_getSize(q->modules):0;}
bool tk_qr_dark(const tk_qr_t *q,int x,int y){return q->valid && qrcodegen_getModule(q->modules,x,y);}
