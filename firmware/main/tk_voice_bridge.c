#include "tk_voice_bridge.h"
#include "tk_voice.h"
#include "tk_f1_device.h"
#include "matcher.h"
#include <stdio.h>
#include <string.h>

static bool s_available,s_armed,s_started,s_owns_mute,s_was_muted;
static uint32_t s_token;
static int64_t s_quiet_since,s_prepare_since;

esp_err_t tk_voice_bridge_init(tk_state_t *s)
{
    s_armed=s_started=s_owns_mute=s_was_muted=false;s_token=0;s_quiet_since=-1;s_prepare_since=0;
    esp_err_t error=tk_voice_init();s_available=error==ESP_OK;
    tk_voice_snapshot_t v=tk_voice_snapshot();tk_model_voice_templates(s,v.counts);
    return error;
}
bool tk_voice_bridge_busy(void){return s_armed || tk_voice_active();}

static void restore(bool keep_muted)
{
    if(s_owns_mute){tk_sound_mute(s_was_muted || keep_muted);s_owns_mute=false;}
    s_armed=s_started=false;s_quiet_since=-1;
}
static int outcome(const tk_voice_snapshot_t *v)
{
    if(v->status==TK_VR_ERROR)return v->error_stage==2?6:3;
    if(v->enrolling && v->decision==VP_ACCEPTED)return 0;
    if(v->decision==VP_ACCEPTED)return 1;
    if(v->decision==VP_AMBIGUOUS)return 4;
    if(v->decision==VP_TOO_LONG)return 5;
    return 2;
}
void tk_voice_bridge_tick(tk_state_t *s,int64_t now,bool allowed,bool keep_muted)
{
    tk_voice_snapshot_t v=tk_voice_snapshot();tk_model_voice_templates(s,v.counts);
    bool wanted=allowed && s->page==TK_PAGE_VOICE && s->voice_busy;
    if(!wanted || (s_armed && s->voice_token!=s_token)){
        if(!allowed && s->page==TK_PAGE_VOICE && s->voice_busy)
            tk_model_voice_result(s,s->voice_token,3,-1,0,now);
        if(v.active)tk_voice_cancel();
        else restore(keep_muted);
        return;
    }
    if(!s_available){tk_model_voice_result(s,s->voice_token,3,-1,0,now);return;}
    if(!s_armed){
        s_armed=true;s_started=false;s_token=s->voice_token;s_quiet_since=-1;
        s_prepare_since=now;
        s_was_muted=tk_sound_stats().muted;s_owns_mute=true;tk_sound_mute(true);
    }
    if(!s_started){
        tk_model_voice_progress(s,s_token,8,now);
        if(now-s_prepare_since>=1500){
            tk_model_voice_result(s,s_token,6,-1,0,now);restore(keep_muted);return;
        }
        if(!tk_sound_capture_ready()){s_quiet_since=-1;return;}
        if(s_quiet_since<0)s_quiet_since=now;
        if(now-s_quiet_since<40)return; // Drain the final queued silent PCM block.
        esp_err_t error=s->voice_operation==2 ?
            tk_voice_request_enroll((unsigned)s->voice_selected,s_token):tk_voice_request_recognize(s_token);
        if(error){tk_model_voice_result(s,s_token,3,-1,0,now);restore(keep_muted);return;}
        s_started=true;return;
    }
    if(v.token!=s_token)return;
    if(v.status==TK_VR_CALIBRATING || v.status==TK_VR_STARTING)
        tk_model_voice_progress(s,s_token,8,now);
    else if(v.status==TK_VR_LISTENING)
        tk_model_voice_progress(s,s_token,v.enrolling?2:1,now);
    else if(!v.active && (v.status==TK_VR_COMPLETE || v.status==TK_VR_ERROR || v.status==TK_VR_CANCELLED)){
        unsigned count=v.word>=0 && v.word<TK_VR_WORDS ? v.counts[v.word]:0;
        tk_model_voice_result(s,s_token,outcome(&v),v.word,(int)count,now);restore(keep_muted);
    }
}
static void inject(tk_state_t *s,tk_key_t key,int64_t now,tk_effects_t *scratch)
{
    tk_model_press(s,key,now,scratch);
    // The only allowed pages here are menu/voice. No HID effects are dispatched.
}
bool tk_voice_bridge_command(tk_state_t *s,const char *text,int64_t now,bool allowed,tk_effects_t *scratch)
{
    if(strncmp(text,">tk.voice.",10))return false;
    if(!strcmp(text,">tk.voice.compact")){
        if(!allowed || s->voice_busy || tk_voice_bridge_busy() || (s->page!=TK_PAGE_MENU && s->page!=TK_PAGE_VOICE))
            puts("@voice compact unavailable");
        else printf("@voice compact_result=%d\n",tk_voice_compact_legacy());
        return true;
    }
    if(!strcmp(text,">tk.voice.status")){
        tk_voice_snapshot_t v=tk_voice_snapshot();
        printf("@voice {\"available\":%s,\"generation\":%u,\"token\":%u,\"status\":%d,\"active\":%s,\"enrolling\":%s,\"word\":%d,\"example\":%d,\"counts\":[%u,%u,%u,%u,%u,%u,%u],\"invalid_mask\":%u,\"decision\":%d,\"distance\":%u,\"runner\":%u,\"frames\":%u,\"error\":%d,\"error_stage\":%d,\"storage_write_error\":%d,\"storage_read_error\":%d,\"storage_unknown\":%s,\"heap\":%u,\"largest\":%u,\"peak\":%u,\"frame_max_us\":%u,\"threshold\":%u,\"stack_min_bytes\":%u,\"heap_integrity\":%s}\n",
               s_available?"true":"false",(unsigned)v.generation,(unsigned)v.token,v.status,v.active?"true":"false",v.enrolling?"true":"false",v.word,v.example,
               v.counts[0],v.counts[1],v.counts[2],v.counts[3],v.counts[4],v.counts[5],v.counts[6],(unsigned)v.invalid_mask,v.decision,v.distance,v.runner_up_distance,v.frames,v.error,v.error_stage,
               v.storage_write_error,v.storage_read_error,v.storage_unknown?"true":"false",
               (unsigned)v.heap,(unsigned)v.largest,(unsigned)v.peak,(unsigned)v.frame_max_us,(unsigned)v.threshold,(unsigned)v.stack_low_watermark,v.heap_integrity?"true":"false");
        return true;
    }
    if(!strcmp(text,">tk.voice.cancel")){
        if(s->page==TK_PAGE_VOICE)inject(s,TK_LONG_UP,now,scratch);
        tk_voice_cancel();return true;
    }
    bool enroll=!strncmp(text,">tk.voice.enroll=",17) && text[17]>='0' && text[17]<='6' && !text[18];
    bool open=!strcmp(text,">tk.voice.open"),listen=!strcmp(text,">tk.voice.listen");
    if(!enroll && !open && !listen){puts("@voice invalid command");return true;}
    if(!allowed){puts("@voice unavailable in current diagnostic mode");return true;}
    if(s->page==TK_PAGE_MENU && !s->pairing && !s->os_pick && s->confirm_del<0)inject(s,TK_LONG_OK,now,scratch);
    if(s->page!=TK_PAGE_VOICE || s->voice_busy){puts("@voice unavailable on current page");return true;}
    if(open)return true;
    if(listen){inject(s,TK_OK,now,scratch);return true;}
    if(enroll){
        unsigned target=(unsigned)(text[17]-'0');
        for(unsigned i=0;i<TK_VR_WORDS && s->voice_selected!=(int)target;i++)inject(s,TK_DOWN,now,scratch);
        inject(s,TK_LONG_OK,now,scratch);return true;
    }
    puts("@voice invalid command");return true;
}
