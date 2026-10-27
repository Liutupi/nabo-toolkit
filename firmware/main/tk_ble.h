#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "tk_slots.h"

typedef enum { TK_BLE_STATE, TK_BLE_PASSKEY, TK_BLE_RESULT, TK_BLE_ERROR, TK_BLE_COMPARE, TK_BLE_SLOTS, TK_BLE_BOUND } tk_ble_event_kind_t;
typedef enum { TK_BLE_IDLE, TK_BLE_PAIRING, TK_BLE_RECONNECT, TK_BLE_LINK, TK_BLE_SECURED } tk_ble_state_t;
typedef struct { tk_ble_event_kind_t kind; uint32_t value, ms; } tk_ble_event_t;
typedef void (*tk_ble_sink_t)(tk_ble_event_t event);
esp_err_t tk_ble_start(tk_ble_sink_t sink);
void tk_ble_pair(void);
// Explicit opt-in experiment; default pairing remains DisplayOnly.
void tk_ble_pair_compare(void);
void tk_ble_compare_reply(bool accept, uint32_t token);
void tk_ble_reconnect(void);
bool tk_ble_send(int report, int modifier, int usage);
bool tk_ble_ready(void);
typedef struct { uint8_t report,modifier; uint16_t usage; } tk_ble_report_t;
bool tk_ble_send_batch(const tk_ble_report_t *reports,unsigned count);
bool tk_ble_select_slot(unsigned slot);
bool tk_ble_delete_slot(unsigned slot);
bool tk_ble_set_slot_type(unsigned slot,unsigned os);
bool tk_ble_profiles(tk_slots_t *snapshot);
bool tk_ble_prepare_sleep(void);
bool tk_ble_sleep_ready(void);

// HID GATT is isolated from lifecycle/advertising; only the host touches attributes.
int tk_ble_hid_register(void);
unsigned tk_ble_hid_subscription(uint16_t attr);
uint16_t tk_ble_hid_handle(int report, bool protocol);
bool tk_ble_hid_protocol(void);
bool tk_ble_hid_suspended(void);
void tk_ble_hid_reset(void);
void tk_ble_hid_battery(int pct);
