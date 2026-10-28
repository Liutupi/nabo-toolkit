// On-demand, speaker-enrolled local navigation prototype. No network or HID.
#include "tk_voice.h"
#include "tk_voice_capture.h"
#include "tk_voice_store.h"
#include "features.h"
#include "matcher.h"
#include "bsp_audio.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "nvs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

typedef struct {uint32_t generation,token;unsigned word;bool enrolling;} request_t;
typedef struct {
    vp_bank_t bank;
    vp_features_t features;
    int16_t pcm[VP_PCM_SAMPLES];
    uint8_t next[VP_MAX_WORDS];
} workspace_t;
typedef union {
    vp_matcher_t matcher;
    vp_frame_t enrollment[VP_MAX_TEMPLATE_FRAMES];
} operation_t;
_Static_assert(TK_VOICE_STORE_SCRATCH_BYTES<=sizeof(vp_features_t),"reuse frontend memory for expected/readback records");
_Static_assert(sizeof(workspace_t)+sizeof(operation_t)<20u*1024u,"voice job workspace budget");
_Static_assert((int)TK_VR_WORDS==(int)VP_MAX_WORDS,"runtime and matcher word count");
_Static_assert(offsetof(tk_voice_snapshot_t,counts)%4==0,"count snapshot word alignment");
#define MIN_FREE (60u*1024u)
#define MIN_BLOCK (30u*1024u)
#define STORAGE_RESERVE 4096u
static QueueHandle_t s_queue;
static atomic_bool s_active,s_cancel,s_initialized;
static atomic_uint s_generation;
static portMUX_TYPE s_mux=portMUX_INITIALIZER_UNLOCKED;
static tk_voice_snapshot_t s_state={.word=-1,.example=-1};
static uint8_t s_unknown;
static uint32_t now_ms(void){return (uint32_t)(esp_timer_get_time()/1000);}
static void publish(const tk_voice_snapshot_t *state)
{
    portENTER_CRITICAL(&s_mux);s_state=*state;portEXIT_CRITICAL(&s_mux);
}
tk_voice_snapshot_t tk_voice_snapshot(void)
{
    tk_voice_snapshot_t state;portENTER_CRITICAL(&s_mux);state=s_state;portEXIT_CRITICAL(&s_mux);return state;
}
bool tk_voice_active(void){return atomic_load(&s_active);}
void tk_voice_cancel(void){atomic_store(&s_cancel,true);}
bool tk_voice_prepare_sleep(void){tk_voice_cancel();return !tk_voice_active();}
static unsigned count_word(const vp_template_t word[VP_EXAMPLES_PER_WORD])
{
    unsigned count=0;for(unsigned e=0;e<VP_EXAMPLES_PER_WORD;e++)if(word[e].count)count++;return count;
}
static void memory_sample(tk_voice_snapshot_t *state)
{
    uint32_t heap=esp_get_free_heap_size(),largest=heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    if(!state->heap || heap<state->heap)state->heap=heap;
    if(!state->largest || largest<state->largest)state->largest=largest;
}
static void worker_diagnostics(tk_voice_snapshot_t *state)
{
    uint32_t remaining=(uint32_t)uxTaskGetStackHighWaterMark(NULL);
    if(!state->stack_low_watermark || remaining<state->stack_low_watermark)state->stack_low_watermark=remaining;
    if(!heap_caps_check_integrity_all(false))state->heap_integrity=false;
}
static esp_err_t load_bank(workspace_t *w,uint8_t *invalid_mask)
{
    vp_bank_init(&w->bank);uint8_t *scratch=(uint8_t *)&w->features;
    for(unsigned word=0;word<VP_MAX_WORDS;word++){
        esp_err_t error=tk_voice_store_load(word,w->bank.word[word],&w->next[word],scratch);
        if(error && (s_unknown&(1u<<word)) && (error==ESP_ERR_NVS_NOT_FOUND || tk_voice_store_bad_record(error))){*invalid_mask|=(uint8_t)(1u<<word);continue;}
        if(tk_voice_store_bad_record(error)){*invalid_mask|=(uint8_t)(1u<<word);continue;}
        if(error && error!=ESP_ERR_NVS_NOT_FOUND)return error;
        if(!error)s_unknown&=(uint8_t)~(1u<<word);
    }
    return ESP_OK;
}
static uint32_t level(const int16_t pcm[VP_PCM_SAMPLES],uint32_t *peak)
{
    int32_t dc=0;for(unsigned i=0;i<VP_PCM_SAMPLES;i++)dc+=pcm[i];dc/=VP_PCM_SAMPLES;
    uint32_t sum=0;
    for(unsigned i=0;i<VP_PCM_SAMPLES;i++){
        int32_t v=(int32_t)pcm[i]-dc;uint32_t a=(uint32_t)(v<0?-v:v);sum+=a;if(a>*peak)*peak=a;
    }
    return sum/VP_PCM_SAMPLES;
}
static void terminal(tk_voice_snapshot_t *state,int status,esp_err_t error,int stage)
{
    state->status=status;state->error=error;state->error_stage=stage;state->active=false;
    publish(state);atomic_store(&s_active,false); // All reads/storage and workspace cleanup finished.
}
static void run(request_t request)
{
    tk_voice_snapshot_t state=tk_voice_snapshot();state.generation=request.generation;state.token=request.token;
    worker_diagnostics(&state);
    if(atomic_load(&s_cancel)){terminal(&state,TK_VR_CANCELLED,ESP_OK,TK_VOICE_ERROR_NONE);return;}
    unsigned operation_bytes=request.enrolling?sizeof(vp_frame_t)*VP_MAX_TEMPLATE_FRAMES:sizeof(operation_t);
    if(esp_get_free_heap_size()<sizeof(workspace_t)+operation_bytes+MIN_FREE+STORAGE_RESERVE ||
       heap_caps_get_largest_free_block(MALLOC_CAP_8BIT)<MIN_BLOCK){
        terminal(&state,TK_VR_ERROR,ESP_ERR_NO_MEM,TK_VOICE_ERROR_MEMORY);return;
    }
    workspace_t *w=calloc(1,sizeof(*w));
    if(!w){terminal(&state,TK_VR_ERROR,ESP_ERR_NO_MEM,TK_VOICE_ERROR_MEMORY);return;}
    operation_t *operation=NULL;
    int final_status=TK_VR_COMPLETE,stage=TK_VOICE_ERROR_NONE;esp_err_t error=ESP_OK;
    memory_sample(&state);
    if(state.heap<MIN_FREE+STORAGE_RESERVE || state.largest<MIN_BLOCK){error=ESP_ERR_NO_MEM;stage=TK_VOICE_ERROR_MEMORY;goto done;}
    state.invalid_mask=0;error=load_bank(w,&state.invalid_mask);if(error){stage=TK_VOICE_ERROR_STORE;goto done;}
    for(unsigned word=0;word<VP_MAX_WORDS;word++)state.counts[word]=(uint8_t)count_word(w->bank.word[word]);
    if(request.enrolling && (s_unknown&(1u<<request.word))){error=ESP_ERR_INVALID_STATE;stage=TK_VOICE_ERROR_STORE;goto done;}
    if(request.enrolling)state.example=w->next[request.word];
    else{
        unsigned count=0;for(unsigned word=0;word<VP_MAX_WORDS;word++)count+=state.counts[word];
        if(!count){state.decision=VP_NO_TEMPLATE;goto done;}
    }
    // NVS may need temporary buffers. Do not overlap those with the DTW rows.
    if(atomic_load(&s_cancel)){final_status=TK_VR_CANCELLED;goto done;}
    if(esp_get_free_heap_size()<operation_bytes+MIN_FREE+STORAGE_RESERVE ||
       heap_caps_get_largest_free_block(MALLOC_CAP_8BIT)<MIN_BLOCK){error=ESP_ERR_NO_MEM;stage=TK_VOICE_ERROR_MEMORY;goto done;}
    operation=calloc(1,operation_bytes);
    if(!operation){error=ESP_ERR_NO_MEM;stage=TK_VOICE_ERROR_MEMORY;goto done;}
    memory_sample(&state);
    if(state.heap<MIN_FREE+STORAGE_RESERVE || state.largest<MIN_BLOCK){error=ESP_ERR_NO_MEM;stage=TK_VOICE_ERROR_MEMORY;goto done;}
    if(!request.enrolling)vp_matcher_begin(&operation->matcher,&w->bank,NULL);
    tk_voice_capture_t capture;tk_voice_capture_init(&capture,now_ms(),request.enrolling);
    state.status=TK_VR_CALIBRATING;publish(&state);
    while(!capture.done){
        if(atomic_load(&s_cancel)){final_status=TK_VR_CANCELLED;goto done;}
        error=bsp_audio_read(w->pcm,sizeof(w->pcm));
        if(atomic_load(&s_cancel)){error=ESP_OK;final_status=TK_VR_CANCELLED;goto done;}
        if(error){stage=TK_VOICE_ERROR_CAPTURE;goto done;}
        uint32_t amplitude=level(w->pcm,&state.peak);bool voiced=tk_voice_capture_feed(&capture,amplitude,now_ms());
        state.status=capture.calibrated?TK_VR_LISTENING:TK_VR_CALIBRATING;
        state.threshold=capture.threshold;state.frames=(uint16_t)capture.frames;
        if(voiced){
            int64_t started=esp_timer_get_time();int16_t coefficients[VP_CEPSTRAL_DIM];vp_frame_t frame;
            vp_features_frame(&w->features,w->pcm,coefficients,NULL);vp_quantize_features(coefficients,&frame);
            if(request.enrolling)operation->enrollment[capture.frames-1]=frame;
            else (void)vp_matcher_push(&operation->matcher,&frame,true);
            uint32_t elapsed=(uint32_t)(esp_timer_get_time()-started);if(elapsed>state.frame_max_us)state.frame_max_us=elapsed;
        }
        memory_sample(&state);publish(&state);
    }
    worker_diagnostics(&state);
    state.decision=capture.decision;
    if(capture.decision!=VP_ACCEPTED)goto done;
    if(atomic_load(&s_cancel)){final_status=TK_VR_CANCELLED;goto done;}
    if(request.enrolling){
        memory_sample(&state);
        if(state.heap<MIN_FREE+STORAGE_RESERVE || state.largest<MIN_BLOCK){error=ESP_ERR_NO_MEM;stage=TK_VOICE_ERROR_MEMORY;goto done;}
        tk_voice_store_result_t stored;
        error=tk_voice_store_save(request.word,w->bank.word[request.word],(unsigned)state.example,
            operation->enrollment,capture.frames,(uint8_t *)&w->features,&stored);
        state.storage_write_error=stored.write_error;state.storage_read_error=stored.read_error;state.storage_unknown=stored.unknown;
        if(error){
            if(stored.unknown){s_unknown|=(uint8_t)(1u<<request.word);state.invalid_mask|=(uint8_t)(1u<<request.word);state.counts[request.word]=0;}
            stage=TK_VOICE_ERROR_STORE;goto done;
        }
        // Fresh NVS readback, not the write return code, proved this exact sample.
        (void)vp_bank_enroll(&w->bank,request.word,(unsigned)state.example,operation->enrollment,capture.frames);
        state.counts[request.word]=(uint8_t)count_word(w->bank.word[request.word]);
        state.invalid_mask&=(uint8_t)~(1u<<request.word);
    }else{
        vp_result_t result=vp_matcher_finish(&operation->matcher);state.decision=result.decision;state.word=result.word;
        state.distance=result.best_distance;state.runner_up_distance=result.runner_up_distance;
    }
done:
    memory_sample(&state);
    if(operation){memset(operation,0,operation_bytes);free(operation);}
    memset(w,0,sizeof(*w));free(w);worker_diagnostics(&state);
    terminal(&state,error?TK_VR_ERROR:final_status,error,stage);
}
static void worker(void *context)
{
    (void)context;request_t request;
    for(;;)if(xQueueReceive(s_queue,&request,portMAX_DELAY)==pdTRUE)run(request);
}
static esp_err_t scan_counts(uint8_t counts[TK_VR_WORDS],uint8_t *invalid_mask)
{
    unsigned bytes=TK_VOICE_STORE_SCRATCH_BYTES+sizeof(vp_template_t)*VP_EXAMPLES_PER_WORD;
    uint8_t *scratch=malloc(bytes);if(!scratch)return ESP_ERR_NO_MEM;
    vp_template_t *word=(vp_template_t *)(scratch+TK_VOICE_STORE_SCRATCH_BYTES);
    esp_err_t error=tk_voice_store_scan(counts,invalid_mask,word,scratch);
    memset(scratch,0,bytes);free(scratch);return error;
}
esp_err_t tk_voice_init(void)
{
    if(atomic_load(&s_initialized))return ESP_OK;
    tk_voice_snapshot_t state={.word=-1,.example=-1,.decision=VP_INVALID_INPUT,.heap_integrity=heap_caps_check_integrity_all(false)};
    esp_err_t error=scan_counts(state.counts,&state.invalid_mask);
    if(error){terminal(&state,TK_VR_ERROR,error,error==ESP_ERR_NO_MEM?TK_VOICE_ERROR_MEMORY:TK_VOICE_ERROR_STORE);return error;}
    s_queue=xQueueCreate(1,sizeof(request_t));
    if(!s_queue || xTaskCreate(worker,"tk_voice",4096,NULL,2,NULL)!=pdPASS){
        if(s_queue)vQueueDelete(s_queue);
        s_queue=NULL;
        terminal(&state,TK_VR_ERROR,ESP_ERR_NO_MEM,TK_VOICE_ERROR_MEMORY);return ESP_ERR_NO_MEM;
    }
    publish(&state);atomic_store(&s_initialized,true);return ESP_OK;
}
static esp_err_t request(bool enrolling,unsigned word,uint32_t token)
{
    if(!atomic_load(&s_initialized))return ESP_ERR_INVALID_STATE;
    if(enrolling && word>=VP_MAX_WORDS)return ESP_ERR_INVALID_ARG;
    if(atomic_exchange(&s_active,true))return ESP_ERR_INVALID_STATE;
    atomic_store(&s_cancel,false);uint32_t generation=atomic_fetch_add(&s_generation,1)+1;
    tk_voice_snapshot_t state=tk_voice_snapshot();
    state.generation=generation;state.token=token;state.status=TK_VR_STARTING;state.active=true;state.enrolling=enrolling;
    state.word=enrolling?(int)word:-1;state.example=-1;state.decision=VP_INVALID_INPUT;
    state.distance=state.runner_up_distance=UINT16_MAX;state.frames=0;state.error=ESP_OK;state.error_stage=TK_VOICE_ERROR_NONE;
    state.heap=state.largest=state.peak=state.frame_max_us=state.threshold=0;
    state.storage_write_error=state.storage_read_error=0;state.storage_unknown=false;publish(&state);
    request_t r={generation,token,word,enrolling};
    if(xQueueSend(s_queue,&r,0)==pdTRUE)return ESP_OK;
    terminal(&state,TK_VR_ERROR,ESP_ERR_INVALID_STATE,TK_VOICE_ERROR_NONE);return ESP_ERR_INVALID_STATE;
}
esp_err_t tk_voice_request_enroll(unsigned word,uint32_t token){return request(true,word,token);}
esp_err_t tk_voice_request_recognize(uint32_t token){return request(false,0,token);}
esp_err_t tk_voice_compact_legacy(void)
{
    if(!atomic_load(&s_initialized) || atomic_exchange(&s_active,true))return ESP_ERR_INVALID_STATE;
    uint8_t *scratch=calloc(1,TK_VOICE_STORE_SCRATCH_BYTES);esp_err_t error=scratch?ESP_OK:ESP_ERR_NO_MEM;
    if(scratch){
        for(unsigned word=0;word<TK_VR_WORDS;word++){
            error=tk_voice_store_compact_legacy(word,scratch);
            if(error==ESP_ERR_NVS_NOT_FOUND)error=ESP_OK;
            if(error)break;
        }
        memset(scratch,0,TK_VOICE_STORE_SCRATCH_BYTES);free(scratch);
    }
    atomic_store(&s_active,false);return error;
}
