// F1 UI task owns the complete model. BLE/buttons/serial only enqueue bounded inputs.
#include "tk_model_internal.h"
#include "tk_ble.h"
#include "tk_ble_diag.h"
#include "tk_f1_device.h"
#include "tk_persist.h"
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include "bsp_audio.h"
#include "bsp_battery.h"
#include "bsp_button.h"
#include "bsp_display.h"
#include "bsp_i2c.h"
#include "bsp_pins.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_sleep.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "sdkconfig.h"
#ifdef CONFIG_NABO_TOOLKIT_F2
#include "tk_config_serial.h"
#include "tk_usb_console.h"
static tk_config_serial_t s_config;
#ifdef TK_F3
#define TK_STAGE "F3"
#else
#define TK_STAGE "F2"
#endif
static void config_reply(void *context,const char *line){(void)context;printf("%s\n",line);}
#else
#define TK_STAGE "F1"
#endif

typedef struct {int kind,key;uint32_t ms;bool down;tk_ble_event_t ble;char line[96];} input_t;
static QueueHandle_t s_inputs;
static atomic_bool s_overflow;
static tk_state_t s_model,s_before_test;
static tk_effects_t s_effects;
static tk_buttons_t s_buttons;
static bool s_test,s_pair_compare,s_ble_available,s_sleep_pending;
static int s_compare,s_last_error;
static uint32_t s_compare_token;
static unsigned s_sent,s_failed,s_simulated;
static int64_t s_sleep_requested;
static int64_t now_ms(void){return esp_timer_get_time()/1000;}
static void enqueue(input_t e){if(xQueueSend(s_inputs,&e,0)!=pdTRUE)atomic_store(&s_overflow,true);}
static void ble_input(tk_ble_event_t e){enqueue((input_t){.kind=1,.ble=e});}
static void button_input(bsp_btn_t key,bsp_btn_ev_t event,void *context)
{
    (void)context;
    if(event==BSP_BTN_PRESS || event==BSP_BTN_RELEASE)enqueue((input_t){.kind=0,.key=key,.down=event==BSP_BTN_PRESS,.ms=(uint32_t)now_ms()});
}
static void problem(const char *text,esp_err_t error)
{
    int64_t now=now_ms();tk_model_screen_reset(&s_model,now);
    s_last_error=error;tk_model_toast(&s_model,now,text,true);ESP_LOGW("tk_f1","operation error=%d",error);
}
static void profiles(void)
{
    tk_slots_t saved;if(!tk_ble_profiles(&saved))return;
    for(int i=0;i<3;i++){
        s_model.slots[i].used=saved.peers[i].used;s_model.slots[i].os=saved.peers[i].os;
        snprintf(s_model.slots[i].name,sizeof(s_model.slots[i].name),"%s",saved.peers[i].name);
        s_model.bind_order[i]=saved.order[i];
    }
    s_model.bind_count=saved.count;s_model.active=saved.active;
}
static void effects(void)
{
    tk_ble_report_t reports[64];unsigned count=0;
    for(int i=0;i<s_effects.count;i++)if(s_effects.items[i].type==TK_EFFECT_HID)count++;
    if(s_effects.overflow || count>64){problem("文字太长，稍后再试",ESP_ERR_NO_MEM);return;}
    unsigned n=0;
    for(int i=0;i<s_effects.count;i++){
        const tk_effect_t *e=&s_effects.items[i];
        if(e->type==TK_EFFECT_HID)reports[n++]=(tk_ble_report_t){e->kind==TK_PACKET_MEDIA?2:1,e->mod,e->usage};
    }
    if(s_test){s_simulated+=count;return;}
    if(count && !tk_ble_send_batch(reports,count)){s_failed+=count;problem("未发送 · 蓝牙尚未就绪",ESP_ERR_INVALID_STATE);return;}
    for(int i=0;i<s_effects.count;i++){
        const tk_effect_t *e=&s_effects.items[i];
        if(e->type==TK_EFFECT_BEEP)tk_sound_tone(e->frequency,e->ms);
        else if(e->type==TK_EFFECT_VOICE){
#ifdef TK_F3
            tk_sound_boot_voice();
#else
            tk_sound_tone(880,100);
#endif
        }
    }
}
static void press(int key,bool physical)
{
    if(key<TK_UP || key>TK_LONG_OK)return;
    if(s_compare){
        int choice=tk_pairing_choice(s_compare==1,physical,key);
        if(choice){tk_ble_compare_reply(choice==1,s_compare_token);s_compare=choice==1?2:0;if(choice==2)s_model.passkey_valid=false;}
        else if(physical && key==TK_LONG_UP){s_compare=0;s_model.pairing=false;s_model.passkey_valid=false;tk_ble_reconnect();}
        return;
    }
    bool pairing=s_model.pairing,picker=s_model.os_pick;int old_delete=s_model.confirm_del,old_os_slot=s_model.os_slot;
    int page=s_model.page,selected=s_model.conn_sel;
    bool beep=s_model.beep,voice=s_model.voice,remote_dim=s_model.remote_dim;int talk=s_model.talk,sleep=s_model.sleep;
    tk_model_press(&s_model,(tk_key_t)key,now_ms(),&s_effects);
#ifdef TK_F3
    if(page==TK_PAGE_BOOT && s_model.page!=TK_PAGE_BOOT)tk_sound_stop_voice();
#endif
    if(!s_test){
        if(!pairing && s_model.pairing){
            if(!s_ble_available){s_model.pairing=false;problem("蓝牙不可用",ESP_ERR_INVALID_STATE);}
            else if(s_pair_compare)tk_ble_pair_compare();else tk_ble_pair();
        }else if(pairing && !s_model.pairing)tk_ble_reconnect();
        else if(picker && !s_model.os_pick && key==TK_OK){if(!tk_ble_set_slot_type(old_os_slot,s_model.slots[old_os_slot].os)){profiles();problem("设备类型未保存",ESP_ERR_NO_MEM);}}
        else if(old_delete>=0 && key==TK_OK){if(!tk_ble_delete_slot(old_delete)){profiles();problem("设备未删除",ESP_ERR_NO_MEM);}}
        else if(page==TK_PAGE_CONN && !picker && old_delete<0 && key==TK_OK && selected<3 && s_model.slots[selected].used){
            if(!tk_ble_select_slot(selected)){profiles();problem("暂时无法切换设备",ESP_ERR_NO_MEM);}
            s_model.connected=false;
        }
        if(beep!=s_model.beep || voice!=s_model.voice || talk!=s_model.talk || sleep!=s_model.sleep){
            esp_err_t error=tk_persist_save(&s_model);
            if(error){s_model.beep=beep;s_model.voice=voice;s_model.talk=talk;s_model.sleep=sleep;problem("设置保存失败",error);}
        }
        if(remote_dim!=s_model.remote_dim){
            esp_err_t error=tk_persist_save_remote(&s_model);
            if(error){s_model.remote_dim=remote_dim;problem("设置保存失败",error);}
        }
    }
    effects();
}
static void on_ble(tk_ble_event_t e)
{
    if(e.kind==TK_BLE_SLOTS){if(!s_test)profiles();}
    else if(e.kind==TK_BLE_BOUND){
        if(s_test)return;
        profiles();s_model.conn_sel=e.value;s_model.connected=false;s_model.pairing=false;s_model.passkey_valid=false;s_compare=0;
        if(e.ms && e.value<3){s_model.os_pick=true;s_model.os_slot=e.value;s_model.os_sel=s_model.slots[e.value].os;}
    }else if(e.kind==TK_BLE_STATE){
        if(!s_test)s_model.connected=e.value==TK_BLE_SECURED && s_model.slots[s_model.active].used && tk_ble_ready();
    }else if(e.kind==TK_BLE_PASSKEY){
        s_compare=0;
        if(e.value>999999)s_model.passkey_valid=false;
        else {char code[8];snprintf(code,sizeof(code),"%06lu",(unsigned long)e.value);tk_model_event(&s_model,"passkey",now_ms(),code);}
    }else if(e.kind==TK_BLE_COMPARE){
        if(!s_model.pairing || s_test){tk_ble_compare_reply(false,e.ms);return;}
        tk_model_screen_reset(&s_model,now_ms());s_compare=1;s_compare_token=e.ms;s_model.passkey_valid=true;s_model.passkey=e.value;
    }else if(e.kind==TK_BLE_RESULT){if(e.value)s_sent++;else s_failed++;}
    else if(e.kind==TK_BLE_ERROR){if(!s_test)profiles();problem("蓝牙或存储操作失败",e.value);}
}
static void status(void)
{
    tk_ble_diag_t diag=tk_ble_diag_snapshot();
#ifdef TK_F3
    tk_sound_stats_t audio=tk_sound_stats();
#endif
    printf("@tk {\"stage\":\"" TK_STAGE "\",\"page\":\"%s\",\"ready\":%s,\"slot\":%d,\"slots\":%d,\"test\":%s,\"heap\":%u,\"largest\":%u,\"sent\":%u,\"failed\":%u,\"simulated\":%u,\"error\":%d,\"screen_off\":%s,\"remote_dim\":%s,\"media_mode\":%d,\"ble_params_valid\":%s,\"ble_ci_us\":%u,\"ble_latency\":%u,\"ble_sto_ms\":%u,\"ble_tx_ok\":%u,\"ble_tx_err\":%u,\"ble_press_err\":%u,\"ble_release_err\":%u,\"ble_enqueue_error\":%d,\"ble_tx_error\":%d"
#ifdef TK_F3
           ",\"min_heap\":%u,\"draw_max_us\":%u,\"anim_id\":%d,\"anim_frame\":%d,\"beep\":%s,\"voice\":%s,\"muted\":%s,\"audio_writes\":%u,\"audio_errors\":%u,\"audio_nonzero\":%u,\"voice_starts\":%u,\"tone_starts\":%u,\"audio_last\":%d"
#endif
           "}\n",
           tk_page_names[s_model.page],s_model.connected&&tk_ble_ready()?"true":"false",s_model.active,s_model.bind_count,s_test?"true":"false",
           (unsigned)esp_get_free_heap_size(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),s_sent,s_failed,s_simulated,s_last_error,
           s_model.screen_off?"true":"false",s_model.remote_dim?"true":"false",s_model.media_mode,
           diag.params_valid?"true":"false",(unsigned)diag.interval_us,(unsigned)diag.latency,(unsigned)diag.supervision_ms,
           (unsigned)diag.tx_completed,(unsigned)diag.tx_errors,(unsigned)diag.press_errors,(unsigned)diag.release_errors,diag.enqueue_error,diag.tx_error
#ifdef TK_F3
           ,(unsigned)esp_get_minimum_free_heap_size(),tk_f1_ui_max_draw_us(),tk_f1_ui_animation_id(),tk_f1_ui_animation_frame()
           ,s_model.beep?"true":"false",s_model.voice?"true":"false",audio.muted?"true":"false",audio.writes,audio.errors,audio.nonzero,audio.voice_starts,audio.tone_starts,audio.last_error
#endif
           );
}
static void command(const char *text)
{
#ifdef CONFIG_NABO_TOOLKIT_F2
    if(tk_config_serial_line(&s_config,text,now_ms(),!s_test && !s_compare)){s_model.last_input=now_ms();tk_model_screen_reset(&s_model,now_ms());return;}
#endif
    if(!strcmp(text,">tk.status"))status();
    else if(!strcmp(text,">tk.test=1")){if(!s_test)s_before_test=s_model;s_test=true;tk_model_screen_reset(&s_model,now_ms());tk_sound_mute(true);tk_ble_reconnect();puts("@tk test=1");}
    else if(!strcmp(text,">tk.test=0")){
        if(s_test)s_model=s_before_test;
        s_test=false;s_compare=0;profiles();s_model.pairing=false;s_model.passkey_valid=false;s_model.os_pick=false;s_model.confirm_del=-1;
        s_model.connected=tk_ble_ready();s_model.cam_end=0;s_model.burst_left=0;s_model.last_input=now_ms();tk_model_screen_reset(&s_model,now_ms());tk_sound_mute(false);puts("@tk test=0");
    }
    else if(!strcmp(text,">tk.reconnect")){s_model.connected=false;tk_ble_reconnect();}
    else if(!strcmp(text,">tk.pair") || !strcmp(text,">tk.pair.compare")){
        if(s_test || s_compare){puts("@tk pairing unavailable in current diagnostic mode");return;}
        s_model.page=TK_PAGE_CONN;s_model.conn_sel=3;s_model.os_pick=false;s_model.confirm_del=-1;s_model.pairing=false;
        s_pair_compare=!strcmp(text,">tk.pair.compare");press(TK_OK,false);s_pair_compare=false;
    }else if(!strncmp(text,">tk.key=",8)){
        for(int key=0;key<6;key++)if(!strcmp(text+8,tk_key_names[key])){press(key,false);return;}
        puts("@tk invalid key");
    }else if(s_test && !strncmp(text,">tk.sim=",8)){
        const char *event=text+8;
        if(!strncmp(event,"paired ",7))tk_model_event(&s_model,"paired",now_ms(),event+7);
        else if(!strncmp(event,"passkey ",8))tk_model_event(&s_model,"passkey",now_ms(),event+8);
        else if(!strcmp(event,"disconnect") || !strcmp(event,"reconnect") || !strcmp(event,"wake"))tk_model_event(&s_model,event,now_ms(),NULL);
        else puts("@tk invalid simulation");
    }else puts("@tk unknown command");
}
static void serial_task(void *arg)
{
    (void)arg;char line[96];unsigned n=0;bool discard=false;
    for(;;){int c=getchar();if(c<0){clearerr(stdin);vTaskDelay(pdMS_TO_TICKS(10));continue;}if(c=='\r')continue;
        if(c=='\n'){
            if(n && (!discard || (n>=8 && !strncmp(line,">tk.cfg.",8)))){line[n]=0;input_t e={.kind=2};if(discard)snprintf(e.line,sizeof(e.line),">tk.cfg.invalid");else memcpy(e.line,line,n+1);enqueue(e);}
            n=0;discard=false;
        }
        else if(c>=32 && c<127 && n<sizeof(line)-1)line[n++]=c;else discard=true;
    }
}
static void power(int64_t now)
{
#ifdef CONFIG_NABO_TOOLKIT_F2
    if(tk_config_serial_busy(&s_config))return;
#endif
    bool due=!s_test && s_buttons.held<0 && tk_model_sleep_due(&s_model,now);
    if(!due){if(s_sleep_pending){s_sleep_pending=false;tk_ble_reconnect();}return;}
    if(!s_sleep_pending){if(tk_ble_prepare_sleep()){s_sleep_pending=true;s_sleep_requested=now;}return;}
    if(!tk_ble_sleep_ready()){
        if(now-s_sleep_requested>2000){s_sleep_pending=false;s_model.last_input=now;problem("蓝牙未停止，暂缓休眠",ESP_ERR_TIMEOUT);tk_ble_reconnect();}return;
    }
    if(bsp_button_read_mv()<BSP_BTN_MV_RELEASED_MIN){s_sleep_pending=false;s_model.last_input=now;tk_ble_reconnect();return;}
    if(!tk_sound_prepare_sleep()){s_sleep_pending=false;s_model.last_input=now;tk_sound_mute(false);tk_ble_reconnect();return;}
    bsp_display_backlight(0);int level=0;
    if(bsp_button_prepare_deep_sleep(&level)!=ESP_OK || level!=1)esp_restart();
    if(esp_sleep_enable_gpio_wakeup_on_hp_periph_powerdown(1ULL<<BSP_BTN_GPIO,ESP_GPIO_WAKEUP_GPIO_LOW)!=ESP_OK)esp_restart();
    // The shared ADC GPIO can electrically wake on any key; UP is the documented path.
    if(bsp_battery_sleep()!=ESP_OK || bsp_audio_sleep()!=ESP_OK || bsp_audio_prepare_deep_sleep()!=ESP_OK ||
       bsp_i2c_prepare_deep_sleep()!=ESP_OK || bsp_display_prepare_deep_sleep()!=ESP_OK)esp_restart();
    esp_deep_sleep_start();esp_restart();
}
static void ui_task(void *arg)
{
    (void)arg;int64_t battery_at=0;
    for(;;){
        if(atomic_exchange(&s_overflow,false)){xQueueReset(s_inputs);tk_buttons_init(&s_buttons);s_model.connected=false;s_model.pairing=false;s_model.cam_end=0;s_model.burst_left=0;tk_ble_reconnect();problem("输入队列满，正在回连",ESP_ERR_NO_MEM);}
        input_t e;while(xQueueReceive(s_inputs,&e,0)==pdTRUE){
            if(e.kind==0)press(tk_button_edge(&s_buttons,e.key,e.down,e.ms),true);
            else if(e.kind==1)on_ble(e.ble);else command(e.line);
        }
        if(!s_test)s_model.connected=s_ble_available && tk_ble_ready() && s_model.slots[s_model.active].used;
#ifdef CONFIG_NABO_TOOLKIT_F2
        tk_config_serial_tick(&s_config,now_ms(),!s_test && !s_compare);
        if(tk_config_serial_busy(&s_config))tk_model_screen_reset(&s_model,now_ms());
#endif
        int64_t now=now_ms();press(tk_button_tick(&s_buttons,(uint32_t)now),true);tk_model_tick(&s_model,now,&s_effects);effects();
        if(now-battery_at>=5000){tk_ble_hid_battery(bsp_battery_soc());battery_at=now;}
        if(!tk_f1_ui_draw(&s_model,now,s_compare,s_ble_available))problem("画面资源不足",ESP_ERR_NO_MEM);
        power(now);vTaskDelay(pdMS_TO_TICKS(16));
    }
}
void app_main(void)
{
#ifdef CONFIG_NABO_TOOLKIT_F2
    tk_usb_console_init();
#endif
    ESP_ERROR_CHECK(nvs_flash_init()); // Preserve NVS on errors; never erase as a recovery shortcut.
    tk_model_init(&s_model,now_ms());esp_err_t saved=tk_persist_load(&s_model);
#ifdef CONFIG_NABO_TOOLKIT_F2
    esp_err_t config_saved=tk_config_serial_init(&s_config,&s_model,config_reply,NULL);
#endif
    s_inputs=xQueueCreate(64,sizeof(input_t));if(!s_inputs){ESP_LOGE("tk_f1","input allocation failed");return;}
    tk_buttons_init(&s_buttons);ESP_ERROR_CHECK(bsp_display_init());bsp_display_backlight(0);
    if(!tk_f1_ui_open()){ESP_LOGE("tk_f1","renderer allocation failed");return;}
    esp_err_t battery=bsp_battery_init();if(battery)ESP_LOGW("tk_f1","battery unavailable=%d",battery);
    ESP_ERROR_CHECK(bsp_button_init(button_input,NULL));esp_err_t audio=tk_sound_open();if(audio)ESP_LOGW("tk_f1","audio unavailable=%d",audio);
    esp_err_t ble=tk_ble_start(ble_input);s_ble_available=!ble;
    if(saved)problem("设置校验失败，保留原记录",saved);
#ifdef CONFIG_NABO_TOOLKIT_F2
    if(config_saved)problem("配置校验失败，保留原记录",config_saved);
#endif
    if(ble)problem("蓝牙不可用",ble);
#ifdef TK_F3
    s_model.boot_start=s_model.last_input=now_ms(); // Show the entire animation after LCD initialization.
#endif
    if(xTaskCreate(ui_task,"tk_ui",8192,NULL,5,NULL)!=pdPASS){ESP_LOGE("tk_f1","UI task failed");return;}
    if(xTaskCreate(serial_task,"tk_serial",3072,NULL,2,NULL)!=pdPASS)ESP_LOGE("tk_f1","serial task failed");
    // The UI enables backlight only after the first complete, fenced frame.
    ESP_LOGI("tk_f1","NABO Toolkit " TK_STAGE " dev / board ai-passport-nabo / no Wi-Fi");
}
