#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"

typedef enum { TK_BLE_STATE, TK_BLE_PASSKEY, TK_BLE_RESULT, TK_BLE_ERROR } tk_ble_event_kind_t;
typedef enum { TK_BLE_IDLE, TK_BLE_PAIRING, TK_BLE_RECONNECT, TK_BLE_LINK, TK_BLE_SECURED } tk_ble_state_t;
typedef struct { tk_ble_event_kind_t kind; uint32_t value, ms; } tk_ble_event_t;
typedef void (*tk_ble_sink_t)(tk_ble_event_t event);
esp_err_t tk_ble_start(tk_ble_sink_t sink);
void tk_ble_pair(void);
void tk_ble_reconnect(void);
bool tk_ble_send(int report, int modifier, int usage);
bool tk_ble_ready(void);

// HID GATT is isolated from lifecycle/advertising; only the host touches attributes.
int tk_ble_hid_register(void);
unsigned tk_ble_hid_subscription(uint16_t attr);
uint16_t tk_ble_hid_handle(int report, bool protocol);
bool tk_ble_hid_protocol(void);
bool tk_ble_hid_suspended(void);
void tk_ble_hid_reset(void);
void tk_ble_hid_battery(int pct);
