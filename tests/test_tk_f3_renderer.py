import ctypes as C
import test_tk_renderer as base
from tk_native import State

class AnimatedRendererTests(base.RendererTests):
    F3=True
    def test_boot_wordmark_has_all_four_large_latin_glyphs(self):
        self.assertGreater(self.lib.tk_render_wordmark_width(),60)
    def test_every_animation_change_and_boot_phase_matches_full_dirty_pixels(self):
        dirty=self.lib.tk_render_new(C.byref(self.assets));full=self.lib.tk_render_new(C.byref(self.assets));s=State()
        self.lib.tk_host_demo(C.byref(s),1)
        try:
            for page in [0,1,2,3,4,5,6,7]:
                s.page=page;s.boot_start=0
                for now in [0,150,400,701,1050,1399,1400,1450,1700,2199,2200,2349,2350,2500,3000,4042,5400,5500,6000,10000]:
                    self.assertTrue(self.lib.tk_render_frame(dirty,C.byref(s),now,False,0),(page,now))
                    self.assertTrue(self.lib.tk_render_frame(full,C.byref(s),now,True,0))
                    self.assertEqual(self.image(dirty),self.image(full),(page,now))
                    self.assertLessEqual(self.lib.tk_render_ops(dirty),128)
            s.page=2
            self.lib.tk_render_frame(dirty,C.byref(s),250,True,0);a=self.image(dirty)
            self.lib.tk_render_frame(dirty,C.byref(s),1500,False,0);self.assertNotEqual(a,self.image(dirty))
        finally:self.lib.tk_render_free(dirty);self.lib.tk_render_free(full)
