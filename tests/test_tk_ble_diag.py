"""Telemetry contracts: no hardware access or radio/send policy in this module."""
import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from tk_native import ROOT,unload

class Diagnostics(C.Structure):
    _fields_=[('params_valid',C.c_bool)]+[(x,C.c_uint32) for x in
        ['interval_us','latency','supervision_ms','tx_completed','tx_errors','press_errors','release_errors']]+[
        ('enqueue_error',C.c_int),('tx_error',C.c_int)]

class BleDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();dest=Path(cls.temp.name)/'diag.so'
        subprocess.run(['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-std=c11',
            str(ROOT/'firmware/main/tk_ble_diag.c'),'-o',str(dest)],check=True)
        cls.lib=C.CDLL(str(dest));cls.lib.tk_ble_diag_link.argtypes=[C.c_bool,C.c_uint16,C.c_uint16,C.c_uint16]
        cls.lib.tk_ble_diag_enqueue.argtypes=[C.c_bool,C.c_int];cls.lib.tk_ble_diag_tx.argtypes=[C.c_int]
        cls.lib.tk_ble_diag_snapshot.restype=Diagnostics
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def setUp(self):self.lib.tk_ble_diag_reset()
    @staticmethod
    def params(d):return d.params_valid,d.interval_us,d.latency,d.supervision_ms
    def test_disconnect_invalidates_parameters_but_preserves_fault_history_and_new_link_units(self):
        self.assertEqual(self.params(self.lib.tk_ble_diag_snapshot()),(False,0,0,0))
        self.lib.tk_ble_diag_link(True,6,0,400)
        self.assertEqual(self.params(self.lib.tk_ble_diag_snapshot()),(True,7500,0,4000))
        self.lib.tk_ble_diag_enqueue(False,0);self.lib.tk_ble_diag_enqueue(True,0)
        self.lib.tk_ble_diag_enqueue(False,12);self.lib.tk_ble_diag_enqueue(True,7)
        self.lib.tk_ble_diag_tx(0);self.lib.tk_ble_diag_tx(23)
        self.lib.tk_ble_diag_link(False,0,0,0);d=self.lib.tk_ble_diag_snapshot()
        self.assertEqual(self.params(d),(False,0,0,0))
        self.assertEqual((d.press_errors,d.release_errors,d.tx_completed,d.tx_errors),(1,1,1,1))
        self.assertEqual((d.enqueue_error,d.tx_error),(7,23))
        self.lib.tk_ble_diag_link(True,65535,65535,65535);d=self.lib.tk_ble_diag_snapshot()
        self.assertEqual(self.params(d),(True,81918750,65535,655350))
        self.assertEqual((d.press_errors,d.release_errors,d.tx_errors),(1,1,1))
        # Boot reset is quiescent and clears history; ordinary reconnect did not.
        self.lib.tk_ble_diag_reset();d=self.lib.tk_ble_diag_snapshot()
        self.assertEqual(self.params(d),(False,0,0,0));self.assertEqual((d.press_errors,d.release_errors,d.tx_errors),(0,0,0))
    def test_parameter_sampling_is_bounded_and_never_mixes_concurrent_link_updates(self):
        allowed={(False,0,0,0),(True,7500,3,4000),(True,50000,12,6000)}
        start=threading.Event();done=threading.Event();failures=[]
        def writer():
            start.wait()
            for _ in range(3000):
                self.lib.tk_ble_diag_link(True,6,3,400)
                self.lib.tk_ble_diag_link(False,0,0,0)
                self.lib.tk_ble_diag_link(True,40,12,600)
            done.set()
        thread=threading.Thread(target=writer,daemon=True);thread.start();started=time.monotonic();start.set()
        for _ in range(10000):
            params=self.params(self.lib.tk_ble_diag_snapshot())
            if params not in allowed:failures.append(params);break
        thread.join(timeout=10)
        self.assertTrue(done.is_set(),'Snapshot blocked the independently progressing parameter writer')
        self.assertFalse(failures,failures);self.assertLess(time.monotonic()-started,10)
