import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import unittest
from tk_native import ROOT,unload
from test_tk_slots import Slots
class Address(C.Structure):_fields_=[('type',C.c_ubyte),('val',C.c_ubyte*6)]
class BondTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();p=Path(self.temp.name)/'backend.so'
        subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror','-std=c11','-I',str(ROOT/'tests/support'),'-I',str(ROOT/'firmware/main'),
                        str(ROOT/'firmware/main/tk_ble_slots.c'),str(ROOT/'firmware/main/tk_slots.c'),str(ROOT/'tests/tk_store_mock.c'),'-o',str(p)],check=True)
        self.lib=C.CDLL(str(p));self.lib.tk_mock_reset()
        self.lib.tk_ble_slots_bound.argtypes=[C.POINTER(Address)];self.lib.tk_ble_slots_snapshot.argtypes=[C.POINTER(Slots)]
        self.lib.tk_ble_slots_snapshot.restype=C.c_bool
        self.lib.tk_mock_blob.argtypes=[C.c_char_p,C.POINTER(C.c_ubyte),C.c_uint]
        for i in (1,2,3):self.lib.tk_mock_add_peer(i)
    def tearDown(self):unload(self.lib);self.lib=None;self.temp.cleanup()
    def init(self):self.lib.tk_ble_slots_init();return self.lib.tk_ble_slots_sync()
    def ids(self):return {self.lib.tk_mock_peer_id(i) for i in range(self.lib.tk_mock_peer_count())}
    def test_new_pair_commit_precedes_fifo_unpair(self):
        self.assertEqual(self.init(),0);self.lib.tk_mock_add_peer(4)
        a=Address(0,(C.c_ubyte*6)(1,2,3,4,5,4));self.assertGreaterEqual(self.lib.tk_ble_slots_bound(C.byref(a)),0)
        self.assertEqual(self.ids(),{2,3,4});self.assertGreater(self.lib.tk_mock_unpair_step(),self.lib.tk_mock_commit_step())
    def test_failed_profile_commit_removes_only_staging_peer(self):
        self.assertEqual(self.init(),0);self.lib.tk_mock_add_peer(4);self.lib.tk_mock_fail(2)
        a=Address(0,(C.c_ubyte*6)(1,2,3,4,5,4));self.assertEqual(self.lib.tk_ble_slots_bound(C.byref(a)),-1)
        self.assertEqual(self.ids(),{1,2,3});self.assertEqual(self.lib.tk_mock_drop_id(0),4)
        s=Slots();self.lib.tk_ble_slots_snapshot(C.byref(s));self.assertEqual(s.count,3)
    def test_startup_cleanup_discards_uncommitted_staging_record(self):
        self.assertEqual(self.init(),0);self.lib.tk_mock_add_peer(4)
        self.assertEqual(self.lib.tk_ble_slots_sync(),0);self.assertEqual(self.ids(),{1,2,3})
    def test_bad_profile_blob_does_not_unpair_or_overwrite_old_records(self):
        data=(C.c_ubyte*329)();self.lib.tk_mock_blob(b'slots_v1',data,329)
        self.assertNotEqual(self.init(),0);self.assertEqual(self.ids(),{1,2,3});self.assertEqual(self.lib.tk_mock_drop_count(),0)
    def test_f0_migration_preserves_selected_identity_and_mac_preference(self):
        peer=(C.c_ubyte*7)(0,1,2,3,4,5,2);mac=(C.c_ubyte*1)(1)
        self.lib.tk_mock_blob(b'f0_peer',peer,7);self.lib.tk_mock_blob(b'f0_mac',mac,1)
        self.assertEqual(self.init(),0);s=Slots();self.lib.tk_ble_slots_snapshot(C.byref(s))
        self.assertEqual(s.peers[s.active].address[5],2);self.assertEqual(s.peers[s.active].os,0)
        self.assertEqual(self.ids(),{1,2,3});self.assertEqual(self.lib.tk_mock_drop_count(),0)
    def test_failed_select_type_and_delete_preserve_committed_slots_and_keys(self):
        self.assertEqual(self.init(),0);before=Slots();self.lib.tk_ble_slots_snapshot(C.byref(before))
        self.lib.tk_mock_fail(2)
        for operation,args in [('select',(0,)),('type',(1,0)),('delete',(1,))]:
            self.assertNotEqual(getattr(self.lib,'tk_ble_slots_'+operation)(*args),0)
            after=Slots();self.lib.tk_ble_slots_snapshot(C.byref(after));self.assertEqual(bytes(after),bytes(before))
            self.assertEqual(self.ids(),{1,2,3});self.assertEqual(self.lib.tk_mock_drop_count(),0)
