"""Production template persistence and calibrated capture bounds; no microphone."""
import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import unittest
import zlib
from tk_native import ROOT,unload

class Frame(C.Structure):_fields_=[('value',C.c_int8*12)]
class Template(C.Structure):_fields_=[('frame',Frame*48),('count',C.c_uint8)]
class StoreResult(C.Structure):
    _fields_=[('write_error',C.c_int),('read_error',C.c_int),('confirmed',C.c_bool),('unknown',C.c_bool)]
class Capture(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('start_ms','noise_sum','cal_frames','threshold','frames','silent','max_frames','min_frames')]+[
        ('calibrated',C.c_bool),('started',C.c_bool),('done',C.c_bool),('decision',C.c_int)]

class VoiceStoreCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();dest=Path(cls.temp.name)/'voice.so';main=ROOT/'firmware/main'
        result=subprocess.run(['cc','-shared','-fPIC','-std=c11','-O2','-Wall','-Wextra','-Werror',
            '-I',str(ROOT/'tests/support'),'-I',str(main),'-I',str(ROOT/'tools/voice_probe'),
            str(main/'tk_voice_store.c'),str(main/'tk_voice_capture.c'),str(ROOT/'tests/tk_store_mock.c'),'-o',str(dest)],
            capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stderr)
        cls.lib=C.CDLL(str(dest));p=C.POINTER(C.c_uint8)
        cls.lib.tk_voice_store_load.argtypes=[C.c_uint,C.POINTER(Template),p,p]
        cls.lib.tk_voice_store_save.argtypes=[C.c_uint,C.POINTER(Template),C.c_uint,C.POINTER(Frame),C.c_uint,p,C.POINTER(StoreResult)]
        cls.lib.tk_voice_store_compact_legacy.argtypes=[C.c_uint,p]
        cls.lib.tk_voice_store_scan.argtypes=[p,p,C.POINTER(Template),p]
        cls.lib.tk_mock_blob.argtypes=[C.c_char_p,p,C.c_uint];cls.lib.tk_mock_dump.argtypes=[C.c_char_p,p]
        cls.lib.tk_voice_capture_init.argtypes=[C.POINTER(Capture),C.c_uint32,C.c_bool]
        cls.lib.tk_voice_capture_feed.argtypes=[C.POINTER(Capture),C.c_uint32,C.c_uint32];cls.lib.tk_voice_capture_feed.restype=C.c_bool
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def setUp(self):self.lib.tk_mock_reset();self.scratch=(C.c_uint8*3548)()
    def blob(self,key,data):
        if key.startswith(b'voice'):
            for suffix in (b'a',b'b'):self.lib.tk_mock_blob(b'vc'+key[-1:]+suffix,(C.c_uint8*1)(),0)
        self.lib.tk_mock_blob(key,(C.c_uint8*len(data)).from_buffer_copy(data),len(data))
    def dump(self,key):
        if key.startswith(b'voice'):
            candidates=[self.dump(b'vc'+key[-1:]+suffix) for suffix in (b'a',b'b')]
            candidates=[x for x in candidates if x]
            if candidates:return max(candidates,key=lambda x:int.from_bytes(x[20:24],'little'))
        return self.raw(key)
    def raw(self,key):
        b=(C.c_uint8*4016)();n=self.lib.tk_mock_dump(key,b);return bytes(b[:n])
    def legacy(self,word,bank,next_slot=1,words=6):
        p=bytearray(1752);p[:16]=bytes([84,75,86,49,1,1,word,words,3,12,48,16,128,62,64,1]);p[16]=next_slot
        for e in range(3):p[17+e]=bank[e].count;p[20+e*576:20+e*576+bank[e].count*12]=bytes(bank[e].frame)[:bank[e].count*12]
        p[-4:]=zlib.crc32(p[:-4]).to_bytes(4,'little');return bytes(p)
    @staticmethod
    def sample(n=20,offset=0):
        a=(Frame*n)()
        for f in range(n):
            for k in range(12):a[f].value[k]=((f+k+offset)%31)-15
        return a
    def save(self,word,bank,example,n=20,offset=0,result=None):
        return self.lib.tk_voice_store_save(word,bank,example,self.sample(n,offset),n,self.scratch,C.byref(result) if result is not None else None)
    def load(self,word):
        bank=(Template*3)();next_slot=C.c_uint8(99)
        error=self.lib.tk_voice_store_load(word,bank,C.byref(next_slot),self.scratch)
        return error,bank,next_slot.value
    def test_missing_record_does_not_initialize_or_rewrite_caller_storage(self):
        bank=(Template*3)();bank[0].count=23;before=bytes(bank);slot=C.c_uint8(2)
        self.assertNotEqual(self.lib.tk_voice_store_load(0,bank,C.byref(slot),self.scratch),0)
        self.assertEqual(bytes(bank),before);self.assertEqual(slot.value,2);self.assertEqual(self.dump(b'voice0'),b'')
    def test_each_word_roundtrips_three_samples_and_preserves_all_nonvoice_keys(self):
        sentinels={k:('private-test-'+k.decode()).encode() for k in (b'cfg_v1',b'slots_v1',b'settings_v1',b'remote_v1')}
        for key,data in sentinels.items():self.blob(key,data)
        for word in range(7):
            bank=(Template*3)()
            for example in range(3):
                before=bytes(bank);self.assertEqual(self.save(word,bank,example,20+example,word),0)
                self.assertEqual(bytes(bank),before,'Save must not mutate caller RAM before runtime installs the confirmed record')
                error,bank,next_slot=self.load(word);self.assertEqual(error,0)
                self.assertEqual(next_slot,(example+1)%3)
                self.assertEqual([x.count for x in bank],[20+i if i<=example else 0 for i in range(3)])
            self.assertLess(len(self.dump(f'voice{word}'.encode())),1752)
        for key,data in sentinels.items():self.assertEqual(self.dump(key),data)
    def test_wrong_format_word_counts_crc_and_padding_never_partially_apply(self):
        bank=(Template*3)();self.assertEqual(self.save(0,bank,0),0);_,bank,_=self.load(0);accepted=self.legacy(0,bank)
        variants=[]
        for offset,value in [(4,2),(5,2),(6,1),(7,5),(8,2),(9,13),(10,49),(11,8),(12,0),(14,0),(16,3),(17,7),(17,49),(20,128),(20+20*12,1)]:
            d=bytearray(accepted);d[offset]=value;d[-4:]=zlib.crc32(d[:-4]).to_bytes(4,'little');variants.append(bytes(d))
        d=bytearray(accepted);d[24]^=1;variants.extend([bytes(d),accepted[:32]])
        for data in variants:
            with self.subTest(prefix=data[:20]):
                self.blob(b'voice0',data);out=(Template*3)();out[2].count=30;before=bytes(out);slot=C.c_uint8(1)
                self.assertNotEqual(self.lib.tk_voice_store_load(0,out,C.byref(slot),self.scratch),0)
                self.assertEqual(bytes(out),before);self.assertEqual(slot.value,1);self.assertEqual(self.dump(b'voice0'),data)
    def test_failed_or_ignored_write_reads_old_record_without_inventing_a_rollback(self):
        bank=(Template*3)();self.assertEqual(self.save(0,bank,0),0);_,bank,_=self.load(0)
        accepted=self.dump(b'voice0');before=bytes(bank)
        for stage in (1,5):
            result=StoreResult();self.lib.tk_mock_fail(stage)
            self.assertNotEqual(self.save(0,bank,1,30,9,result),0)
            self.assertFalse(result.confirmed);self.assertFalse(result.unknown);self.assertIn(result.read_error,(0,0x1102))
            self.assertEqual(bytes(bank),before);self.assertEqual(self.dump(b'voice0'),accepted)
    def test_written_record_is_confirmed_even_when_set_or_commit_returns_error(self):
        for stage,write_error in ((4,0x1108),(2,-1)):
            with self.subTest(stage=stage):
                self.lib.tk_mock_reset();empty=(Template*3)();self.assertEqual(self.save(0,empty,0),0)
                _,bank,_=self.load(0);before=bytes(bank);old=self.dump(b'voice0');result=StoreResult()
                self.lib.tk_mock_fail(stage);self.assertEqual(self.save(0,bank,1,30,9,result),0)
                self.assertTrue(result.confirmed);self.assertFalse(result.unknown)
                self.assertEqual((result.write_error,result.read_error),(write_error,0))
                self.assertEqual(bytes(bank),before);self.assertNotEqual(self.dump(b'voice0'),old)
                error,loaded,next_slot=self.load(0);self.assertEqual((error,next_slot),(0,2))
                self.assertEqual([x.count for x in loaded],[20,30,0])
    def test_unreadable_postwrite_is_unknown_and_never_blindly_restores_old_blob(self):
        empty=(Template*3)();self.assertEqual(self.save(0,empty,0),0);_,bank,_=self.load(0)
        old=self.dump(b'voice0');before=bytes(bank);result=StoreResult();self.lib.tk_mock_fail(6)
        self.assertNotEqual(self.save(0,bank,1,30,9,result),0)
        self.assertFalse(result.confirmed);self.assertTrue(result.unknown)
        self.assertEqual((result.write_error,result.read_error),(0,-1))
        self.assertEqual(bytes(bank),before);written=self.dump(b'voice0');self.assertNotEqual(written,old)
        self.lib.tk_mock_fail(0);error,loaded,next_slot=self.load(0)
        self.assertEqual((error,next_slot),(0,2));self.assertEqual([x.count for x in loaded],[20,30,0])
        self.assertEqual(self.dump(b'voice0'),written)
    def test_replacing_rotated_sample_retains_other_examples_and_zeroes_unused_tail(self):
        bank=(Template*3)()
        for example in range(3):self.assertEqual(self.save(2,bank,example,40,example),0);_,bank,_=self.load(2)
        others=bytes(bank[1])+bytes(bank[2]);self.assertEqual(self.save(2,bank,0,15,9),0)
        _,bank,next_slot=self.load(2);self.assertEqual(next_slot,1);self.assertEqual(bank[0].count,15)
        self.assertEqual(bytes(bank[1])+bytes(bank[2]),others)
        self.assertEqual(bytes(bank[0].frame)[15*12:],bytes((48-15)*12))
    def test_invalid_enrollment_never_writes_a_record(self):
        bank=(Template*3)()
        for word,example,n in [(7,0,20),(0,3,20),(0,0,7),(0,0,49)]:self.assertNotEqual(self.save(word,bank,example,n),0)
        bad=self.sample();bad[0].value[0]=-128
        self.assertNotEqual(self.lib.tk_voice_store_save(0,bank,0,bad,20,self.scratch,None),0)
        self.assertEqual(self.dump(b'voice0'),b'')
    def test_invalid_one_word_keeps_others_usable_and_explicit_reenrollment_repairs_only_that_word(self):
        empty=(Template*3)()
        for word in range(7):self.assertEqual(self.save(word,empty,0,20,word),0)
        originals={f'voice{w}'.encode():self.dump(f'voice{w}'.encode()) for w in range(7)}
        broken=bytearray(originals[b'voice2']);broken[25]^=1;self.blob(b'voice2',bytes(broken))
        counts=(C.c_uint8*7)();mask=C.c_uint8();wordbuf=(Template*3)()
        self.assertEqual(self.lib.tk_voice_store_scan(counts,C.byref(mask),wordbuf,self.scratch),0)
        self.assertEqual(list(counts),[1,1,0,1,1,1,1]);self.assertEqual(mask.value,4)
        self.assertEqual(self.dump(b'voice2'),bytes(broken),'Scan preserves corrupt record')
        self.assertEqual(self.save(2,empty,0,22,9),0)
        self.assertEqual(self.lib.tk_voice_store_scan(counts,C.byref(mask),wordbuf,self.scratch),0)
        self.assertEqual(list(counts),[1]*7);self.assertEqual(mask.value,0)
        for key,data in originals.items():
            if key!=b'voice2':self.assertEqual(self.dump(key),data)
    def test_real_store_read_error_is_not_silently_treated_as_a_bad_optional_record(self):
        self.lib.tk_mock_fail(3);counts=(C.c_uint8*7)();mask=C.c_uint8();wordbuf=(Template*3)()
        self.assertNotEqual(self.lib.tk_voice_store_scan(counts,C.byref(mask),wordbuf,self.scratch),0)
        self.assertEqual(mask.value,0)
    def test_six_word_records_load_unchanged_but_seventh_requires_new_header(self):
        original={}
        for word in range(7):
            empty=(Template*3)();self.assertEqual(self.save(word,empty,0,21,word),0);_,bank,_=self.load(word)
            data=self.legacy(word,bank,words=6)
            self.blob(f'voice{word}'.encode(),data);original[word]=bytes(data)
        counts=(C.c_uint8*7)();mask=C.c_uint8();wordbuf=(Template*3)()
        self.assertEqual(self.lib.tk_voice_store_scan(counts,C.byref(mask),wordbuf,self.scratch),0)
        self.assertEqual(list(counts),[1,1,1,1,1,1,0]);self.assertEqual(mask.value,64)
        for word in range(6):
            error,bank,slot=self.load(word);self.assertEqual((error,slot,bank[0].count),(0,1,21))
            self.assertEqual(self.dump(f'voice{word}'.encode()),original[word])
        _,bank,slot=self.load(2);self.assertEqual(self.save(2,bank,slot,24,9),0)
        error,loaded,slot=self.load(2);self.assertEqual((error,slot),(0,2))
        self.assertEqual([x.count for x in loaded],[21,24,0]);self.assertEqual(self.dump(b'voice2')[7],7)
        self.assertEqual(self.save(6,(Template*3)(),0,23,6),0)
        self.assertEqual(self.load(6)[0],0);self.assertEqual(self.dump(b'voice6')[7],7)
        for word in (0,1,3,4,5):self.assertEqual(self.dump(f'voice{word}'.encode()),original[word])
    def test_compact_bitpacking_is_lossless_for_constant_and_full_range_coefficients(self):
        for mode in ('constant','range'):
            self.lib.tk_mock_reset();bank=(Template*3)()
            for e in range(3):
                frames=(Frame*48)()
                for f in range(48):
                    for d in range(12):frames[f].value[d]=(-127 if mode=='constant' or (f+d)%2 else 127)
                self.assertEqual(self.lib.tk_voice_store_save(0,bank,e,frames,48,self.scratch,None),0)
                error,bank,slot=self.load(0);self.assertEqual((error,slot),(0,(e+1)%3))
                self.assertEqual(bytes(bank[e].frame),bytes(frames))
            self.assertEqual(len(self.dump(b'voice0')),46 if mode=='constant' else 1774)
    def test_capacity_pressure_keeps_legacy_words_and_active_journal_on_space_failure(self):
        # Match the actual six-page partition's 546 live entries: six legacy
        # blobs (342 entries) plus 204 other entries/chunk-fragment overhead.
        old={};seed=(Template*3)()
        for e in range(3):seed[e].count=47;C.memmove(seed[e].frame,self.sample(47,e),47*12)
        for word in range(6):
            old[word]=self.legacy(word,seed,next_slot=0);self.blob(f'voice{word}'.encode(),old[word])
        self.lib.tk_mock_capacity(630,204);bank=(Template*3)()
        for turn in range(30):
            slot=turn%3;self.assertEqual(self.save(6,bank,slot,47,turn%10),0)
            error,bank,next_slot=self.load(6);self.assertEqual((error,next_slot),(0,(slot+1)%3))
        accepted={s:self.dump(b'vc6'+s) for s in (b'a',b'b')};before=bytes(bank)
        maximum=(Frame*48)()
        for f in range(48):
            for d in range(12):maximum[f].value[d]=127 if (f+d)%2 else -127
        result=StoreResult()
        self.assertEqual(self.lib.tk_voice_store_save(6,bank,next_slot,maximum,48,self.scratch,C.byref(result)),0x1105)
        self.assertFalse(result.confirmed);self.assertFalse(result.unknown);self.assertEqual(bytes(bank),before)
        self.assertEqual(self.load(6)[1][:][0].count,47)
        for suffix,data in accepted.items():self.assertEqual(self.dump(b'vc6'+suffix),data)
        for word,data in old.items():self.assertEqual(self.dump(f'voice{word}'.encode()),data)
    def test_sdk_partial_write_cleanup_cannot_target_the_previous_confirmed_key(self):
        bank=(Template*3)();self.assertEqual(self.save(6,bank,0,30),0);_,bank,slot=self.load(6)
        accepted=self.dump(b'vc6a');self.lib.tk_mock_fail(7);result=StoreResult()
        self.assertEqual(self.save(6,bank,slot,31,9,result),0x1105)
        self.assertFalse(result.unknown);self.assertEqual(self.dump(b'vc6a'),accepted);self.assertEqual(self.dump(b'vc6b'),b'')
        self.lib.tk_mock_fail(0);error,loaded,next_slot=self.load(6)
        self.assertEqual((error,next_slot),(0,1));self.assertEqual([x.count for x in loaded],[30,0,0])
    def test_malformed_compact_width_size_crc_or_generation_never_applies(self):
        bank=(Template*3)();self.assertEqual(self.save(0,bank,0),0);record=self.dump(b'vc0a')
        for offset,value in ((4,3),(20,0),(24,128),(36,15)):
            data=bytearray(record);data[offset]=value;data[-4:]=zlib.crc32(data[:-4]).to_bytes(4,'little')
            self.blob(b'vc0a',data);out=(Template*3)();out[1].count=20;before=bytes(out);slot=C.c_uint8(2)
            self.assertNotEqual(self.lib.tk_voice_store_load(0,out,C.byref(slot),self.scratch),0)
            self.assertEqual(bytes(out),before);self.assertEqual(slot.value,2)
    def test_incomplete_inactive_slot_does_not_block_the_fresh_valid_confirmed_slot(self):
        self.lib.tk_mock_read_fail_key.argtypes=[C.c_char_p]
        bank=(Template*3)();self.assertEqual(self.save(0,bank,0),0);accepted=self.dump(b'vc0a')
        self.lib.tk_mock_read_fail_key(b'vc0b');error,loaded,slot=self.load(0)
        self.assertEqual((error,slot,loaded[0].count),(0,1,20));self.assertEqual(self.dump(b'vc0a'),accepted)
        self.lib.tk_mock_read_fail_key(None)
    def test_failed_retirement_preserves_both_journals_and_restart_selects_latest_generation(self):
        bank=(Template*3)();self.assertEqual(self.save(0,bank,0),0);_,bank,slot=self.load(0)
        self.lib.tk_mock_fail(8);result=StoreResult();self.assertEqual(self.save(0,bank,slot,30,9,result),0)
        self.assertTrue(result.confirmed);self.assertEqual(result.write_error,-1)
        self.assertTrue(self.dump(b'vc0a'));self.assertTrue(self.dump(b'vc0b'))
        self.lib.tk_mock_fail(0);error,loaded,slot=self.load(0)
        self.assertEqual((error,slot),(0,2));self.assertEqual([x.count for x in loaded],[20,30,0])
    def test_explicit_legacy_compaction_preserves_every_sample_and_next_without_rotation(self):
        for counts,mode in (((0,8,19),'normal'),((48,48,48),'normal'),((20,0,48),'constant'),((48,48,48),'extreme'),((0,0,0),'empty')):
            for next_slot in range(3):
                with self.subTest(counts=counts,mode=mode,next_slot=next_slot):
                    self.lib.tk_mock_reset();bank=(Template*3)()
                    for e,n in enumerate(counts):
                        bank[e].count=n
                        for f in range(n):
                            for d in range(12):bank[e].frame[f].value[d]=(-127 if mode=='constant' else (127 if (f+d)%2 else -127) if mode=='extreme' else (f+d+e)%31-15)
                    original=self.legacy(2,bank,next_slot);self.blob(b'voice2',original)
                    others={b'voice0':self.legacy(0,bank,next_slot),b'cfg_v1':b'opaque-config',b'slots_v1':b'opaque-bonds'}
                    for key,data in others.items():self.blob(key,data)
                    before=bytes(bank);self.assertEqual(self.lib.tk_voice_store_compact_legacy(2,self.scratch),0)
                    error,loaded,slot=self.load(2);self.assertEqual((error,slot),(0,next_slot));self.assertEqual(bytes(loaded),before)
                    self.assertEqual(self.raw(b'voice2'),b'');self.assertTrue(self.raw(b'vc2a'));self.assertEqual(self.raw(b'vc2a')[16],next_slot)
                    for key,data in others.items():self.assertEqual(self.raw(key),data)
                    accepted=(self.raw(b'vc2a'),self.raw(b'vc2b'));commits=self.lib.tk_mock_commit_step()
                    self.lib.tk_mock_fail(8);self.assertEqual(self.lib.tk_voice_store_compact_legacy(2,self.scratch),0)
                    self.assertEqual((self.raw(b'vc2a'),self.raw(b'vc2b')),accepted);self.assertEqual(self.lib.tk_mock_commit_step(),commits)
    def test_legacy_compaction_rejects_missing_corrupt_and_capacity_without_deleting_source(self):
        self.assertNotEqual(self.lib.tk_voice_store_compact_legacy(0,self.scratch),0)
        bank=(Template*3)();bank[0].count=20;C.memmove(bank[0].frame,self.sample(),20*12)
        original=self.legacy(0,bank,2);broken=bytearray(original);broken[25]^=1;self.blob(b'voice0',broken)
        self.assertNotEqual(self.lib.tk_voice_store_compact_legacy(0,self.scratch),0);self.assertEqual(self.raw(b'voice0'),broken)
        self.blob(b'voice0',original);self.lib.tk_mock_capacity(630,630)
        self.assertEqual(self.lib.tk_voice_store_compact_legacy(0,self.scratch),0x1105)
        self.assertEqual(self.raw(b'voice0'),original);self.assertEqual(self.raw(b'vc0a'),b'')
        self.lib.tk_mock_capacity(630,0);self.lib.tk_mock_fail(7)
        self.assertEqual(self.lib.tk_voice_store_compact_legacy(0,self.scratch),0x1105)
        self.assertEqual(self.raw(b'voice0'),original);self.assertEqual(self.raw(b'vc0a'),b'')
    def test_legacy_compaction_write_read_and_retirement_faults_always_leave_recoverable_sample(self):
        for fault in (1,2,4,5,6,8):
            with self.subTest(fault=fault):
                self.lib.tk_mock_reset();bank=(Template*3)();bank[0].count=20;C.memmove(bank[0].frame,self.sample(),20*12)
                original=self.legacy(1,bank,2);self.blob(b'voice1',original);self.lib.tk_mock_fail(fault)
                error=self.lib.tk_voice_store_compact_legacy(1,self.scratch)
                if fault in (2,4):self.assertEqual(error,0);self.assertEqual(self.raw(b'voice1'),b'')
                else:self.assertNotEqual(error,0);self.assertEqual(self.raw(b'voice1'),original)
                self.lib.tk_mock_fail(0);error,loaded,slot=self.load(1)
                self.assertEqual((error,slot),(0,2));self.assertEqual(bytes(loaded),bytes(bank))
    def capture(self,enrolling=True,start=0):
        c=Capture();self.lib.tk_voice_capture_init(C.byref(c),start,enrolling)
        for i in range(1,16):self.assertFalse(self.lib.tk_voice_capture_feed(C.byref(c),20,(start+i*20)&0xffffffff))
        self.assertTrue(c.calibrated);self.assertEqual(c.threshold,128);return c,(start+300)&0xffffffff
    def feed(self,c,level,now):return self.lib.tk_voice_capture_feed(C.byref(c),level,now&0xffffffff)
    def test_calibration_needs_sample_count_and_wall_clock_and_noise_sum_stays_bounded(self):
        c=Capture();self.lib.tk_voice_capture_init(C.byref(c),0,True)
        for _ in range(1000):self.assertFalse(self.feed(c,65535,0))
        self.assertFalse(c.calibrated);self.assertEqual(c.noise_sum,15*65535)
        self.feed(c,65535,300);self.assertTrue(c.calibrated);self.assertGreater(c.threshold,65535)
        self.assertFalse(self.feed(c,65535,320));self.assertFalse(c.started)
    def test_trailing_silence_accepts_only_complete_not_too_short_utterances(self):
        for count,decision in [(14,2),(15,0),(48,0)]:
            with self.subTest(frames=count):
                c,now=self.capture()
                for _ in range(count):now+=20;self.assertTrue(self.feed(c,1000,now))
                for _ in range(14):now+=20;self.assertFalse(self.feed(c,0,now));self.assertFalse(c.done)
                self.feed(c,0,now+20);self.assertTrue(c.done);self.assertEqual(c.decision,decision)
    def test_enrollment_limit48_and_slow_recognition_limit96_reject_next_frame(self):
        for enrolling,limit in [(True,48),(False,96)]:
            with self.subTest(enrolling=enrolling):
                c,now=self.capture(enrolling)
                for _ in range(limit):now+=20;self.assertTrue(self.feed(c,1000,now))
                self.assertFalse(c.done);self.assertFalse(self.feed(c,1000,now+20))
                self.assertTrue(c.done);self.assertEqual(c.decision,3)
    def test_query_minimum_matches_matcher_eight_frames_while_enrollment_needs_fifteen(self):
        for enrolling,count,decision in [(False,7,2),(False,8,0),(False,14,0),(True,14,2),(True,15,0)]:
            with self.subTest(enrolling=enrolling,count=count):
                c,now=self.capture(enrolling)
                for _ in range(count):now+=20;self.assertTrue(self.feed(c,1000,now))
                for _ in range(15):now+=20;self.assertFalse(self.feed(c,0,now))
                self.assertTrue(c.done);self.assertEqual(c.decision,decision)
    def test_three_second_timeout_and_uptime_wrap_never_accept_incomplete_speech(self):
        for start in (0,0xffffff00):
            c,now=self.capture(False,start);self.feed(c,0,(start+3000)&0xffffffff)
            self.assertTrue(c.done);self.assertEqual(c.decision,1)
            c,now=self.capture(False,start)
            for i in range(15):self.assertTrue(self.feed(c,1000,now+(i+1)*20))
            self.assertFalse(self.feed(c,1000,(start+3000)&0xffffffff));self.assertEqual(c.decision,3)
