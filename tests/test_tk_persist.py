import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import unittest
import zlib
from tk_native import ROOT,State,unload
class SettingsPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();p=Path(cls.temp.name)/'persist.so'
        subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror','-std=c11','-I',str(ROOT/'tests/support'),'-I',str(ROOT/'firmware/main'),
                        str(ROOT/'firmware/main/tk_persist.c'),str(ROOT/'tests/tk_store_mock.c'),'-o',str(p)],check=True)
        cls.lib=C.CDLL(str(p));cls.lib.tk_persist_load.argtypes=[C.POINTER(State)];cls.lib.tk_persist_save.argtypes=[C.POINTER(State)]
        cls.lib.tk_persist_save_remote.argtypes=[C.POINTER(State)]
        cls.lib.tk_mock_blob.argtypes=[C.c_char_p,C.POINTER(C.c_ubyte),C.c_uint];cls.lib.tk_mock_dump.argtypes=[C.c_char_p,C.POINTER(C.c_ubyte)]
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def setUp(self):self.lib.tk_mock_reset()
    def blob(self,name,data):
        out=(C.c_ubyte*len(data)).from_buffer_copy(data);self.lib.tk_mock_blob(name,out,len(data))
    def dump(self,name):
        out=(C.c_ubyte*4016)();n=self.lib.tk_mock_dump(name,out);return bytes(out[:n])
    @staticmethod
    def record(header):return header+zlib.crc32(header).to_bytes(4,'little')
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
    def test_legacy_blob_preserves_new_default_when_remote_record_is_missing(self):
        old=self.record(b'TKS\x01\x00\x01\x06\x02');self.blob(b'settings_v1',old)
        s=State(remote_dim=True);self.assertEqual(self.lib.tk_persist_load(C.byref(s)),0)
        self.assertEqual((s.beep,s.voice,s.talk,s.sleep,s.remote_dim),(False,True,6,2,True))
        self.assertEqual(self.dump(b'settings_v1'),old);self.assertEqual(self.dump(b'remote_v1'),b'')
    def test_remote_setting_roundtrip_does_not_rewrite_old_settings_or_device_data(self):
        old=self.record(b'TKS\x01\x01\x00\x03\x01');self.blob(b'settings_v1',old)
        sentinels={b'slots_v1':b'local-slots-sentinel',b'cfg_v1':b'local-card-config-sentinel'}
        for name,data in sentinels.items():self.blob(name,data)
        for enabled in (False,True):
            s=State(remote_dim=enabled);self.assertEqual(self.lib.tk_persist_save_remote(C.byref(s)),0)
            restored=State(remote_dim=not enabled);self.assertEqual(self.lib.tk_persist_load(C.byref(restored)),0)
            self.assertEqual(restored.remote_dim,enabled);self.assertEqual(self.dump(b'settings_v1'),old)
            self.assertEqual(self.dump(b'remote_v1'),self.record(b'TKR\x01'+bytes([enabled])+b'\0\0\0'))
            for name,data in sentinels.items():self.assertEqual(self.dump(name),data)
    def test_remote_only_record_loads_without_legacy_settings(self):
        self.blob(b'remote_v1',self.record(b'TKR\x01\x00\0\0\0'))
        s=State(beep=True,voice=True,talk=1,sleep=3,remote_dim=True)
        self.assertEqual(self.lib.tk_persist_load(C.byref(s)),0)
        self.assertEqual((s.beep,s.voice,s.talk,s.sleep,s.remote_dim),(True,True,1,3,False))
    def test_bad_remote_records_are_reported_retained_and_do_not_apply_flag(self):
        headers=[b'TKR\x02\x00\0\0\0',b'TKR\x01\x02\0\0\0',b'TKR\x01\x00\x01\0\0']
        records=[b'TKR',b'TKR\x01'+bytes(8)]+[self.record(x) for x in headers]
        for record in records:
            with self.subTest(record=record):
                self.blob(b'remote_v1',record);s=State(remote_dim=True);before=bytes(s)
                self.assertNotEqual(self.lib.tk_persist_load(C.byref(s)),0)
                self.assertEqual(bytes(s),before);self.assertEqual(self.dump(b'remote_v1'),record)
    def test_bad_remote_record_keeps_valid_legacy_settings_available(self):
        old=self.record(b'TKS\x01\x00\x01\x02\x01');self.blob(b'settings_v1',old);self.blob(b'remote_v1',b'broken')
        s=State(remote_dim=True);self.assertNotEqual(self.lib.tk_persist_load(C.byref(s)),0)
        self.assertEqual((s.beep,s.voice,s.talk,s.sleep,s.remote_dim),(False,True,2,1,True))
        self.assertEqual(self.dump(b'settings_v1'),old);self.assertEqual(self.dump(b'remote_v1'),b'broken')
    def test_remote_write_and_commit_failures_do_not_replace_committed_record(self):
        accepted=self.record(b'TKR\x01\x01\0\0\0');self.blob(b'remote_v1',accepted)
        old=self.record(b'TKS\x01\x01\x01\x01\x03');self.blob(b'settings_v1',old)
        for stage in (1,2):
            self.lib.tk_mock_fail(stage);s=State(remote_dim=False)
            self.assertNotEqual(self.lib.tk_persist_save_remote(C.byref(s)),0)
            self.assertEqual(self.dump(b'remote_v1'),accepted);self.assertEqual(self.dump(b'settings_v1'),old)
        self.lib.tk_mock_fail(0)
