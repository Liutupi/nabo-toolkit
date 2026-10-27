#pragma once
#include <stdbool.h>
#include <stdint.h>

typedef enum { TK_UP, TK_DOWN, TK_OK, TK_LONG_UP, TK_LONG_DOWN, TK_LONG_OK } tk_key_t;
typedef enum { TK_FX_NONE, TK_FX_PASTE, TK_FX_VOLUME, TK_FX_PAIR, TK_FX_RECONNECT, TK_FX_SAVE_OS } tk_fx_t;
typedef struct { int held; uint32_t since; bool fired; } tk_buttons_t;
typedef struct { bool test, mac, ready, pairing, passkey_valid; uint32_t passkey, reconnect_ms; } tk_probe_t;

void tk_buttons_init(tk_buttons_t *b);
int tk_button_edge(tk_buttons_t *b, int key, bool down, uint32_t now);
int tk_button_tick(tk_buttons_t *b, uint32_t now);
tk_fx_t tk_probe_press(tk_probe_t *m, tk_key_t key);
bool tk_hid_ready(bool encrypted, bool authenticated, unsigned subscribed, bool report_mode, bool suspended);
bool tk_hid_packet(int report, int modifier, int usage, uint8_t out[8], unsigned *length);
