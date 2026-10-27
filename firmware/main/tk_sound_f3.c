#include "tk_f1_device.h"
#include "tk_audio_mix.h"
#include <stdatomic.h>
#include "bsp_audio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
extern const uint8_t _binary_boot_welcome_pcm_start[],_binary_boot_welcome_pcm_end[];
typedef struct {unsigned frequency,ms;} tone_t;
static QueueHandle_t s_queue;
static SemaphoreHandle_t s_lock;
static atomic_bool s_muted,s_busy,s_voice,s_cancel;
static atomic_uint s_writes,s_errors,s_nonzero,s_voice_starts,s_tone_starts;
static atomic_int s_last_error;
tk_sound_stats_t tk_sound_stats(void)
{
    return (tk_sound_stats_t){atomic_load(&s_writes),atomic_load(&s_errors),atomic_load(&s_nonzero),atomic_load(&s_voice_starts),atomic_load(&s_tone_starts),atomic_load(&s_last_error),atomic_load(&s_muted)};
}
static void worker(void *context)
{
    (void)context;int16_t samples[320];tk_audio_mix_t mix;
    tk_audio_mix_init(&mix,_binary_boot_welcome_pcm_start,(size_t)(_binary_boot_welcome_pcm_end-_binary_boot_welcome_pcm_start));
    bool last=false;
    for(;;){
        xSemaphoreTake(s_lock,portMAX_DELAY);
        if(atomic_exchange(&s_cancel,false) || atomic_load(&s_muted)){tk_audio_mix_voice(&mix,false);mix.tone_left=0;}
        if(atomic_exchange(&s_voice,false) && !atomic_load(&s_muted)){tk_audio_mix_voice(&mix,true);atomic_fetch_add(&s_voice_starts,1);}
        tone_t tone;
        if(!mix.tone_left && !atomic_load(&s_muted) && xQueueReceive(s_queue,&tone,0)==pdTRUE){tk_audio_mix_tone(&mix,tone.frequency,tone.ms);atomic_fetch_add(&s_tone_starts,1);}
        bool active=tk_audio_mix_fill(&mix,samples,320);atomic_store(&s_busy,active);
        if(active || last){
            for(unsigned i=0;i<320;i++)if(samples[i]){atomic_fetch_add(&s_nonzero,1);break;}
            esp_err_t error=bsp_audio_write(samples,sizeof(samples));
            if(error){atomic_store(&s_last_error,error);if(atomic_fetch_add(&s_errors,1)==0)ESP_LOGW("tk_audio","PCM write error=%d",error);}
            else atomic_fetch_add(&s_writes,1);
        } // A final silent DMA block follows playback.
        last=active;xSemaphoreGive(s_lock);
        if(!active)vTaskDelay(pdMS_TO_TICKS(20));
    }
}
esp_err_t tk_sound_open(void)
{
    s_lock=xSemaphoreCreateMutex();if(!s_lock)return ESP_ERR_NO_MEM;
    esp_err_t e=bsp_audio_init();if(e)return e;e=bsp_audio_set_format(16000,16,1);if(e)return e;
    // Codec percentage is a -50..0 dB curve:35 is -32.5 dB,80 is -10 dB.
    // Match the board's accepted Fortune setting; PCM and tones retain headroom.
    bsp_audio_set_volume(80);
    s_queue=xQueueCreate(8,sizeof(tone_t));if(!s_queue)return ESP_ERR_NO_MEM;
    if(xTaskCreate(worker,"tk_audio",3072,NULL,3,NULL)!=pdPASS){vQueueDelete(s_queue);s_queue=NULL;return ESP_ERR_NO_MEM;}return ESP_OK;
}
bool tk_sound_tone(unsigned frequency,unsigned ms)
{
    if(!s_queue || atomic_load(&s_muted) || frequency<80 || frequency>5000 || ms>1000)return false;
    tone_t t={frequency,ms};return xQueueSend(s_queue,&t,0)==pdTRUE;
}
bool tk_sound_boot_voice(void){if(!s_queue || atomic_load(&s_muted))return false;atomic_store(&s_voice,true);return true;}
void tk_sound_stop_voice(void){atomic_store(&s_voice,false);atomic_store(&s_cancel,true);}
bool tk_sound_idle(void){return !s_queue || (!atomic_load(&s_busy) && !atomic_load(&s_voice) && uxQueueMessagesWaiting(s_queue)==0);}
void tk_sound_mute(bool muted)
{
    atomic_store(&s_muted,muted);if(muted){tk_sound_stop_voice();if(s_queue)xQueueReset(s_queue);}
}
bool tk_sound_prepare_sleep(void){tk_sound_mute(true);return !s_lock || xSemaphoreTake(s_lock,pdMS_TO_TICKS(2000))==pdTRUE;}
