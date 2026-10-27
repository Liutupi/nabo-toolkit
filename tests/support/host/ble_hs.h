#pragma once
#include <stdint.h>
typedef struct {uint8_t type,val[6];} ble_addr_t;
int ble_gap_unpair(const ble_addr_t *peer);
