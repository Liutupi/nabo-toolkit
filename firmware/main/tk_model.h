#pragma once
#include "tk_hid_map.h"
#include "tk_config_types.h"
#include "tk_probe_model.h"
#include <stdint.h>

typedef enum { TK_PAGE_BOOT, TK_PAGE_MENU, TK_PAGE_MACRO, TK_PAGE_PPT, TK_PAGE_MEET,
               TK_PAGE_MEDIA, TK_PAGE_CAM, TK_PAGE_CARD, TK_PAGE_CONN, TK_PAGE_SET, TK_PAGE_VOICE } tk_page_t;

enum { TK_VOICE_TARGETS=7 };
typedef enum { TK_VOICE_NONE, TK_VOICE_RECOGNIZE, TK_VOICE_ENROLL } tk_voice_operation_t;
typedef enum { TK_VOICE_READY, TK_VOICE_LISTENING, TK_VOICE_RECORDING, TK_VOICE_SAVED,
    TK_VOICE_REJECTED, TK_VOICE_ERROR, TK_VOICE_UNTRAINED, TK_VOICE_MISSING_GROUP,
    TK_VOICE_PREPARING, TK_VOICE_AMBIGUOUS, TK_VOICE_TOO_LONG, TK_VOICE_CAPTURE_ERROR } tk_voice_status_t;
typedef enum { TK_VOICE_RESULT_ENROLLED, TK_VOICE_RESULT_MATCHED, TK_VOICE_RESULT_REJECTED,
    TK_VOICE_RESULT_ERROR, TK_VOICE_RESULT_AMBIGUOUS, TK_VOICE_RESULT_TOO_LONG,
    TK_VOICE_RESULT_CAPTURE_ERROR } tk_voice_outcome_t;
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
    bool remote_dim, screen_off;
    int64_t screen_since;
    int media_mode;
    bool media_select;
    int voice_selected;
    uint8_t voice_counts[TK_VOICE_TARGETS];
    bool voice_busy;
    int voice_operation, voice_status;
    uint32_t voice_token;
} tk_state_t;

void tk_model_init(tk_state_t *s, int64_t now); // Real device starts with empty slots, disconnected.
void tk_model_press(tk_state_t *s, tk_key_t key, int64_t now, tk_effects_t *out);
void tk_model_tick(tk_state_t *s, int64_t now, tk_effects_t *out);
void tk_model_event(tk_state_t *s, const char *event, int64_t now, const char *arg);
bool tk_model_sleep_due(const tk_state_t *s, int64_t now);
void tk_model_screen_reset(tk_state_t *s, int64_t now);
bool tk_model_voice_open(tk_state_t *s,int64_t now);
bool tk_model_voice_templates(tk_state_t *s,const uint8_t counts[TK_VOICE_TARGETS]);
bool tk_model_voice_progress(tk_state_t *s,uint32_t token,int status,int64_t now);
bool tk_model_voice_result(tk_state_t *s,uint32_t token,int outcome,int target,int count,int64_t now);
int64_t tk_model_ppt_elapsed(const tk_state_t *s, int64_t now);
tk_os_t tk_model_os(const tk_state_t *s);
void tk_model_apply_config(tk_state_t *s,const tk_custom_t *config);
int tk_model_macro_count(const tk_state_t *s);
const char *tk_model_macro_name(const tk_state_t *s,int group);
tk_binding_t tk_model_macro_binding(const tk_state_t *s,int group,int column);
extern const tk_card_t tk_default_cards[3];
extern const char *const tk_page_names[11], *const tk_key_names[6], *const tk_voice_names[TK_VOICE_TARGETS];
