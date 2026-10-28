set(TK_COMMON "tk_ble.c" "tk_ble_hid.c" "tk_ble_diag.c" "tk_probe_model.c" "tk_gfx.c" "tk_shapes.c" "tk_text.c")
if(CONFIG_NABO_TOOLKIT_F1)
    set(TK_APPLICATION "tk_f1_main.c" "tk_f1_ui_device.c" "tk_f1_assets.c" "tk_sound.c" "tk_persist.c"
        "tk_model.c" "tk_model_config.c" "tk_model_tools.c" "tk_model_connection.c" "tk_hid_map.c" "tk_slots.c" "tk_ble_slots.c"
        "tk_ui.c" "tk_ui_animation.c" "tk_ui_tools.c" "tk_ui_connection.c" "tk_ui_card.c" "tk_qr.c"
        "../fonts/tk_font_12.c" "../fonts/tk_font_16.c" "../fonts/tk_font_18.c" "../fonts/tk_font_28.c" "../fonts/tk_font_48.c" "../fonts/tk_font_cjk.c")
    set(TK_EMBED "../assets/placeholder_avatar.rgb565" "../assets/placeholder_avatar.alpha"
        "../assets/placeholder_bust.rgb565" "../assets/placeholder_bust.alpha"
        "../assets/placeholder_welcome.rgb565" "../assets/placeholder_welcome.alpha")
else()
    set(TK_APPLICATION "tk_main.c" "tk_probe_ui.c")
endif()
if(CONFIG_NABO_TOOLKIT_F3)
    list(REMOVE_ITEM TK_APPLICATION "../fonts/tk_font_cjk.c" "tk_sound.c")
    list(APPEND TK_APPLICATION "../fonts/tk_font_cjk_compact.c" "tk_cjk_compact.c" "tk_animation.c" "tk_audio_mix.c" "tk_sound_f3.c")
    set(TK_EMBED "../assets/animations.bin" "../assets/boot-welcome.pcm")
endif()
if(CONFIG_NABO_TOOLKIT_F2)
    list(APPEND TK_APPLICATION "tk_config_lex.c" "tk_config_parse.c" "tk_config_json.c" "tk_config_store.c" "tk_config_serial.c" "tk_usb_console.c")
    set_source_files_properties("tk_config_lex.c" "tk_config_parse.c" "tk_config_json.c" "tk_config_store.c"
        PROPERTIES COMPILE_OPTIONS "-Os")
endif()
if(CONFIG_NABO_TOOLKIT_VOICE)
    list(APPEND TK_APPLICATION "tk_voice.c" "tk_voice_store.c" "tk_voice_capture.c" "tk_voice_bridge.c"
        "../../tools/voice_probe/features.c" "../../tools/voice_probe/matcher.c")
    # Storage/control are not frame-time hot paths; preserve -O2 for DSP/rendering.
    set_source_files_properties("tk_voice.c" "tk_voice_store.c" "tk_voice_bridge.c"
        PROPERTIES COMPILE_OPTIONS "-Os")
endif()
# IDF expands requirements before CONFIG_* exists; unused libraries are discarded.
idf_component_register(
    SRCS ${TK_COMMON} ${TK_APPLICATION}
    INCLUDE_DIRS "." "../../tools/voice_probe"
    REQUIRES bsp lvgl esp_lcd esp_timer nvs_flash bt qrcodegen esp_driver_gpio espressif__cjson esp_driver_usb_serial_jtag
    EMBED_FILES ${TK_EMBED}
)
target_compile_options(${COMPONENT_LIB} PRIVATE -O2)
if(CONFIG_NABO_TOOLKIT_F3)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE TK_F3=1 TK_COMPACT_CJK=1)
endif()
