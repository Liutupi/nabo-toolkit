#pragma once
#include <stdbool.h>
#include <stdint.h>

// Telemetry only: no radio, peer identifiers, report payloads or send decisions.
typedef struct {
    bool params_valid;
    uint32_t interval_us,latency,supervision_ms;
    uint32_t tx_completed,tx_errors,press_errors,release_errors;
    int enqueue_error,tx_error;
} tk_ble_diag_t;

// Boot-only reset before BLE callbacks/tasks start. Link loss preserves totals.
void tk_ble_diag_reset(void);
// Called only by the NimBLE host task. Raw units are 1.25 ms and 10 ms.
void tk_ble_diag_link(bool valid,uint16_t interval,uint16_t latency,uint16_t supervision);
// A failed attempt includes existing readiness/generation rejection before SDK.
void tk_ble_diag_enqueue(bool release,int status);
// Notification TX completion is not an acknowledgement of host processing.
void tk_ble_diag_tx(int status);
// Bounded atomic snapshot: a racing parameter update may return invalid/zeros.
tk_ble_diag_t tk_ble_diag_snapshot(void);
