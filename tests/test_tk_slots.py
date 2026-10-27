import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import unittest
import zlib
from tk_native import ROOT,unload
class Peer(C.Structure):
    _fields_=[('used',C.c_ubyte),('type',C.c_ubyte),('os',C.c_ubyte),('address',C.c_ubyte*6),('name',C.c_char*96)]
class Slots(C.Structure):
    _fields_=[('peers',Peer*3),('order',C.c_ubyte*3),('count',C.c_ubyte),('active',C.c_ubyte)]
def peer(i):return Peer(1,0,1,(C.c_ubyte*6)(1,2,3,4,5,i),('Synthetic '+str(i)).encode())
class SlotStorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();p=Path(cls.temp.name)/'slots.so'
        subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror','-std=c11',str(ROOT/'firmware/main/tk_slots.c'),'-o',str(p)],check=True)
        cls.lib=C.CDLL(str(p));lib=cls.lib
        lib.tk_slots_add.argtypes=[C.POINTER(Slots),C.POINTER(Peer),C.POINTER(Peer)]
        lib.tk_slots_remove.argtypes=[C.POINTER(Slots),C.c_uint];lib.tk_slots_remove.restype=C.c_bool
        lib.tk_slots_encode.argtypes=[C.POINTER(Slots),C.POINTER(C.c_ubyte)];lib.tk_slots_encode.restype=C.c_bool
        lib.tk_slots_decode.argtypes=[C.POINTER(Slots),C.POINTER(C.c_ubyte),C.c_size_t];lib.tk_slots_decode.restype=C.c_bool
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def test_fifo_replacement_and_selection_do_not_become_lru(self):
        s=Slots();old=Peer()
        for i in (1,2,3):self.assertGreaterEqual(self.lib.tk_slots_add(C.byref(s),C.byref(peer(i)),C.byref(old)),0)
        s.active=0
        self.assertEqual(self.lib.tk_slots_add(C.byref(s),C.byref(peer(4)),C.byref(old)),0)
        self.assertEqual(list(old.address),[1,2,3,4,5,1]);self.assertEqual(list(s.order),[1,2,0])
        self.assertEqual(self.lib.tk_slots_add(C.byref(s),C.byref(peer(5)),C.byref(old)),1)
        self.assertEqual(list(s.order),[2,0,1])
    def test_crc_roundtrip_bad_data_rejection_is_atomic(self):
        s=Slots();self.lib.tk_slots_add(C.byref(s),C.byref(peer(1)),None);out=(C.c_ubyte*329)()
        self.assertTrue(self.lib.tk_slots_encode(C.byref(s),out));restored=Slots()
        self.assertTrue(self.lib.tk_slots_decode(C.byref(restored),out,329));self.assertEqual(bytes(s),bytes(restored))
        before=bytes(restored);out[25]^=1
        self.assertFalse(self.lib.tk_slots_decode(C.byref(restored),out,329));self.assertEqual(bytes(restored),before)
        raw=bytearray(out);raw[5]=255;raw[325:]=zlib.crc32(raw[:325]).to_bytes(4,'little');out=(C.c_ubyte*329).from_buffer_copy(raw)
        self.assertFalse(self.lib.tk_slots_decode(C.byref(restored),out,329));self.assertEqual(bytes(restored),before)
    def test_duplicate_repair_and_invalid_new_record_preserve_other_slots(self):
        s=Slots();self.lib.tk_slots_add(C.byref(s),C.byref(peer(1)),None);self.lib.tk_slots_add(C.byref(s),C.byref(peer(2)),None)
        self.assertEqual(self.lib.tk_slots_add(C.byref(s),C.byref(peer(1)),None),0);self.assertEqual(s.count,2);self.assertEqual(list(s.order[:2]),[1,0])
        before=bytes(s);bad=peer(3);bad.os=9
        self.assertEqual(self.lib.tk_slots_add(C.byref(s),C.byref(bad),None),-1);self.assertEqual(bytes(s),before)
        self.assertTrue(self.lib.tk_slots_remove(C.byref(s),0));self.assertEqual(list(s.order[:s.count]),[1]);self.assertEqual(s.peers[1].name,b'Synthetic 2')
