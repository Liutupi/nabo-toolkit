#include "tk_voice_capture.h"
#include <string.h>

void tk_voice_capture_init(tk_voice_capture_t *c,uint32_t now,bool enrolling)
{
    memset(c,0,sizeof(*c));c->start_ms=now;c->decision=VP_NO_SPEECH;
    c->max_frames=enrolling?VP_MAX_TEMPLATE_FRAMES:VP_MAX_QUERY_FRAMES;
    c->min_frames=enrolling?15:VP_MIN_SPEECH_FRAMES;
}
bool tk_voice_capture_feed(tk_voice_capture_t *c,uint32_t level,uint32_t now)
{
    if(c->done)return false;
    if(now-c->start_ms>=3000){c->done=true;c->decision=c->started?VP_TOO_LONG:VP_NO_SPEECH;return false;}
    if(!c->calibrated){
        if(level>65535)level=65535;
        if(c->cal_frames<15){c->noise_sum+=level;c->cal_frames++;}
        if(c->cal_frames>=15 && now-c->start_ms>=300){
            c->threshold=(c->noise_sum/c->cal_frames)*3+32;
            if(c->threshold<128)c->threshold=128;
            c->calibrated=true;
        }
        return false;
    }
    if(level>=c->threshold){
        c->started=true;c->silent=0;
        if(c->frames>=c->max_frames){c->done=true;c->decision=VP_TOO_LONG;return false;}
        c->frames++;return true;
    }
    if(c->started && ++c->silent>=15){c->done=true;c->decision=c->frames<c->min_frames?VP_TOO_SHORT:VP_ACCEPTED;}
    return false;
}
