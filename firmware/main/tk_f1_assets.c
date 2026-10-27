#include "tk_ui.h"
#ifdef TK_F3
#include "../assets/runtime.h"
extern const uint8_t _binary_animations_bin_start[];
static tk_animation_t animation;
static const tk_animation_bank_t bank={_binary_animations_bin_start,TK_ANIMATION_BANK_BYTES};
const tk_ui_assets_t tk_f1_assets={.animation=&animation,.bank=&bank};
#else
#define PICTURE(name,wid,hei) \
    extern const uint8_t _binary_placeholder_##name##_rgb565_start[]; \
    extern const uint8_t _binary_placeholder_##name##_alpha_start[]
PICTURE(avatar,64,64);
PICTURE(bust,84,110);
PICTURE(welcome,115,150);
const tk_ui_assets_t tk_f1_assets={
    {(const uint16_t *)_binary_placeholder_avatar_rgb565_start,_binary_placeholder_avatar_alpha_start,64,64},
    {(const uint16_t *)_binary_placeholder_bust_rgb565_start,_binary_placeholder_bust_alpha_start,84,110},
    {(const uint16_t *)_binary_placeholder_welcome_rgb565_start,_binary_placeholder_welcome_alpha_start,115,150},NULL,NULL};
#endif
