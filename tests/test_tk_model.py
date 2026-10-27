import ctypes as C
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from tk_native import ROOT, State, Effects, build, replay, unload

ROWS=[json.loads(line) for line in (ROOT/'tests/tk_golden/traces.jsonl').read_text(encoding='utf-8').splitlines()]
class ModelReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.lib=build(cls.temp.name)
    @classmethod
    def tearDownClass(cls):
        unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def test_every_reference_step_matches_complete_c_state_and_outputs(self):
        self.assertGreaterEqual(len(ROWS),1582)
        self.assertIsNone(replay(self.lib,ROWS))
    def test_production_init_has_no_demonstration_bonds_or_fake_connection(self):
        s=State();self.lib.tk_model_init(C.byref(s),12345)
        self.assertFalse(s.connected);self.assertFalse(any(x.used for x in s.slots));self.assertEqual(s.bind_count,0)
        self.assertEqual(s.last_input,12345);self.assertEqual(s.boot_start,12345)
        self.assertLess(C.sizeof(State),8192);self.assertLess(C.sizeof(Effects),32768)
    def test_replay_rejects_time_cadence_and_right_modifier_mutations(self):
        self.assertIsNone(replay(self.lib,ROWS), 'Mutation probes require a passing unmodified model first')
        mutations=[('tk_model.c','elapsed>=5500','elapsed>=5499'),
                   ('tk_model.c','s->next_shot+=600','s->next_shot+=601'),
                   ('tk_hid_data.inc','{1,96,0,NULL}','{1,32,0,NULL}')]
        for filename,old,new in mutations:
            with self.subTest(mutation=filename+old),tempfile.TemporaryDirectory() as directory:
                for p in (ROOT/'firmware/main').iterdir():
                    if p.suffix in ('.c','.h','.inc'):shutil.copyfile(p,Path(directory)/p.name)
                p=Path(directory)/filename;s=p.read_text(encoding='utf-8');self.assertIn(old,s)
                p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
                lib=build(directory,Path(directory))
                try:self.assertIsNotNone(replay(lib,ROWS))
                finally:unload(lib);lib=None
