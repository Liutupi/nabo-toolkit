#pragma once
#include "tk_hid_map.h"
#include "tk_config_types.h"
#include "tk_probe_model.h"
#include <stdint.h>

typedef enum { TK_PAGE_BOOT, TK_PAGE_MENU, TK_PAGE_MACRO, TK_PAGE_PPT, TK_PAGE_MEET,
               TK_PAGE_MEDIA, TK_PAGE_CAM, TK_PAGE_CARD, TK_PAGE_CONN, TK_PAGE_SET } tk_page_t;
typedef struct { bool used; char name[96]; int os; } tk_slot_t;
typedef struct { int type, kind, mod, usage, frequency, ms; uint8_t bytes[8]; int length; char label[192]; } tk_effect_t;
enum { TK_EFFECT_HID=1, TK_EFFECT_BEEP, TK_EFFECT_VOICE, TK_EFFECT_MAX=128 };
typedef struct { int count; bool overflow; tk_effect_t items[TK_EFFECT_MAX]; } tk_effects_t;
typedef struct {
    int page, menu; int64_t last_input, boot_start; bool boot_voiced;
    tk_slot_t slots[3]; int bind_order[3], bind_count, active; bool connected;
    bool pairing; int64_t pair_until; bool passkey_valid; uint32_t passkey;
    int conn_sel, confirm_del; bool os_pick; int os_slot, os_sel;
    bool beep, voice; int talk, sleep, set_sel;
    bool ppt_running; int64_t ppt_start, ppt_acc; int ppt_pages; bool ppt_black;
    int meet_app, cam_delay; int64_t cam_end; int cam_last_sec, burst_left;
    int64_t next_shot; int shots, macro_group, card_idx; bool card_zoom;
    tk_card_t cards[3]; int card_count;
    bool toast; char toast_text[256]; bool toast_error; int64_t toast_until;
    bool react; int react_key; int64_t react_until;
    bool hit; int hit_key; int64_t hit_until;
    const tk_custom_t *config; // UI-owned immutable committed configuration; NULL = author defaults.
} tk_state_t;

void tk_model_init(tk_state_t *s, int64_t now); // Real device starts with empty slots, disconnected.
void tk_model_press(tk_state_t *s, tk_key_t key, int64_t now, tk_effects_t *out);
void tk_model_tick(tk_state_t *s, int64_t now, tk_effects_t *out);
void tk_model_event(tk_state_t *s, const char *event, int64_t now, const char *arg);
bool tk_model_sleep_due(const tk_state_t *s, int64_t now);
int64_t tk_model_ppt_elapsed(const tk_state_t *s, int64_t now);
tk_os_t tk_model_os(const tk_state_t *s);
void tk_model_apply_config(tk_state_t *s,const tk_custom_t *config);
int tk_model_macro_count(const tk_state_t *s);
const char *tk_model_macro_name(const tk_state_t *s,int group);
tk_binding_t tk_model_macro_binding(const tk_state_t *s,int group,int column);
extern const tk_card_t tk_default_cards[3];
extern const char *const tk_page_names[10], *const tk_key_names[6];
