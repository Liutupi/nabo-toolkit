// Run the actual worker against synthetic PCM and bounded fake RTOS/codec APIs.
// No physical microphone, device NVS or real-time performance claim.
#include "tk_voice.h"
#include "bsp_audio.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include <setjmp.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#ifdef _WIN32
#include <windows.h>
static void pause_ms(void){Sleep(1);}
#else
#include <time.h>
static void pause_ms(void){struct timespec delay={0,1000000};nanosleep(&delay,NULL);}
#endif

struct mock_queue {unsigned size;atomic_bool pending;uint8_t bytes[64];};
static TaskFunction_t s_task;
static jmp_buf s_return;
static atomic_bool s_block,s_entered,s_release;
static unsigned s_reads,s_speech=20,s_heap=100000,s_largest=80000,s_stack=2048,s_integrity_checks;
static bool s_integrity=true;
static bool s_read_error,s_running;
static int64_t s_clock;
QueueHandle_t xQueueCreate(unsigned length,unsigned size)
{(void)length;if(size>64)return NULL;struct mock_queue *q=calloc(1,sizeof(*q));if(q)q->size=size;return q;}
void vQueueDelete(QueueHandle_t q){free(q);}
int xQueueSend(QueueHandle_t q,const void *item,uint32_t wait)
{(void)wait;if(atomic_load(&q->pending))return 0;memcpy(q->bytes,item,q->size);atomic_store(&q->pending,true);return 1;}
int xQueueReceive(QueueHandle_t q,void *item,uint32_t wait)
{(void)wait;if(atomic_exchange(&q->pending,false)){memcpy(item,q->bytes,q->size);return 1;}if(s_running)longjmp(s_return,1);return 0;}
int xTaskCreate(TaskFunction_t task,const char *name,unsigned stack,void *arg,unsigned priority,void *handle)
{(void)name;(void)stack;(void)arg;(void)priority;(void)handle;s_task=task;return 1;}
size_t esp_get_free_heap_size(void){return s_heap;}
size_t heap_caps_get_largest_free_block(unsigned caps){(void)caps;return s_largest;}
bool heap_caps_check_integrity_all(bool print_errors){(void)print_errors;s_integrity_checks++;return s_integrity;}
unsigned uxTaskGetStackHighWaterMark(void *task){(void)task;return s_stack;}
int64_t esp_timer_get_time(void){return s_clock;}
esp_err_t bsp_audio_read(void *pcm,size_t bytes)
{
    atomic_store(&s_entered,true);
    while(atomic_load(&s_block) && !atomic_load(&s_release))pause_ms();
    s_reads++;s_clock+=20000;
    if(s_read_error)return ESP_FAIL;
    int16_t *samples=pcm;bool speech=s_reads>15 && s_reads<=15+s_speech;
    for(unsigned i=0;i<bytes/sizeof(*samples);i++)samples[i]=speech?(i%32<16?5000:-5000):0;
    return ESP_OK;
}

// Include, rather than clone, the production worker/control implementation so
// test-only reset can clean its private task state between simulated boots.
static unsigned s_allocations,s_fail_allocation,s_cancel_allocation;
static void *s_jobs[4];
static void *voice_calloc(size_t count,size_t size)
{
    s_allocations++;if(s_allocations==s_fail_allocation)return NULL;
    void *p=calloc(count,size);if(p)for(unsigned i=0;i<4;i++)if(!s_jobs[i]){s_jobs[i]=p;break;}
    if(s_allocations==s_cancel_allocation)tk_voice_cancel();
    return p;
}
static void voice_free(void *p){for(unsigned i=0;i<4;i++)if(s_jobs[i]==p)s_jobs[i]=NULL;free(p);}
#define calloc voice_calloc
#define free voice_free
#include "../firmware/main/tk_voice.c"
#undef calloc
#undef free
void tk_voice_host_reset(void)
{
    if(s_queue){vQueueDelete(s_queue);s_queue=NULL;}
    atomic_store(&s_active,false);atomic_store(&s_cancel,false);atomic_store(&s_initialized,false);atomic_store(&s_generation,0);
    s_state=(tk_voice_snapshot_t){.word=-1,.example=-1};s_unknown=0;s_task=NULL;s_reads=0;s_speech=20;s_clock=0;
    for(unsigned i=0;i<4;i++){free(s_jobs[i]);s_jobs[i]=NULL;}s_allocations=s_fail_allocation=s_cancel_allocation=0;
    s_heap=100000;s_largest=80000;s_read_error=s_running=false;s_stack=2048;s_integrity=true;s_integrity_checks=0;
    atomic_store(&s_block,false);atomic_store(&s_entered,false);atomic_store(&s_release,false);
}
void tk_voice_host_drain(void)
{if(!s_task)return;s_running=true;if(!setjmp(s_return))s_task(NULL);s_running=false;}
void tk_voice_host_audio(unsigned frames,int fail,int block)
{s_reads=0;s_speech=frames;s_read_error=fail!=0;atomic_store(&s_block,block!=0);atomic_store(&s_entered,false);atomic_store(&s_release,false);}
void tk_voice_host_release(void){atomic_store(&s_release,true);}
int tk_voice_host_read_entered(void){return atomic_load(&s_entered);}
unsigned tk_voice_host_reads(void){return s_reads;}
void tk_voice_host_memory(unsigned heap,unsigned largest){s_heap=heap;s_largest=largest;}
unsigned tk_voice_host_snapshot_bytes(void){return sizeof(tk_voice_snapshot_t);}
unsigned tk_voice_host_workspace_bytes(void){return sizeof(workspace_t)+sizeof(operation_t);}
unsigned tk_voice_host_enroll_workspace_bytes(void){return sizeof(workspace_t)+sizeof(vp_frame_t)*VP_MAX_TEMPLATE_FRAMES;}
void tk_voice_host_allocation_fault(unsigned fail,unsigned cancel){s_allocations=0;s_fail_allocation=fail;s_cancel_allocation=cancel;}
unsigned tk_voice_host_allocations(void){return s_allocations;}
unsigned tk_voice_host_live_allocations(void){unsigned n=0;for(unsigned i=0;i<4;i++)if(s_jobs[i])n++;return n;}
unsigned tk_voice_host_counts_offset(void){return offsetof(tk_voice_snapshot_t,counts);}
void tk_voice_host_diagnostics(unsigned stack,int integrity){s_stack=stack;s_integrity=integrity!=0;}
unsigned tk_voice_host_integrity_checks(void){return s_integrity_checks;}
