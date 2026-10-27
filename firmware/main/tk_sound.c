#include "tk_f1_device.h"
#include <stdatomic.h>
#include "bsp_audio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
typedef struct {unsigned frequency,ms;} tone_t;
static QueueHandle_t s_queue;
static atomic_bool s_busy,s_muted;
static SemaphoreHandle_t s_lock;
static void worker(void *context)
{
    (void)context;tone_t tone;int16_t samples[320];
    for(;;){
        if(xQueueReceive(s_queue,&tone,portMAX_DELAY)!=pdTRUE)continue;
        xSemaphoreTake(s_lock,portMAX_DELAY);
        if(atomic_load(&s_muted)){xSemaphoreGive(s_lock);continue;}
        atomic_store(&s_busy,true);uint32_t phase=0,step=(uint32_t)(((uint64_t)tone.frequency<<24)/16000);
        unsigned left=tone.ms*16;
        while(left && !atomic_load(&s_muted)){
            unsigned count=left<320?left:320;
            for(unsigned i=0;i<count;i++){phase=(phase+step)&0xffffff;int value=(int)(phase>>12);value=value<2048?value:4095-value;samples[i]=(int16_t)((value-1024)*2);}
            if(bsp_audio_write(samples,count*2)!=ESP_OK)break;
            left-=count;
        }
        // Explicit silence clears the final waveform from the codec DMA path.
        for(unsigned i=0;i<320;i++)samples[i]=0;
        bsp_audio_write(samples,sizeof(samples));atomic_store(&s_busy,false);xSemaphoreGive(s_lock);
    }
}
esp_err_t tk_sound_open(void)
{
    s_lock=xSemaphoreCreateMutex();if(!s_lock)return ESP_ERR_NO_MEM;
    esp_err_t e=bsp_audio_init();if(e)return e;e=bsp_audio_set_format(16000,16,1);if(e)return e;bsp_audio_set_volume(35);
    s_queue=xQueueCreate(8,sizeof(tone_t));if(!s_queue)return ESP_ERR_NO_MEM;
    if(xTaskCreate(worker,"tk_audio",3072,NULL,3,NULL)!=pdPASS){vQueueDelete(s_queue);s_queue=NULL;return ESP_ERR_NO_MEM;}return ESP_OK;
}
bool tk_sound_tone(unsigned frequency,unsigned ms)
{
    if(!s_queue || atomic_load(&s_muted) || frequency<80 || frequency>5000 || ms>1000)return false;
    tone_t t={frequency,ms};return xQueueSend(s_queue,&t,0)==pdTRUE;
}
bool tk_sound_idle(void){return !s_queue || (!atomic_load(&s_busy) && uxQueueMessagesWaiting(s_queue)==0);}
void tk_sound_mute(bool muted){atomic_store(&s_muted,muted);if(muted && s_queue)xQueueReset(s_queue);}
bool tk_sound_prepare_sleep(void)
{
    tk_sound_mute(true);
    // Return with the lock held: the caller must immediately deep-sleep or restart.
    return !s_lock || xSemaphoreTake(s_lock,pdMS_TO_TICKS(2000))==pdTRUE;
}
