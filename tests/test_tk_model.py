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
        self.assertGreaterEqual(len(ROWS),2666)
        self.assertEqual({r['state']['display']['off'] for r in ROWS},{False,True})
        self.assertEqual({r['state']['media']['mode'] for r in ROWS if r['state']['page']=='media'},{0,1})
        self.assertEqual({r['state']['voice']['status'] for r in ROWS},set(range(12)))
        self.assertIsNone(replay(self.lib,ROWS))
    def test_production_init_has_no_demonstration_bonds_or_fake_connection(self):
        s=State();self.lib.tk_model_init(C.byref(s),12345)
        self.assertFalse(s.connected);self.assertFalse(any(x.used for x in s.slots));self.assertEqual(s.bind_count,0)
        self.assertEqual(s.last_input,12345);self.assertEqual(s.boot_start,12345)
        self.assertTrue(s.remote_dim);self.assertFalse(s.screen_off);self.assertEqual(s.screen_since,-1)
        self.assertEqual(s.media_mode,0);self.assertTrue(s.media_select)
        self.assertEqual(list(s.voice_counts),[0]*7);self.assertFalse(s.voice_busy)
        self.assertEqual((s.voice_selected,s.voice_operation,s.voice_status,s.voice_token),(0,0,0,0))
        self.assertLess(C.sizeof(State),8192);self.assertLess(C.sizeof(Effects),32768)
    def test_voice_guards_counter_wrap_and_invalid_count_snapshot_are_atomic(self):
        for field,value in [('pairing',True),('os_pick',True),('confirm_del',0)]:
            s=State();self.lib.tk_model_init(C.byref(s),0);s.page=1;setattr(s,field,value);before=bytes(s)
            self.assertFalse(self.lib.tk_model_voice_open(C.byref(s),10));self.assertEqual(bytes(s),before)
        s=State();out=Effects();self.lib.tk_model_init(C.byref(s),0);s.page=1;s.voice_token=0xffffffff
        self.assertTrue(self.lib.tk_model_voice_open(C.byref(s),10));self.assertEqual(s.voice_token,1)
        before=bytes(s);self.assertFalse(self.lib.tk_model_voice_templates(C.byref(s),(C.c_uint8*7)(0,0,4,0,0,0,0)))
        self.assertEqual(bytes(s),before);self.lib.tk_model_press(C.byref(s),5,20,C.byref(out));token=s.voice_token
        self.assertTrue(s.voice_busy);self.assertFalse(any(x.type==1 for x in out.items[:out.count]))
        self.lib.tk_model_press(C.byref(s),3,30,C.byref(out));before=bytes(s)
        self.assertFalse(self.lib.tk_model_voice_result(C.byref(s),token,1,0,0,40));self.assertEqual(bytes(s),before)
    def test_voice_count_snapshot_reads_unaligned_sources_as_bytes_without_partial_updates(self):
        s=State();self.lib.tk_model_init(C.byref(s),0)
        for offset in range(4):
            with self.subTest(offset=offset):
                data=C.create_string_buffer(bytes([0xA5])*16,16)
                values=[(i+offset)%4 for i in range(7)]
                for i,value in enumerate(values):data[offset+i]=bytes([value])
                pointer=C.cast(C.byref(data,offset),C.POINTER(C.c_uint8));before=bytes(data)
                self.assertTrue(self.lib.tk_model_voice_templates(C.byref(s),pointer))
                self.assertEqual(list(s.voice_counts),values);self.assertEqual(bytes(data),before)
                state_before=bytes(s);data[offset+6]=bytes([4]);before=bytes(data)
                self.assertFalse(self.lib.tk_model_voice_templates(C.byref(s),pointer))
                self.assertEqual(bytes(s),state_before);self.assertEqual(bytes(data),before)
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
