"""Exercise the real UI/audio adapter with deterministic runtime/sound providers."""
import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import unittest
from tk_native import ROOT,State,Effects,unload


class VoiceBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();dest=Path(cls.temp.name)/'bridge.so'
        source=ROOT/'firmware/main'
        subprocess.run(['cc','-std=c11','-shared','-fPIC','-Wall','-Wextra','-Werror',
            '-I',str(ROOT/'tests/support'),'-I',str(source),'-I',str(ROOT/'tools/voice_probe'),
            *[str(source/n) for n in ['tk_model.c','tk_model_config.c','tk_model_tools.c',
              'tk_model_connection.c','tk_hid_map.c','tk_voice_bridge.c']],
            str(ROOT/'tests/tk_voice_bridge_host.c'),'-o',str(dest)],check=True)
        cls.lib=C.CDLL(str(dest));l=cls.lib
        l.tk_model_init.argtypes=[C.POINTER(State),C.c_int64]
        l.tk_model_press.argtypes=[C.POINTER(State),C.c_int,C.c_int64,C.POINTER(Effects)]
        l.tk_voice_bridge_init.argtypes=[C.POINTER(State)]
        l.tk_voice_bridge_tick.argtypes=[C.POINTER(State),C.c_int64,C.c_bool,C.c_bool]
        l.tk_voice_bridge_command.argtypes=[C.POINTER(State),C.c_char_p,C.c_int64,C.c_bool,C.POINTER(Effects)]
        l.tk_voice_bridge_command.restype=C.c_bool
        l.tk_voice_bridge_busy.restype=l.vb_muted.restype=C.c_bool
        l.vb_ready.argtypes=[C.c_bool];l.vb_count.argtypes=[C.c_uint,C.c_uint]
        l.vb_finish.argtypes=[C.c_int,C.c_int,C.c_int,C.c_uint]

    @classmethod
    def tearDownClass(cls):
        unload(cls.lib);cls.temp.cleanup()

    def setUp(self):
        self.state=State();self.out=Effects()
        self.lib.tk_model_init(C.byref(self.state),0);self.state.page=1
        self.assertEqual(self.lib.tk_voice_bridge_init(C.byref(self.state)),0)

    def command(self,text,now=10,allowed=True):
        return self.lib.tk_voice_bridge_command(C.byref(self.state),text.encode(),now,allowed,C.byref(self.out))

    def tick(self,now,allowed=True,muted=False):
        self.lib.tk_voice_bridge_tick(C.byref(self.state),now,allowed,muted)

    def start_enroll(self):
        self.command('>tk.voice.enroll=0');self.tick(20);self.tick(61)
        self.assertEqual(self.lib.vb_requested(),1)

    def test_writer_quiescence_is_required_before_microphone_start(self):
        self.command('>tk.voice.enroll=0');self.lib.vb_ready(False)
        self.tick(20);self.tick(100)
        self.assertTrue(self.lib.vb_muted());self.assertEqual(self.lib.vb_requested(),0)
        self.lib.vb_ready(True);self.tick(110);self.tick(149)
        self.assertEqual(self.lib.vb_requested(),0)
        self.tick(150);self.assertEqual(self.lib.vb_requested(),1)
        self.lib.vb_phase(3);self.tick(151)
        self.assertEqual(self.state.voice_status,2)
        self.lib.vb_finish(0,0,0,1);self.tick(200)
        self.assertFalse(self.lib.vb_muted());self.assertFalse(self.state.voice_busy)
        self.assertEqual((self.state.voice_counts[0],self.state.voice_status),(1,3))

    def test_faulty_audio_writer_has_a_bounded_prepare_timeout(self):
        self.command('>tk.voice.enroll=0');self.lib.vb_ready(False)
        self.tick(20);self.tick(1519)
        self.assertTrue(self.state.voice_busy);self.assertEqual(self.lib.vb_requested(),0)
        self.tick(1520)
        self.assertFalse(self.state.voice_busy);self.assertFalse(self.lib.vb_muted())
        self.assertEqual(self.state.voice_status,11)

    def test_cancelled_late_result_does_not_jump_or_unmute_before_read_finishes(self):
        self.start_enroll()
        self.lib.tk_model_press(C.byref(self.state),3,70,C.byref(self.out))
        self.tick(71);self.assertGreater(self.lib.vb_cancelled(),0)
        self.assertTrue(self.lib.vb_muted());self.assertTrue(self.lib.tk_voice_bridge_busy())
        self.lib.vb_finish(0,0,0,1);self.tick(90)
        self.assertEqual(self.state.page,1);self.assertFalse(self.lib.vb_muted())

    def test_recognition_only_navigates_after_terminal_result(self):
        self.lib.vb_count(3,1);self.tick(1)
        self.command('>tk.voice.listen');self.tick(20);self.tick(61)
        self.assertEqual(self.state.page,10)
        self.lib.vb_finish(0,3,0,1);self.tick(100)
        self.assertEqual(self.state.page,7);self.assertFalse(self.lib.tk_voice_bridge_busy())

    def test_external_diagnostic_mute_survives_voice_cancellation(self):
        self.start_enroll();self.tick(70,allowed=False,muted=True)
        self.assertFalse(self.state.voice_busy);self.assertTrue(self.lib.vb_muted())
        self.lib.vb_finish(1,-1,0,0);self.tick(90,allowed=False,muted=True)
        self.assertTrue(self.lib.vb_muted())

    def test_failure_stages_and_ambiguity_are_not_silent_page_jumps(self):
        for decision,stage,status in [(7,0,9),(3,0,10),(1,2,11),(1,3,5)]:
            self.setUp();self.start_enroll();self.lib.vb_finish(decision,-1,stage,0);self.tick(90)
            self.assertEqual((self.state.page,self.state.voice_status),(10,status))
            self.assertFalse(self.state.voice_busy)

    def test_invalid_or_disallowed_serial_command_has_no_navigation_effect(self):
        for text in ('>tk.voice.bad','>tk.voice.enroll=7','>tk.voice.enroll=00'):
            self.assertTrue(self.command(text));self.assertEqual(self.state.page,1)
        self.assertTrue(self.command('>tk.voice.open',allowed=False));self.assertEqual(self.state.page,1)

    def test_seventh_target_enrolls_and_retains_other_counts(self):
        for i,n in enumerate((3,3,3,3,1,0,0)):self.lib.vb_count(i,n)
        self.assertTrue(self.command('>tk.voice.enroll=6'))
        self.assertEqual(self.state.voice_selected,6)
        self.tick(20);self.tick(61)
        self.assertEqual(self.lib.vb_requested(),1)
        self.lib.vb_finish(0,6,0,1);self.tick(100)
        self.assertEqual(list(self.state.voice_counts),[3,3,3,3,1,0,1])
        self.assertFalse(self.state.voice_busy)

    def test_explicit_maintenance_is_gated_and_does_not_navigate_or_capture(self):
        self.command('>tk.voice.compact',allowed=False)
        self.assertEqual(self.lib.vb_compacted(),0)
        self.command('>tk.voice.compact')
        self.assertEqual(self.lib.vb_compacted(),1)
        self.assertEqual((self.state.page,self.lib.vb_requested()),(1,0))
        self.start_enroll();self.command('>tk.voice.compact')
        self.assertEqual(self.lib.vb_compacted(),1)


if __name__=='__main__':unittest.main()
