#include "tk_animation.h"
#include <stdlib.h>
void *tk_anim_new(void){tk_animation_t *a=malloc(sizeof(*a));if(a)tk_animation_init(a);return a;}
void tk_anim_free(void *a){free(a);}
bool tk_anim_frame(void *a,const uint8_t *data,size_t bytes,unsigned id,uint64_t elapsed)
{
    tk_animation_bank_t b={data,bytes};return tk_animation_frame(a,&b,id,elapsed);
}
const uint8_t *tk_anim_pixels(void *a){return ((tk_animation_t *)a)->pixels;}
unsigned tk_anim_width(void *a){return ((tk_animation_t *)a)->width;}
unsigned tk_anim_height(void *a){return ((tk_animation_t *)a)->height;}
unsigned tk_anim_memory(void){return sizeof(tk_animation_t);}
