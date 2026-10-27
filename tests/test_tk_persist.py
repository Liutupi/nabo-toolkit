import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import unittest
from tk_native import ROOT,State,unload
class SettingsPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();p=Path(cls.temp.name)/'persist.so'
        subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror','-std=c11','-I',str(ROOT/'tests/support'),'-I',str(ROOT/'firmware/main'),
                        str(ROOT/'firmware/main/tk_persist.c'),str(ROOT/'tests/tk_store_mock.c'),'-o',str(p)],check=True)
        cls.lib=C.CDLL(str(p));cls.lib.tk_persist_load.argtypes=[C.POINTER(State)];cls.lib.tk_persist_save.argtypes=[C.POINTER(State)]
        cls.lib.tk_mock_blob.argtypes=[C.c_char_p,C.POINTER(C.c_ubyte),C.c_uint];cls.lib.tk_mock_dump.argtypes=[C.c_char_p,C.POINTER(C.c_ubyte)]
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def setUp(self):self.lib.tk_mock_reset()
    def test_settings_roundtrip_and_missing_store_preserve_defaults(self):
        s=State(beep=True,voice=True,talk=1,sleep=3);self.assertEqual(self.lib.tk_persist_load(C.byref(s)),0)
        s.beep=False;s.talk=6;s.sleep=2;self.assertEqual(self.lib.tk_persist_save(C.byref(s)),0)
        restored=State();self.assertEqual(self.lib.tk_persist_load(C.byref(restored)),0)
        self.assertEqual((restored.beep,restored.voice,restored.talk,restored.sleep),(False,True,6,2))
    def test_corrupt_or_short_blob_never_partially_applies_settings(self):
        s=State(beep=True,voice=True,talk=1,sleep=3);before=bytes(s)
        for data in [b'TKS',b'TKS\x01'+bytes(8)]:
            out=(C.c_ubyte*len(data)).from_buffer_copy(data);self.lib.tk_mock_blob(b'settings_v1',out,len(data))
            self.assertNotEqual(self.lib.tk_persist_load(C.byref(s)),0);self.assertEqual(bytes(s),before)
    def test_storage_failure_is_reported_and_invalid_values_are_not_written(self):
        s=State(beep=True,voice=False,talk=1,sleep=3)
        for stage in (1,2):self.lib.tk_mock_fail(stage);self.assertNotEqual(self.lib.tk_persist_save(C.byref(s)),0)
        self.lib.tk_mock_fail(0);s.talk=9;self.assertNotEqual(self.lib.tk_persist_save(C.byref(s)),0)
