#pragma once
#include "tk_slots.h"
#include "host/ble_hs.h"
#include "esp_err.h"
// These functions run only on the NimBLE host; snapshot copies are mutex-protected.
void tk_ble_slots_init(void);
esp_err_t tk_ble_slots_sync(void);
bool tk_ble_slots_selected(ble_addr_t *peer);
int tk_ble_slots_bound(const ble_addr_t *peer);
esp_err_t tk_ble_slots_select(unsigned slot);
esp_err_t tk_ble_slots_type(unsigned slot,unsigned os);
esp_err_t tk_ble_slots_delete(unsigned slot);
bool tk_ble_slots_snapshot(tk_slots_t *out);
bool tk_ble_slots_available(void);
bool tk_ble_slots_known(const ble_addr_t *peer);
