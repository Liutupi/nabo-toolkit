"""Host-check the C probe's input and HID contracts; no ESP-IDF or board needed."""
import ctypes as C
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
class Buttons(C.Structure):
    _fields_ = [('held', C.c_int), ('since', C.c_uint32), ('fired', C.c_bool)]
class Probe(C.Structure):
    _fields_ = [('test', C.c_bool), ('mac', C.c_bool), ('ready', C.c_bool), ('pairing', C.c_bool),
                ('passkey_valid', C.c_bool), ('passkey', C.c_uint32), ('reconnect_ms', C.c_uint32)]

class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / 'probe.so'
        subprocess.run(['cc', '-shared', '-fPIC', '-Wall', '-Wextra', '-Werror', '-std=c11',
                        str(ROOT/'firmware/main/tk_probe_model.c'), '-o', str(library)], check=True)
        cls.lib = C.CDLL(str(library))
        cls.lib.tk_button_edge.argtypes = [C.POINTER(Buttons), C.c_int, C.c_bool, C.c_uint32]
        cls.lib.tk_button_tick.argtypes = [C.POINTER(Buttons), C.c_uint32]
        cls.lib.tk_buttons_init.argtypes = [C.POINTER(Buttons)]
        cls.lib.tk_probe_press.argtypes = [C.POINTER(Probe), C.c_int]
        cls.lib.tk_hid_ready.argtypes = [C.c_bool, C.c_bool, C.c_uint, C.c_bool, C.c_bool]
        cls.lib.tk_hid_ready.restype = C.c_bool
        cls.lib.tk_hid_packet.argtypes = [C.c_int, C.c_int, C.c_int, C.POINTER(C.c_uint8), C.POINTER(C.c_uint)]
        cls.lib.tk_hid_packet.restype = C.c_bool
        cls.lib.tk_pairing_choice.argtypes = [C.c_bool, C.c_bool, C.c_int]
        cls.lib.tk_pairing_token_valid.argtypes = [C.c_bool, C.c_uint32, C.c_uint32]
        cls.lib.tk_pairing_token_valid.restype = C.c_bool
        cls.lib.tk_reconnect_phase.argtypes = [C.c_uint32, C.c_uint32]
    @classmethod
    def tearDownClass(cls):
        # Windows locks loaded DLLs, including a PE library named probe.so.
        if sys.platform == 'win32':
            import _ctypes
            _ctypes.FreeLibrary(cls.lib._handle)
            cls.lib = None
        cls.temp.cleanup()
    def test_button_classifier_matches_javascript_for_4000_edges_and_ticks(self):
        rng = random.Random(0x4e41424f)
        events = []; now = 0
        for _ in range(4000):
            now += rng.choice([0, 1, 499, 500, 501, 700])
            events.append([rng.choice(['down', 'up', 'tick']), rng.randrange(3), now])
        script = """const {B}=require('./tests/tk_golden/model.js').load();
let st=B.create(),keys=['up','down','ok'];
let es=JSON.parse(require('fs').readFileSync(0,'utf8'));
console.log(JSON.stringify(es.map(([op,k,t])=>op==='tick'?B.tick(st,t):op==='down'?(B.down(st,keys[k],t),[]):B.up(st,keys[k],t))));"""
        reference = json.loads(subprocess.check_output(['node', '-e', script], input=json.dumps(events).encode(), cwd=ROOT))
        state = Buttons(); self.lib.tk_buttons_init(C.byref(state)); names=['up','down','ok','long_up','long_down','long_ok']
        actual=[]
        for op,k,t in events:
            event = self.lib.tk_button_tick(C.byref(state),t) if op=='tick' else self.lib.tk_button_edge(C.byref(state),k,op=='down',t)
            actual.append([] if event < 0 else [names[event]])
        self.assertEqual(actual, reference)
    def test_long_press_wrap_and_single_emission(self):
        state=Buttons(); self.lib.tk_buttons_init(C.byref(state))
        self.lib.tk_button_edge(C.byref(state), 2, True, 0xffffff00)
        self.assertEqual(self.lib.tk_button_tick(C.byref(state), 243), -1)
        self.assertEqual(self.lib.tk_button_tick(C.byref(state), 244), 5)
        self.assertEqual(self.lib.tk_button_edge(C.byref(state), 2, False, 300), -1)
    def test_secure_and_both_subscriptions_are_required(self):
        for enc,auth,sub,protocol,suspended in itertools.product([False,True],[False,True],range(8),[False,True],[False,True]):
            expected=enc and auth and not suspended and bool(sub & (1 if protocol else 4)) and bool(sub & 2)
            self.assertEqual(self.lib.tk_hid_ready(enc,auth,sub,protocol,suspended), expected)
    def packet(self, report, mod, usage):
        out=(C.c_uint8*8)(); length=C.c_uint()
        ok=self.lib.tk_hid_packet(report,mod,usage,out,C.byref(length))
        return ok, bytes(out[:length.value])
    def test_keyboard_consumer_and_right_modifier_reports(self):
        self.assertEqual(self.packet(1,8,0x19),(True,b'\x08\x00\x19\0\0\0\0\0'))
        self.assertEqual(self.packet(1,1,0x19),(True,b'\x01\x00\x19\0\0\0\0\0'))
        self.assertEqual(self.packet(1,0x60,0),(True,b'\x60\0\0\0\0\0\0\0'))
        self.assertEqual(self.packet(2,0,0xe9),(True,b'\xe9\0'))
        for args in [(0,0,1),(1,256,1),(1,0,0x74),(2,1,0xe9),(2,0,1024),(1,0,-1)]:
            self.assertFalse(self.packet(*args)[0])
    def test_navigation_never_sends_hid_and_disconnected_actions_drop(self):
        p=Probe(mac=True)
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),2),0); self.assertTrue(p.test)
        for key in [0,2]: self.assertEqual(self.lib.tk_probe_press(C.byref(p),key),0)
        p.ready=True
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),2),1)
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),0),2)
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),3),0); self.assertFalse(p.test)
    def test_leading_zero_passkey_blocks_reports_and_cancel_reconnects(self):
        p=Probe(test=True,mac=True,ready=True,pairing=True,passkey_valid=True,passkey=123)
        self.assertEqual(f'{p.passkey:06d}','000123')
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),2),0)
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),3),4)
        self.assertFalse(p.passkey_valid)
    def test_mode_toggle_and_pair_reconnect_effects(self):
        p=Probe(test=True,mac=True)
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),1),5); self.assertFalse(p.mac)
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),4),3)
        self.assertEqual(self.lib.tk_probe_press(C.byref(p),5),4)

    def test_numeric_comparison_requires_physical_short_ok_or_long_up(self):
        for pending, physical, key in itertools.product([False, True], [False, True], range(-1, 7)):
            expected = (1 if key == 2 else 2 if key == 3 else 0) if pending and physical else 0
            self.assertEqual(self.lib.tk_pairing_choice(pending, physical, key), expected)

    def test_numeric_comparison_rejects_stale_cancelled_and_zero_tokens(self):
        for pending, current, requested in [(False, 7, 7), (True, 7, 6), (True, 8, 7),
                                            (True, 0, 0), (True, 1, 0xffffffff)]:
            self.assertFalse(self.lib.tk_pairing_token_valid(pending, current, requested))
        self.assertTrue(self.lib.tk_pairing_token_valid(True, 7, 7))
        self.assertTrue(self.lib.tk_pairing_token_valid(True, 0xffffffff, 0xffffffff))

    def test_reconnect_falls_back_before_three_second_budget_and_preserves_ten_second_window(self):
        # Same policy must work across the uint32 uptime wrap, including delayed ticks.
        for started in [0, 12345, 0xffffff00]:
            for elapsed, expected in [(0, 0), (499, 0), (500, 1), (501, 1),
                                      (2999, 1), (9999, 1), (10000, 2), (11000, 2)]:
                self.assertEqual(self.lib.tk_reconnect_phase((started + elapsed) & 0xffffffff, started), expected)
