#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef enum { TK_OS_MAC, TK_OS_WIN, TK_OS_IOS, TK_OS_ANDROID } tk_os_t;
typedef enum { TK_PACKET_NONE, TK_PACKET_KEY, TK_PACKET_MEDIA, TK_PACKET_TEXT } tk_packet_kind_t;
typedef struct { int kind, mod, usage; const char *text; } tk_packet_t;
typedef struct { const char *label; tk_packet_t family[2]; } tk_binding_t;
extern const tk_binding_t tk_ppt_bindings[5]; // prev, next, black, end, start
extern const tk_binding_t tk_meeting_bindings[4][3]; // mute, camera, hand
extern const tk_binding_t tk_media_bindings[6]; // tk_key_t order
extern const tk_binding_t tk_macro_bindings[6][3]; // up, OK, down mapped by helper
extern const tk_binding_t tk_shutter_binding;
extern const char *const tk_macro_names[6], *const tk_meeting_names[4], *const tk_os_names[4];
const tk_packet_t *tk_hid_resolve(const tk_binding_t *binding, tk_os_t os);
void tk_hid_chord(const tk_packet_t *packet, tk_os_t os, char *out, size_t size);
void tk_hid_key_name(unsigned usage, char *out, size_t size);
bool tk_hid_char(unsigned char ch, tk_packet_t *out);
unsigned tk_hid_report(const tk_packet_t *packet, uint8_t out[8]);
