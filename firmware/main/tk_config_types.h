#pragma once
#include "tk_hid_map.h"
enum { TK_CFG_MAX=4000, TK_CFG_GROUPS=6, TK_CFG_CARDS=3, TK_CFG_RECORD_MAX=4016 };
typedef struct { char title[48],name[96],line[192],qr[512]; } tk_card_t;
// No internal pointers: validated configuration can be staged and copied atomically.
typedef struct { char label[33],text[65]; uint16_t media,key[2]; uint8_t kind,mask,mod[2]; } tk_cfg_slot_t;
typedef struct { char name[33]; tk_cfg_slot_t slots[3]; } tk_cfg_group_t;
typedef struct tk_custom { int group_count,card_count; tk_cfg_group_t groups[6]; tk_card_t cards[3]; } tk_custom_t;
