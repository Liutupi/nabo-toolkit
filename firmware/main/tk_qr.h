#pragma once
#include <stdbool.h>
#include <stdint.h>
// Version <=10 keeps a 512-byte UTF-8 payload bounded and permits integer LCD scaling.
#define TK_QR_BYTES 4096
typedef struct { uint8_t modules[TK_QR_BYTES]; bool valid; } tk_qr_t;
bool tk_qr_encode(tk_qr_t *qr, const char *text);
int tk_qr_size(const tk_qr_t *qr);
bool tk_qr_dark(const tk_qr_t *qr, int x, int y);
