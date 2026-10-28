"""Exercise the production display adapter against instrumented host drivers."""
import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import unittest
from tk_native import ROOT,unload

class DisplayDeviceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();folder=Path(cls.temp.name)
        headers={
            'bsp_display.h':'#include <stdint.h>\nvoid *bsp_display_panel(void);\nvoid *bsp_display_io(void);\nvoid bsp_display_backlight(uint8_t percent);\n',
            'esp_heap_caps.h':'#include <stddef.h>\n#define MALLOC_CAP_DMA 1\n#define MALLOC_CAP_INTERNAL 2\nvoid *heap_caps_malloc(size_t size,unsigned flags);\n',
            'esp_lcd_panel_io.h':'#include <stddef.h>\n#include "esp_err.h"\nesp_err_t esp_lcd_panel_io_tx_param(void *io,int cmd,const void *param,size_t size);\n',
            'esp_lcd_panel_ops.h':'#include "esp_err.h"\n#include <stdlib.h>\n#define ESP_ERROR_CHECK(x) do {if((x)!=ESP_OK)abort();}while(0)\nesp_err_t esp_lcd_panel_draw_bitmap(void *panel,int x,int y,int x1,int y1,const void *pixels);\n',
            'esp_timer.h':'#include <stdint.h>\nint64_t esp_timer_get_time(void);\n',
        }
        for name,text in headers.items():(folder/name).write_text(text,encoding='utf-8')
        dest=folder/'display.so';main=ROOT/'firmware/main'
        compiled=subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror','-std=c11','-DLV_CONF_SKIP','-DLV_LVGL_H_INCLUDE_SIMPLE',
            '-I',str(folder),'-I',str(ROOT/'tests/support'),'-I',str(main),'-I',str(ROOT/'firmware/managed_components/lvgl__lvgl'),
            '-I',str(ROOT/'firmware/components/qrcodegen'),str(main/'tk_f1_ui_device.c'),str(ROOT/'tests/tk_display_device_host.c'),'-o',str(dest)],
            capture_output=True,encoding='utf-8',errors='replace')
        if compiled.returncode:raise RuntimeError(compiled.stderr)
        cls.lib=C.CDLL(str(dest));cls.lib.tk_f1_ui_open.restype=C.c_bool
        cls.lib.tk_display_host_draw.argtypes=[C.c_int,C.c_int,C.c_int64];cls.lib.tk_display_host_draw.restype=C.c_int
        cls.lib.tk_display_host_events.restype=C.c_char_p
        if not cls.lib.tk_f1_ui_open():raise RuntimeError('Host display allocation failed')
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def setUp(self):
        self.assertTrue(self.lib.tk_display_host_draw(0,0,0))
        self.assertTrue(self.lib.tk_display_host_draw(1,0,1))
        self.lib.tk_display_host_reset()
    def test_dark_remote_skips_frames_animation_and_lcd_even_as_time_advances(self):
        for now in range(30000,90000,1000):self.assertTrue(self.lib.tk_display_host_draw(1,0,now))
        self.assertEqual(self.lib.tk_display_host_frames(),0)
        self.assertEqual(self.lib.tk_display_host_sends(),0)
        self.assertEqual(self.lib.tk_display_host_fences(),0)
        self.assertEqual(self.lib.tk_display_host_light(),0)
        self.assertEqual(self.lib.tk_display_host_events(),b'')
    def test_wake_invalidates_and_fences_the_full_frame_before_backlight(self):
        self.assertTrue(self.lib.tk_display_host_draw(0,0,60000))
        self.assertEqual(self.lib.tk_display_host_events(),b'IRSFCL')
        self.assertEqual(self.lib.tk_display_host_invalidates(),1)
        self.assertEqual(self.lib.tk_display_host_light(),80)
        self.lib.tk_display_host_reset();self.assertTrue(self.lib.tk_display_host_draw(0,0,60016))
        self.assertEqual(self.lib.tk_display_host_invalidates(),0)
        self.assertNotIn(b'L',self.lib.tk_display_host_events())
    def test_failed_wake_keeps_backlight_dark_and_retry_repaints_before_light(self):
        self.assertFalse(self.lib.tk_display_host_draw(0,1,60000))
        self.assertEqual(self.lib.tk_display_host_events(),b'IR')
        self.assertEqual(self.lib.tk_display_host_light(),0)
        self.assertEqual(self.lib.tk_display_host_sends(),0)
        self.lib.tk_display_host_reset();self.assertTrue(self.lib.tk_display_host_draw(0,0,60016))
        self.assertEqual(self.lib.tk_display_host_events(),b'IRSFCL')
        self.assertEqual(self.lib.tk_display_host_light(),80)
