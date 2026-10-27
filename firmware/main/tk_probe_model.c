#include "tk_probe_model.h"
#include <string.h>

void tk_buttons_init(tk_buttons_t *b) { *b = (tk_buttons_t){.held = -1}; }
int tk_button_tick(tk_buttons_t *b, uint32_t now)
{
    if (b->held < 0 || b->fired || (uint32_t)(now - b->since) < 500) return -1;
    b->fired = true;
    return b->held + 3;
}
int tk_button_edge(tk_buttons_t *b, int key, bool down, uint32_t now)
{
    if (key < 0 || key > 2) return -1;
    if (down) {
        if (b->held < 0) { b->held = key; b->since = now; b->fired = false; }
        return -1;
    }
    if (key != b->held) return -1;
    int event = tk_button_tick(b, now);
    if (event < 0 && !b->fired) event = key;
    b->held = -1;
    return event;
}
tk_fx_t tk_probe_press(tk_probe_t *m, tk_key_t key)
{
    if (key == TK_LONG_UP) { m->test = false; m->passkey_valid = false; return m->pairing ? TK_FX_RECONNECT : TK_FX_NONE; }
    if (key == TK_LONG_DOWN) return TK_FX_PAIR;
    if (key == TK_LONG_OK) return TK_FX_RECONNECT;
    if (!m->test) { if (key == TK_OK) m->test = true; return TK_FX_NONE; }
    if (key == TK_DOWN) { m->mac = !m->mac; return TK_FX_SAVE_OS; }
    if (!m->ready || m->passkey_valid) return TK_FX_NONE;
    if (key == TK_UP) return TK_FX_VOLUME;
    return key == TK_OK ? TK_FX_PASTE : TK_FX_NONE;
}
bool tk_hid_ready(bool encrypted, bool authenticated, unsigned subscribed, bool report_mode, bool suspended)
{
    unsigned keyboard = report_mode ? 1 : 4;
    return encrypted && authenticated && !suspended && (subscribed & keyboard) && (subscribed & 2);
}
bool tk_hid_packet(int report, int modifier, int usage, uint8_t out[8], unsigned *length)
{
    if (!out || !length || modifier < 0 || modifier > 255 || usage < 0) return false;
    memset(out, 0, 8);
    if (report == 1 && usage <= 0x73) { out[0] = modifier; out[2] = usage; *length = 8; return true; }
    if (report == 2 && modifier == 0 && usage <= 0x3ff) {
        out[0] = usage; out[1] = usage >> 8; *length = 2; return true;
    }
    return false;
}
int tk_pairing_choice(bool pending, bool physical, int key)
{
    if (!pending || !physical) return 0;
    return key == TK_OK ? 1 : key == TK_LONG_UP ? 2 : 0;
}
bool tk_pairing_token_valid(bool pending, uint32_t current, uint32_t requested)
{
    return pending && current != 0 && current == requested;
}
tk_reconnect_phase_t tk_reconnect_phase(uint32_t now, uint32_t started)
{
    uint32_t elapsed = now - started;
    return elapsed < TK_DIRECTED_MS ? TK_RC_DIRECTED : elapsed < TK_RECONNECT_MS ? TK_RC_FILTERED : TK_RC_IDLE;
}
