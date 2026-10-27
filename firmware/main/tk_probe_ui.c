// Independent F0 diagnostic page: no Adventure menu/game shell or UI assets.
#include "tk_probe_ui.h"
#include "tk_gfx.h"
#include <stdio.h>
#include <stdlib.h>
#include "bsp_display.h"
#include "esp_heap_caps.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"

static ag_t *s_gfx;
static uint16_t *s_strip[2];
#define INK ag_rgb(20, 32, 58)
#define GOLD ag_rgb(247, 198, 92)
#define PAPER ag_rgb(245, 243, 235)
#define DIM ag_rgb(161, 174, 196)
#define GREEN ag_rgb(89, 203, 167)
static void send_strip(void *ctx, int x, int y, int w, int h, uint16_t *px)
{
    (void)ctx;
    ESP_ERROR_CHECK(esp_lcd_panel_draw_bitmap(bsp_display_panel(), x, y, x + w, y + h, px));
    // Fence DMA before the renderer reuses a stripe.
    ESP_ERROR_CHECK(esp_lcd_panel_io_tx_param(bsp_display_io(), 0x00, NULL, 0));
}
bool tk_probe_ui_open(void)
{
    s_gfx = calloc(1, sizeof(*s_gfx));
    for (int i = 0; i < 2; ++i) s_strip[i] = heap_caps_malloc(240 * AG_STRIP * 2, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    if (!s_gfx || !s_strip[0] || !s_strip[1]) {
        free(s_gfx); s_gfx = NULL;
        for (int i = 0; i < 2; ++i) { free(s_strip[i]); s_strip[i] = NULL; }
        return false;
    }
    ag_init(s_gfx, s_strip[0], s_strip[1], send_strip, NULL);
    return true;
}
static void text(const char *s, int x, int y, uint16_t color)
{
    ag_text(s_gfx, &lv_font_montserrat_14, s, x, y, NT_ALIGN_LEFT, color);
}
static void card(int y, const char *key, const char *label)
{
    ag_rect(s_gfx, 10, y, 220, 34, 8, ag_rgb(34, 49, 76), 255, 0, 0);
    text(key, 18, y + 22, GOLD); text(label, 75, y + 22, PAPER);
}
void tk_probe_ui_draw(const tk_probe_t *m, const char *status, unsigned heap, unsigned largest, unsigned sent, unsigned failed)
{
    ag_t *g = s_gfx;
    char line[64];
    ag_begin(g, m->test ? 1 : 0);
    ag_band(g, 0, 320, INK, INK);
    text("NABO TOOLKIT", 12, 23, PAPER); text("F0", 206, 23, GOLD);
    ag_rect(g, 0, 31, 240, 4, 0, GOLD, 255, 0, 0);
    ag_circle(g, 17, 52, 4, m->ready ? GREEN : GOLD, 255, 0, 0);
    text(status, 29, 57, m->ready ? GREEN : DIM);
    ag_text(g, &lv_font_montserrat_20, m->test ? "Bluetooth test" : "Ready to test", 12, 88, NT_ALIGN_LEFT, PAPER);
    snprintf(line, sizeof(line), "%s / ready in %lu ms", m->mac ? "Mac" : "Win / phone", (unsigned long)m->reconnect_ms);
    text(line, 12, 109, DIM);
    if (m->test) {
        card(121, "UP", "Volume +"); card(161, "OK", m->mac ? "Cmd + V" : "Ctrl + V");
        card(201, "DOWN", "Switch OS");
    } else {
        card(121, "OK", "Open test"); card(161, "Hold DN", "Pair (60 s)"); card(201, "Hold OK", "Reconnect");
    }
    snprintf(line, sizeof(line), "Heap %uK / block %uK", heap / 1024, largest / 1024);
    text(line, 12, 258, heap >= 60 * 1024 && largest >= 30 * 1024 ? GREEN : GOLD);
    snprintf(line, sizeof(line), "Sent %u / failed %u", sent, failed); text(line, 12, 280, DIM);
    text(m->test ? "Hold UP: back  DN: pair" : "F0 diagnostic firmware", 12, 309, PAPER);
    if (m->passkey_valid) {
        ag_rect(g, 10, 91, 220, 140, 14, INK, 255, GOLD, 2);
        text("ENTER ON YOUR DEVICE", 23, 119, PAPER);
        snprintf(line, sizeof(line), "%06lu", (unsigned long)m->passkey);
        ag_text(g, &lv_font_montserrat_28, line, 120, 167, NT_ALIGN_CENTER, GOLD);
        text("Hold UP to cancel", 49, 203, DIM);
    }
    ag_flush(g);
}
