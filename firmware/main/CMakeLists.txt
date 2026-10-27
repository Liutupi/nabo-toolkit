idf_component_register(
    SRCS "tk_main.c" "tk_ble.c" "tk_ble_hid.c" "tk_probe_model.c" "tk_probe_ui.c"
         "tk_gfx.c" "tk_shapes.c" "tk_text.c"
    INCLUDE_DIRS "."
    REQUIRES bsp lvgl esp_lcd esp_timer nvs_flash bt
)
target_compile_options(${COMPONENT_LIB} PRIVATE -O2)
