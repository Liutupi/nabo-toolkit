"""Compose the production ADC short/long classifier with the real remote model."""
import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import unittest
from tk_native import ROOT,State,Effects,build,unload

class Buttons(C.Structure):
    _fields_=[('held',C.c_int),('since',C.c_uint32),('fired',C.c_bool)]

class DarkRemoteInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();folder=Path(cls.temp.name)
        cls.model=build(folder);dest=folder/'buttons.so'
        subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror','-std=c11',
            str(ROOT/'firmware/main/tk_probe_model.c'),'-o',str(dest)],check=True)
        cls.buttons=C.CDLL(str(dest));cls.buttons.tk_buttons_init.argtypes=[C.POINTER(Buttons)]
        cls.buttons.tk_button_edge.argtypes=[C.POINTER(Buttons),C.c_int,C.c_bool,C.c_uint32]
        cls.buttons.tk_button_tick.argtypes=[C.POINTER(Buttons),C.c_uint32]
    @classmethod
    def tearDownClass(cls):
        unload(cls.buttons);unload(cls.model);cls.buttons=cls.model=None;cls.temp.cleanup()
    def state(self,page,mode=0):
        s=State();self.model.tk_model_init(C.byref(s),0)
        s.page=page;s.connected=True;s.slots[0].used=True;s.slots[0].os=1
        s.media_select=False;s.media_mode=mode;s.macro_group=3
        out=Effects();self.model.tk_model_tick(C.byref(s),10,C.byref(out))
        return s,out
    def consume(self,s,out,key,now):
        group,mode=s.macro_group,s.media_mode
        self.model.tk_model_press(C.byref(s),key,now,C.byref(out))
        self.assertEqual(out.count,0);self.assertFalse(out.overflow)
        self.assertFalse(s.screen_off);self.assertEqual(s.screen_since,now)
        self.assertEqual((s.macro_group,s.media_mode),(group,mode))
    def test_ticked_long_ok_wakes_once_and_held_release_never_sends_short_ok(self):
        for page,mode in [(2,0),(5,0),(5,1)]:
            with self.subTest(page=page,mode=mode):
                s,out=self.state(page,mode);self.model.tk_model_tick(C.byref(s),30010,C.byref(out))
                self.assertTrue(s.screen_off);b=Buttons();self.buttons.tk_buttons_init(C.byref(b))
                self.assertEqual(self.buttons.tk_button_edge(C.byref(b),2,True,30020),-1)
                self.assertEqual(self.buttons.tk_button_tick(C.byref(b),30519),-1)
                key=self.buttons.tk_button_tick(C.byref(b),30520);self.assertEqual(key,5)
                self.consume(s,out,key,30520)
                self.assertEqual(self.buttons.tk_button_tick(C.byref(b),31020),-1)
                self.assertEqual(self.buttons.tk_button_edge(C.byref(b),2,False,31021),-1)
                self.assertEqual(out.count,0)
    def test_delayed_release_classifies_one_wake_without_prior_timer_tick(self):
        for page in (2,5):
            with self.subTest(page=page):
                s,out=self.state(page);self.model.tk_model_tick(C.byref(s),30010,C.byref(out))
                b=Buttons();self.buttons.tk_buttons_init(C.byref(b))
                self.buttons.tk_button_edge(C.byref(b),2,True,30020)
                key=self.buttons.tk_button_edge(C.byref(b),2,False,30720);self.assertEqual(key,5)
                self.consume(s,out,key,30720)
                self.assertEqual(self.buttons.tk_button_edge(C.byref(b),2,False,30721),-1)
    def test_hold_crossing_screen_deadline_consumes_long_ok_instead_of_group_or_track(self):
        for page in (2,5):
            with self.subTest(page=page):
                s,out=self.state(page);b=Buttons();self.buttons.tk_buttons_init(C.byref(b))
                self.buttons.tk_button_edge(C.byref(b),2,True,29520)
                self.model.tk_model_tick(C.byref(s),30010,C.byref(out));self.assertTrue(s.screen_off)
                key=self.buttons.tk_button_tick(C.byref(b),30020);self.assertEqual(key,5)
                self.consume(s,out,key,30020)
                self.assertEqual(self.buttons.tk_button_edge(C.byref(b),2,False,30100),-1)
