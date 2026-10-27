#include "tk_audio_mix.h"
#include <string.h>
void tk_audio_mix_init(tk_audio_mix_t *m,const uint8_t *pcm,size_t bytes)
{
    memset(m,0,sizeof(*m));m->pcm=pcm;m->frames=bytes/2;m->position=m->frames;
}
void tk_audio_mix_voice(tk_audio_mix_t *m,bool play){m->position=play?0:m->frames;}
void tk_audio_mix_tone(tk_audio_mix_t *m,unsigned frequency,unsigned ms)
{
    m->phase=0;m->step=(uint32_t)(((uint64_t)frequency<<24)/16000);m->tone_left=m->tone_total=ms*16;
}
bool tk_audio_mix_fill(tk_audio_mix_t *m,int16_t *out,size_t frames)
{
    bool active=m->position<m->frames || m->tone_left;
    for(size_t i=0;i<frames;i++){
        bool voice=m->pcm && m->position<m->frames;int32_t value=0;
        if(voice){const uint8_t *p=m->pcm+m->position++*2;value=(int16_t)(p[0]|(unsigned)p[1]<<8);}
        if(m->tone_left){
            m->phase=(m->phase+m->step)&0xffffff;int tone=(int)(m->phase>>12);tone=tone<2048?tone:4095-tone;
            // Five ms at either edge: first/last sample zero, no waveform step.
            unsigned attack=m->tone_total-m->tone_left,release=m->tone_left-1;
            unsigned gain=attack<80?attack:80;if(release<gain)gain=release;
            value+=(tone-1024)*2*(int)gain/80/(voice?4:1);m->tone_left--;
        }
        out[i]=(int16_t)(value>32767?32767:value< -32768?-32768:value);
    }return active;
}
