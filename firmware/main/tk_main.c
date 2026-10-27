#include "tk_ble.h"
#include "tk_probe_model.h"
#include "tk_probe_ui.h"
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include "bsp_battery.h"
#include "bsp_button.h"
#include "bsp_display.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "nvs.h"
#include "nvs_flash.h"

// Only the UI task owns the probe model. Producers do bounded queue sends.
typedef struct { int kind, key; uint32_t ms; bool down; tk_ble_event_t ble; char line[40]; } input_t;
static QueueHandle_t s_inputs;
static atomic_bool s_overflow;
static tk_probe_t s_model = {.mac = true};
static tk_buttons_t s_buttons;
static unsigned s_sent, s_failed;
static bool s_test;
static int s_compare; // 0 normal passkey, 1 physical decision pending, 2 waiting for phone.
static uint32_t s_compare_token;
static char s_status[40] = "Starting Bluetooth";
static uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }
static void enqueue(input_t input) { if (xQueueSend(s_inputs, &input, 0) != pdTRUE) atomic_store(&s_overflow, true); }
static void on_ble(tk_ble_event_t event) { enqueue((input_t){.kind = 1, .ble = event}); }
static void on_button(bsp_btn_t button, bsp_btn_ev_t event, void *user)
{
    (void)user;
    if (event == BSP_BTN_PRESS || event == BSP_BTN_RELEASE)
        enqueue((input_t){.kind = 0, .key = button, .down = event == BSP_BTN_PRESS, .ms = now_ms()});
}
static void os_preference(bool save)
{
    nvs_handle_t h;
    esp_err_t err = nvs_open("nabo_tk", save ? NVS_READWRITE : NVS_READONLY, &h);
    if (err) { if (save) snprintf(s_status, sizeof(s_status), "OS save failed"); return; }
    uint8_t value = s_model.mac;
    if (save) { err = nvs_set_u8(h, "f0_mac", value); if (!err) err = nvs_commit(h); }
    else if (nvs_get_u8(h, "f0_mac", &value) == ESP_OK && value <= 1) s_model.mac = value;
    nvs_close(h);
    if (err) snprintf(s_status, sizeof(s_status), "OS save failed");
}
static void key(int key, bool physical)
{
    if (key < TK_UP || key > TK_LONG_OK) return;
    if (s_compare) {
        int choice = tk_pairing_choice(s_compare == 1, physical, key);
        if (choice) {
            tk_ble_compare_reply(choice == 1, s_compare_token);
            s_compare = choice == 1 ? 2 : 0;
            if (choice == 2) s_model.passkey_valid = false;
        } else if (s_compare == 2 && physical && key == TK_LONG_UP) {
            s_compare = 0; s_model.passkey_valid = false; tk_ble_reconnect();
        }
        return; // Serial-injected keys can neither approve nor send HID during comparison.
    }
    tk_fx_t effect = tk_probe_press(&s_model, (tk_key_t)key);
    if (effect == TK_FX_PAIR) { s_model.ready = false; s_model.pairing = true; tk_ble_pair(); }
    else if (effect == TK_FX_RECONNECT) { s_model.ready = false; s_model.passkey_valid = false; tk_ble_reconnect(); }
    else if (effect == TK_FX_SAVE_OS) os_preference(true);
    else if (effect == TK_FX_PASTE || effect == TK_FX_VOLUME) {
        bool ok = s_test || (effect == TK_FX_PASTE ? tk_ble_send(1, s_model.mac ? 0x08 : 0x01, 0x19) : tk_ble_send(2, 0, 0xe9));
        if (ok && s_test) s_sent++;
        else if (!ok) { s_failed++; snprintf(s_status, sizeof(s_status), "Not sent / not ready"); }
    }
}
static void status(void)
{
    printf("@tk {\"stage\":\"F0\",\"page\":\"%s\",\"ready\":%s,\"os\":\"%s\",\"test\":%s,\"heap\":%u,\"largest\":%u,\"min_heap\":%u,\"ready_ms\":%lu,\"sent\":%u,\"failed\":%u}\n",
           s_model.test ? "test" : "menu", s_model.ready ? "true" : "false", s_model.mac ? "mac" : "windows", s_test ? "true" : "false",
           (unsigned)esp_get_free_heap_size(), (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),
           (unsigned)esp_get_minimum_free_heap_size(), (unsigned long)s_model.reconnect_ms, s_sent, s_failed);
}
static void command(const char *s)
{
    if (!strcmp(s, ">tk.status")) status();
    else if (!strcmp(s, ">tk.test=1")) { s_test = true; puts("@tk test=1"); }
    else if (!strcmp(s, ">tk.test=0")) { s_test = false; puts("@tk test=0"); }
    else if (!strcmp(s, ">tk.pair")) tk_ble_pair();
    else if (!strcmp(s, ">tk.pair.compare")) tk_ble_pair_compare();
    else if (!strcmp(s, ">tk.reconnect")) tk_ble_reconnect();
    else if (!strncmp(s, ">tk.key=", 8)) {
        static const char *names[] = {"up", "down", "ok", "long_up", "long_down", "long_ok"};
        for (int i = 0; i < 6; ++i) if (!strcmp(s + 8, names[i])) { key(i, false); return; }
        puts("@tk invalid key");
    } else puts("@tk unknown command");
}
static void ble_event(tk_ble_event_t event)
{
    static const char *states[] = {"Waiting / hold DN to pair", "Pairing (60 s)", "Reconnecting", "Securing / subscribing", "SECURED / ready"};
    if (event.kind == TK_BLE_STATE && event.value <= TK_BLE_SECURED) {
        s_model.ready = event.value == TK_BLE_SECURED;
        if (event.value != TK_BLE_LINK) s_model.pairing = event.value == TK_BLE_PAIRING;
        if (s_model.ready) s_model.reconnect_ms = event.ms;
        snprintf(s_status, sizeof(s_status), "%s", states[event.value]);
        status();
    } else if (event.kind == TK_BLE_PASSKEY) {
        s_compare = 0;
        s_model.passkey_valid = event.value <= 999999;
        s_model.passkey = event.value;
    } else if (event.kind == TK_BLE_COMPARE && event.value <= 999999) {
        s_compare = 1; s_compare_token = event.ms;
        s_model.ready = false; s_model.pairing = true;
        s_model.passkey_valid = true; s_model.passkey = event.value;
    } else if (event.kind == TK_BLE_RESULT) {
        if (event.value) s_sent++; else s_failed++;
    } else if (event.kind == TK_BLE_ERROR) {
        snprintf(s_status, sizeof(s_status), "BLE/NVS error %lu", (unsigned long)event.value);
        ESP_LOGW("tk", "BLE/NVS error %lu", (unsigned long)event.value);
    }
}
static void serial_task(void *arg)
{
    (void)arg;
    char line[40]; unsigned used = 0; bool discard = false;
    for (;;) {
        int c = getchar();
        if (c < 0) { vTaskDelay(pdMS_TO_TICKS(10)); continue; }
        if (c == '\r') continue;
        if (c == '\n') {
            if (!discard && used) { line[used] = 0; input_t e = {.kind = 2}; memcpy(e.line, line, used + 1); enqueue(e); }
            used = 0; discard = false;
        } else if (used < sizeof(line) - 1 && c >= 32 && c < 127) line[used++] = c;
        else discard = true;
    }
}
static void ui_task(void *arg)
{
    (void)arg;
    uint32_t metric_at = 0, battery_at = 0;
    unsigned heap = 0, largest = 0;
    for (;;) {
        if (atomic_exchange(&s_overflow, false)) {
            xQueueReset(s_inputs); tk_buttons_init(&s_buttons);
            s_model.ready = false; snprintf(s_status, sizeof(s_status), "Queue overflow / reconnect"); tk_ble_reconnect();
        }
        input_t e;
        while (xQueueReceive(s_inputs, &e, 0) == pdTRUE) {
            if (e.kind == 0) key(tk_button_edge(&s_buttons, e.key, e.down, e.ms), true);
            else if (e.kind == 1) ble_event(e.ble);
            else command(e.line);
        }
        uint32_t ms = now_ms();
        key(tk_button_tick(&s_buttons, ms), true);
        if (ms - metric_at >= 1000) {
            heap = esp_get_free_heap_size(); largest = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT); metric_at = ms;
        }
        if (ms - battery_at >= 5000) { tk_ble_hid_battery(bsp_battery_soc()); battery_at = ms; }
        tk_probe_ui_draw(&s_model, s_status, heap, largest, s_sent, s_failed, s_compare);
        vTaskDelay(pdMS_TO_TICKS(16));
    }
}
void app_main(void)
{
    // An NVS error is reported, never hidden with a partition or whole-chip erase.
    ESP_ERROR_CHECK(nvs_flash_init());
    s_inputs = xQueueCreate(64, sizeof(input_t));
    if (!s_inputs) { ESP_LOGE("tk", "UI queue allocation failed"); return; }
    tk_buttons_init(&s_buttons); os_preference(false);
    ESP_ERROR_CHECK(bsp_display_init()); bsp_display_backlight(0);
    if (!tk_probe_ui_open()) { ESP_LOGE("tk", "renderer allocation failed"); return; }
    esp_err_t battery = bsp_battery_init();
    if (battery) ESP_LOGW("tk", "battery unavailable: %s", esp_err_to_name(battery));
    ESP_ERROR_CHECK(bsp_button_init(on_button, NULL));
    esp_err_t ble = tk_ble_start(on_ble);
    if (ble) snprintf(s_status, sizeof(s_status), "Bluetooth unavailable");
    if (xTaskCreate(ui_task, "tk_ui", 6144, NULL, 5, NULL) != pdPASS) { ESP_LOGE("tk", "UI task allocation failed"); return; }
    if (xTaskCreate(serial_task, "tk_serial", 3072, NULL, 2, NULL) != pdPASS) ESP_LOGE("tk", "serial task unavailable");
    bsp_display_backlight(80);
    ESP_LOGI("tk", "NABO Toolkit F0 diag3 / board ai-passport-nabo / no Wi-Fi");
}
