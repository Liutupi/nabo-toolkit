import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from tk_native import ROOT, State, Effects, Custom, OS, KEYS, unload, configure

class Picture(C.Structure):
    _fields_=[('pixels',C.POINTER(C.c_uint16)),('alpha',C.POINTER(C.c_uint8)),('w',C.c_int),('h',C.c_int)]
class Assets(C.Structure):
    _fields_=[('avatar',Picture),('bust',Picture),('welcome',Picture),('animation',C.c_void_p),('bank',C.c_void_p)]
class RendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lvgl=ROOT/'firmware/managed_components/lvgl__lvgl'
        if not (lvgl/'lvgl.h').exists():raise unittest.SkipTest('Renderer needs managed LVGL headers: run IDF reconfigure first')
        cls.temp=tempfile.TemporaryDirectory();dest=Path(cls.temp.name)/'renderer.so';main=ROOT/'firmware/main'
        source=['tk_model.c','tk_model_config.c','tk_model_tools.c','tk_model_connection.c','tk_hid_map.c','tk_ui.c','tk_ui_animation.c','tk_ui_tools.c','tk_ui_connection.c','tk_ui_card.c','tk_qr.c','tk_gfx.c','tk_shapes.c','tk_text.c']
        f3=getattr(cls,'F3',False);flags=['-DTK_F3=1','-DTK_COMPACT_CJK=1'] if f3 else []
        if f3:source+=['tk_animation.c','tk_cjk_compact.c']
        compiled=subprocess.run(['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-std=c11','-DLV_CONF_SKIP','-DLV_LVGL_H_INCLUDE_SIMPLE','-DLV_FONT_FMT_TXT_LARGE=1',*flags,
                        '-I',str(main),'-I',str(lvgl),'-I',str(ROOT/'firmware/components/qrcodegen'),
                        *[str(main/n) for n in source],str(ROOT/'firmware/components/qrcodegen/qrcodegen.c'),
                        *[str(ROOT/f'firmware/fonts/tk_font_{n}.c') for n in (12,16,18,28,48)],
                        str(ROOT/('firmware/fonts/tk_font_cjk_compact.c' if f3 else 'firmware/fonts/tk_font_cjk.c')),
                        str(ROOT/'tests/tk_model_host.c'),str(ROOT/'tests/tk_renderer_host.c'),'-o',str(dest)],capture_output=True,encoding='utf-8',errors='replace')
        if compiled.returncode:raise RuntimeError(compiled.stderr)
        cls.lib=C.CDLL(str(dest));lib=cls.lib
        lib.tk_host_demo.argtypes=[C.POINTER(State),C.c_int]
        lib.tk_model_press.argtypes=[C.POINTER(State),C.c_int,C.c_int64,C.POINTER(Effects)]
        lib.tk_model_tick.argtypes=[C.POINTER(State),C.c_int64,C.POINTER(Effects)]
        lib.tk_model_event.argtypes=[C.POINTER(State),C.c_char_p,C.c_int64,C.c_char_p]
        lib.tk_model_apply_config.argtypes=[C.POINTER(State),C.POINTER(Custom)]
        lib.tk_render_new.argtypes=[C.POINTER(Assets)];lib.tk_render_new.restype=C.c_void_p
        lib.tk_render_free.argtypes=[C.c_void_p]
        lib.tk_render_frame.argtypes=[C.c_void_p,C.POINTER(State),C.c_int64,C.c_bool,C.c_int];lib.tk_render_frame.restype=C.c_bool
        lib.tk_render_pixels.argtypes=[C.c_void_p];lib.tk_render_pixels.restype=C.POINTER(C.c_uint16)
        for name in ('bytes','ops','glyphs','scaled_glyphs'):
            getattr(lib,'tk_render_'+name).argtypes=[C.c_void_p];getattr(lib,'tk_render_'+name).restype=C.c_uint
        lib.tk_render_fallback_glyphs.argtypes=[C.c_void_p];lib.tk_render_fallback_glyphs.restype=C.c_uint
        lib.tk_render_fallback_height.argtypes=[C.c_void_p];lib.tk_render_fallback_height.restype=C.c_uint
        cls.buffers=[];cls.assets=Assets();meta=json.loads((ROOT/'firmware/assets/placeholders.json').read_text())
        for name,item in meta.items():
            pixels=(C.c_uint16*(item['w']*item['h'])).from_buffer_copy((ROOT/f'firmware/assets/placeholder_{name}.rgb565').read_bytes())
            alpha=(C.c_uint8*(item['w']*item['h'])).from_buffer_copy((ROOT/f'firmware/assets/placeholder_{name}.alpha').read_bytes())
            cls.buffers.extend([pixels,alpha]);setattr(cls.assets,name,Picture(pixels,alpha,item['w'],item['h']))
        if f3:
            class Bank(C.Structure):_fields_=[('data',C.POINTER(C.c_uint8)),('bytes',C.c_size_t)]
            data=(ROOT/'firmware/assets/animations.bin').read_bytes();raw=(C.c_uint8*len(data)).from_buffer_copy(data)
            bank=Bank(raw,len(data));cls.buffers.extend([raw,bank]);cls.assets.bank=C.cast(C.pointer(bank),C.c_void_p)
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'lib'):unload(cls.lib);cls.lib=None
        if hasattr(cls,'temp'):cls.temp.cleanup()
    def image(self,h):return C.string_at(self.lib.tk_render_pixels(h),240*320*2)
    def test_incremental_matches_full_pixels_across_all_pages_and_overlays(self):
        dirty=self.lib.tk_render_new(C.byref(self.assets));full=self.lib.tk_render_new(C.byref(self.assets))
        self.assertTrue(dirty and full);s=State();out=Effects();seen=set();frames=0
        try:
            rows=[json.loads(x) for x in (ROOT/'tests/tk_golden/traces.jsonl').read_text(encoding='utf-8').splitlines()]
            for index,row in enumerate(rows):
                call=row['call'];now=row['now'];kind=call['type']
                if kind=='init':self.lib.tk_host_demo(C.byref(s),OS.index(call['os']))
                elif kind=='press':self.lib.tk_model_press(C.byref(s),KEYS.index(call['key']),now,C.byref(out))
                elif kind=='tick':self.lib.tk_model_tick(C.byref(s),now,C.byref(out))
                elif kind=='config':configure(self.lib,s,call['config'])
                else:
                    arg=call.get('arg');arg=f'{arg:06d}' if call['event']=='passkey' and isinstance(arg,int) else arg
                    self.lib.tk_model_event(C.byref(s),call['event'].encode(),now,str(arg).encode() if arg is not None else None)
                key=(s.page,s.pairing,s.passkey_valid,s.os_pick,s.confirm_del>=0,s.card_zoom,s.cam_end>0,s.ppt_black,
                     s.media_mode,s.media_select,s.screen_off)
                if key in seen and index%19:continue
                seen.add(key);frames+=1
                self.assertTrue(self.lib.tk_render_frame(dirty,C.byref(s),now,False,0),(row['scenario'],row['step']))
                self.assertTrue(self.lib.tk_render_frame(full,C.byref(s),now,True,0))
                self.assertEqual(self.image(dirty),self.image(full),(row['scenario'],row['step']))
                self.assertLessEqual(self.lib.tk_render_ops(dirty),128);self.assertLessEqual(self.lib.tk_render_glyphs(dirty),320)
            self.assertEqual({x[0] for x in seen},set(range(10)));self.assertGreater(frames,80)
            self.assertTrue(self.lib.tk_render_frame(dirty,C.byref(s),now,False,0));self.assertTrue(self.lib.tk_render_frame(full,C.byref(s),now,True,0));self.assertEqual(self.image(dirty),self.image(full))
            self.assertTrue(self.lib.tk_render_frame(dirty,C.byref(s),now,False,0));self.assertEqual(self.lib.tk_render_bytes(dirty),0)
        finally:self.lib.tk_render_free(dirty);self.lib.tk_render_free(full)
    def test_six_digit_pair_code_is_squeezed_without_dropping_digits(self):
        h=self.lib.tk_render_new(C.byref(self.assets));s=State();self.lib.tk_host_demo(C.byref(s),0)
        s.page=8;s.pairing=True;s.pair_until=60000;s.passkey_valid=True;s.passkey=888888
        try:
            self.assertTrue(self.lib.tk_render_frame(h,C.byref(s),20,True,1))
            self.assertEqual(self.lib.tk_render_scaled_glyphs(h),6)
        finally:self.lib.tk_render_free(h)
    def test_media_modes_and_screen_off_wake_incremental_match_full(self):
        dirty=self.lib.tk_render_new(C.byref(self.assets));full=self.lib.tk_render_new(C.byref(self.assets))
        self.assertTrue(dirty and full);s=State();self.lib.tk_host_demo(C.byref(s),0)
        try:
            s.page=5
            for selecting,mode in [(True,0),(True,1),(False,0),(False,1)]:
                s.media_select=selecting;s.media_mode=mode
                self.assertTrue(self.lib.tk_render_frame(dirty,C.byref(s),10,False,0))
                self.assertTrue(self.lib.tk_render_frame(full,C.byref(s),10,True,0))
                self.assertEqual(self.image(dirty),self.image(full),(selecting,mode))
            s.screen_off=True;s.toast=True;s.os_pick=True
            self.assertTrue(self.lib.tk_render_frame(dirty,C.byref(s),10,False,0))
            self.assertTrue(self.lib.tk_render_frame(full,C.byref(s),10,True,0))
            self.assertEqual(self.image(dirty),bytes(240*320*2),'Screen-off must remain fully black, including overlays')
            self.assertEqual(self.image(dirty),self.image(full))
            self.assertEqual(self.lib.tk_render_glyphs(dirty),0)
            s.screen_off=False;s.toast=False;s.os_pick=False
            self.assertTrue(self.lib.tk_render_frame(dirty,C.byref(s),10,False,0))
            self.assertTrue(self.lib.tk_render_frame(full,C.byref(s),10,True,0))
            self.assertEqual(self.image(dirty),self.image(full));self.assertNotEqual(self.image(dirty),bytes(240*320*2))
        finally:self.lib.tk_render_free(dirty);self.lib.tk_render_free(full)
    def test_custom_chinese_labels_use_flash_fallback_and_dirty_matches_full(self):
        from test_tk_config import example
        h=self.lib.tk_render_new(C.byref(self.assets));full=self.lib.tk_render_new(C.byref(self.assets));s=State();self.lib.tk_host_demo(C.byref(s),0)
        cfg=example();cfg['groups'][0]['name']='獭貘鸮';cfg['cards'][0]['name']='我的办公室';configure(self.lib,s,cfg);s.page=2
        try:
            self.assertTrue(self.lib.tk_render_frame(h,C.byref(s),0,False,0));self.assertGreaterEqual(self.lib.tk_render_fallback_glyphs(h),3)
            self.assertGreaterEqual(self.lib.tk_render_fallback_height(h),16,'18px fallback labels must not shrink to font-wide bounding-box metrics')
            s.page=7;self.assertTrue(self.lib.tk_render_frame(h,C.byref(s),0,False,0));self.assertTrue(self.lib.tk_render_frame(full,C.byref(s),0,True,0));self.assertEqual(self.image(h),self.image(full))
        finally:self.lib.tk_render_free(h);self.lib.tk_render_free(full)
    def test_same_size_qr_payload_change_repaints_and_original_atlas_hashes_stay_bound(self):
        h=self.lib.tk_render_new(C.byref(self.assets));full=self.lib.tk_render_new(C.byref(self.assets));s=State();self.lib.tk_host_demo(C.byref(s),0);s.page=7;s.card_zoom=True
        try:
            self.assertTrue(self.lib.tk_render_frame(h,C.byref(s),0,False,0));before=self.image(h)
            s.cards[0].qr=b'https://example.org/nabo'
            self.assertTrue(self.lib.tk_render_frame(h,C.byref(s),0,False,0));self.assertTrue(self.lib.tk_render_frame(full,C.byref(s),0,True,0))
            self.assertNotEqual(before,self.image(h));self.assertEqual(self.image(h),self.image(full))
        finally:self.lib.tk_render_free(h);self.lib.tk_render_free(full)
        meta=json.loads((ROOT/'firmware/assets/placeholders.json').read_text())
        for item in meta.values():self.assertEqual(hashlib.sha256((ROOT/item['source']).read_bytes()).hexdigest(),item['source_sha256'])
