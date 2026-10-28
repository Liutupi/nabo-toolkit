#include "tk_voice.h"
#include "tk_f1_device.h"
#include <string.h>

static tk_voice_snapshot_t value;
static bool muted,ready;
static unsigned requested,cancelled,compacted;

esp_err_t tk_voice_init(void)
{
    memset(&value,0,sizeof(value));value.word=-1;value.heap_integrity=true;muted=false;ready=true;requested=cancelled=compacted=0;return ESP_OK;
}
static esp_err_t request(bool enroll,int word,uint32_t token)
{
    requested++;value.active=true;value.enrolling=enroll;value.word=word;
    value.token=token;value.generation++;value.status=TK_VR_STARTING;return ESP_OK;
}
esp_err_t tk_voice_request_enroll(unsigned word,uint32_t token){return request(true,(int)word,token);}
esp_err_t tk_voice_request_recognize(uint32_t token){return request(false,-1,token);}
void tk_voice_cancel(void){cancelled++;}
bool tk_voice_active(void){return value.active;}
tk_voice_snapshot_t tk_voice_snapshot(void){return value;}
bool tk_voice_prepare_sleep(void){return !value.active;}
void tk_sound_mute(bool v){muted=v;}
bool tk_sound_capture_ready(void){return muted && ready;}
tk_sound_stats_t tk_sound_stats(void){return (tk_sound_stats_t){.muted=muted};}
void vb_ready(bool v){ready=v;}
bool vb_muted(void){return muted;}
unsigned vb_requested(void){return requested;}
unsigned vb_cancelled(void){return cancelled;}
esp_err_t tk_voice_compact_legacy(void){compacted++;return ESP_OK;}
unsigned vb_compacted(void){return compacted;}
void vb_count(unsigned word,unsigned n){value.counts[word]=(uint8_t)n;}
void vb_phase(int phase){value.status=phase;}
void vb_finish(int decision,int word,int error_stage,unsigned count)
{
    value.active=false;value.decision=decision;value.word=word;value.error_stage=error_stage;
    value.status=error_stage?TK_VR_ERROR:TK_VR_COMPLETE;
    if(!error_stage && word>=0 && word<TK_VR_WORDS)value.counts[word]=(uint8_t)count;
}
