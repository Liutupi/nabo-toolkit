"""Actual voice worker lifecycle with fake RTOS/NVS/PCM; no speech acceptance."""
import ctypes as C
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from tk_native import ROOT,unload

class Snapshot(C.Structure):
    _fields_=[('generation',C.c_uint32),('token',C.c_uint32)]+[(n,C.c_int) for n in ('status','word','example','decision')]+[
        ('active',C.c_bool),('enrolling',C.c_bool),('counts_padding',C.c_uint8*2),('counts',C.c_uint8*7),('invalid_mask',C.c_uint8),
        ('distance',C.c_uint16),('runner_up_distance',C.c_uint16),('frames',C.c_uint16),('error',C.c_int),('error_stage',C.c_int)]+[
        (n,C.c_uint32) for n in ('heap','largest','peak','frame_max_us','threshold')]+[
        ('storage_write_error',C.c_int),('storage_read_error',C.c_int),('storage_unknown',C.c_bool),
        ('stack_low_watermark',C.c_uint32),('heap_integrity',C.c_bool)]

class VoiceRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();folder=Path(cls.temp.name)
        headers={
            'bsp_audio.h':'#include "esp_err.h"\n#include <stddef.h>\nesp_err_t bsp_audio_read(void *pcm,size_t bytes);\n',
            'esp_system.h':'#include <stddef.h>\nsize_t esp_get_free_heap_size(void);\n',
            'esp_heap_caps.h':'#include <stddef.h>\n#include <stdbool.h>\n#define MALLOC_CAP_8BIT 1\nsize_t heap_caps_get_largest_free_block(unsigned caps);\nbool heap_caps_check_integrity_all(bool print_errors);\n',
            'esp_timer.h':'#include <stdint.h>\nint64_t esp_timer_get_time(void);\n',
            'freertos/FreeRTOS.h':'#pragma once\n#include <stdint.h>\n#include <stdatomic.h>\n#define portMAX_DELAY UINT32_MAX\n#define pdTRUE 1\n#define pdPASS 1\ntypedef struct {atomic_flag lock;} portMUX_TYPE;\n#define portMUX_INITIALIZER_UNLOCKED {ATOMIC_FLAG_INIT}\nstatic inline void enter(portMUX_TYPE *m){while(atomic_flag_test_and_set(&m->lock)){};}\n#define portENTER_CRITICAL(m) enter(m)\n#define portEXIT_CRITICAL(m) atomic_flag_clear(&(m)->lock)\n',
            'freertos/queue.h':'#pragma once\n#include <stdint.h>\ntypedef struct mock_queue *QueueHandle_t;\nQueueHandle_t xQueueCreate(unsigned length,unsigned size);\nvoid vQueueDelete(QueueHandle_t q);\nint xQueueSend(QueueHandle_t q,const void *item,uint32_t wait);\nint xQueueReceive(QueueHandle_t q,void *item,uint32_t wait);\n',
            'freertos/task.h':'#pragma once\ntypedef void (*TaskFunction_t)(void *);\nint xTaskCreate(TaskFunction_t task,const char *name,unsigned stack,void *arg,unsigned priority,void *handle);\nunsigned uxTaskGetStackHighWaterMark(void *task);\n',
        }
        for name,text in headers.items():p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
        dest=folder/'voice_runtime.so';main=ROOT/'firmware/main';probe=ROOT/'tools/voice_probe'
        result=subprocess.run(['cc','-shared','-fPIC','-std=c11','-O2','-Wall','-Wextra','-Werror',
            '-I',str(folder),'-I',str(ROOT/'tests/support'),'-I',str(main),'-I',str(probe),
            str(ROOT/'tests/tk_voice_runtime_host.c'),str(main/'tk_voice_store.c'),str(main/'tk_voice_capture.c'),
            str(probe/'features.c'),str(probe/'matcher.c'),str(ROOT/'tests/tk_store_mock.c'),'-o',str(dest)],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stderr)
        cls.lib=C.CDLL(str(dest));l=cls.lib
        l.tk_voice_snapshot.restype=Snapshot;l.tk_voice_active.restype=C.c_bool;l.tk_voice_prepare_sleep.restype=C.c_bool
        l.tk_voice_request_enroll.argtypes=[C.c_uint,C.c_uint32];l.tk_voice_request_recognize.argtypes=[C.c_uint32]
        l.tk_voice_host_audio.argtypes=[C.c_uint,C.c_int,C.c_int];l.tk_voice_host_memory.argtypes=[C.c_uint,C.c_uint]
        l.tk_mock_dump.argtypes=[C.c_char_p,C.POINTER(C.c_uint8)]
        l.tk_mock_blob.argtypes=[C.c_char_p,C.POINTER(C.c_uint8),C.c_uint]
        if l.tk_voice_host_snapshot_bytes()!=C.sizeof(Snapshot):raise RuntimeError('Voice snapshot ABI drift')
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def setUp(self):self.lib.tk_voice_host_reset();self.lib.tk_mock_reset();self.assertEqual(self.lib.tk_voice_init(),0)
    def dump(self,key):
        if key.startswith(b'voice'):
            candidates=[self.dump(b'vc'+key[-1:]+suffix) for suffix in (b'a',b'b')]
            candidates=[x for x in candidates if x]
            if candidates:return max(candidates,key=lambda x:int.from_bytes(x[20:24],'little'))
        data=(C.c_uint8*4016)();n=self.lib.tk_mock_dump(key,data);return bytes(data[:n])
    def test_enrollment_token_count_and_slot_rotation_commit_only_one_word(self):
        self.assertLess(self.lib.tk_voice_host_workspace_bytes(),20*1024)
        self.assertGreater(self.lib.tk_voice_host_workspace_bytes()-self.lib.tk_voice_host_enroll_workspace_bytes(),2400)
        for i in range(4):
            self.lib.tk_voice_host_audio(20,0,0);self.assertEqual(self.lib.tk_voice_request_enroll(3,100+i),0)
            self.assertTrue(self.lib.tk_voice_active());self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
            self.assertFalse(v.active);self.assertFalse(self.lib.tk_voice_active());self.assertEqual(v.status,4)
            self.assertEqual((v.token,v.generation,v.word,v.example,v.decision),(100+i,i+1,3,i%3,0))
            self.assertEqual(list(v.counts),[0,0,0,min(i+1,3),0,0,0]);self.assertEqual(v.error_stage,0)
        self.assertLess(len(self.dump(b'voice3')),1752);self.assertTrue(self.dump(b'voice3'));self.assertEqual(self.dump(b'voice0'),b'')
    def test_memory_gate_and_read_error_are_distinct_terminal_failures(self):
        self.lib.tk_voice_host_memory(50000,40000);self.assertEqual(self.lib.tk_voice_request_enroll(0,1),0)
        self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot();self.assertEqual((v.status,v.error_stage),(6,1))
        self.assertFalse(v.active);self.assertEqual(self.lib.tk_voice_host_reads(),0)
        self.lib.tk_voice_host_memory(100000,80000);self.lib.tk_voice_host_audio(20,1,0)
        self.assertEqual(self.lib.tk_voice_request_enroll(0,2),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.error_stage),(6,2));self.assertFalse(v.active);self.assertEqual(self.dump(b'voice0'),b'')
    def test_full_bank_repeated_capture_and_match_keeps_all_records_and_bounds(self):
        # Exercise every template row and allocation lifecycle with real frontend
        # output. Identical fake words must reject as ambiguous, not pick a page.
        token=200
        for word in range(7):
            for example in range(3):
                self.lib.tk_voice_host_audio(20+example,0,0)
                self.assertEqual(self.lib.tk_voice_request_enroll(word,token),0)
                self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot();token+=1
                self.assertEqual((v.status,v.word,v.example,v.counts[word]),(4,word,example,example+1))
        records={w:self.dump(f'voice{w}'.encode()) for w in range(7)}
        for _ in range(30):
            self.lib.tk_voice_host_audio(21,0,0)
            self.assertEqual(self.lib.tk_voice_request_recognize(token),0);token+=1
            self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
            self.assertEqual((v.status,v.decision,v.word),(4,7,-1));self.assertEqual(list(v.counts),[3]*7)
            self.assertFalse(v.active);self.assertEqual(v.invalid_mask,0)
        for word,data in records.items():self.assertEqual(self.dump(f'voice{word}'.encode()),data)
    def test_diagnostics_align_counts_and_check_heap_only_at_lifecycle_boundaries(self):
        self.assertEqual(self.lib.tk_voice_host_counts_offset()%4,0)
        self.assertEqual(self.lib.tk_voice_host_counts_offset(),Snapshot.counts.offset)
        initial=self.lib.tk_voice_host_integrity_checks();self.assertEqual(initial,1)
        self.lib.tk_voice_host_diagnostics(1536,1);self.lib.tk_voice_host_audio(20,0,0)
        self.assertEqual(self.lib.tk_voice_request_enroll(6,800),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.word,v.counts[6]),(4,6,1));self.assertTrue(v.heap_integrity)
        self.assertEqual(v.stack_low_watermark,1536)
        self.assertEqual(self.lib.tk_voice_host_integrity_checks()-initial,3,'Not one integrity scan per PCM frame')
        self.lib.tk_voice_host_diagnostics(1024,0);self.lib.tk_voice_host_audio(20,0,0)
        self.assertEqual(self.lib.tk_voice_request_recognize(801),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual(v.stack_low_watermark,1024);self.assertFalse(v.heap_integrity)
    def test_store_failure_does_not_advance_counts_or_rotation(self):
        self.lib.tk_voice_host_audio(20,0,0);self.lib.tk_mock_fail(1)
        self.assertEqual(self.lib.tk_voice_request_enroll(2,50),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.error_stage,v.example),(6,3,0));self.assertEqual(list(v.counts),[0]*7)
        self.assertEqual(self.dump(b'voice2'),b'');self.lib.tk_mock_fail(0);self.lib.tk_voice_host_audio(20,0,0)
        self.assertEqual(self.lib.tk_voice_request_enroll(2,51),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.example,v.counts[2]),(4,0,1))
    def test_readback_confirms_immediate_write_despite_sdk_error_and_rotation_advances(self):
        self.lib.tk_voice_host_audio(20,0,0);self.lib.tk_mock_fail(4)
        self.assertEqual(self.lib.tk_voice_request_enroll(2,60),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.error,v.error_stage,v.example,v.counts[2]),(4,0,0,0,1))
        self.assertEqual((v.storage_write_error,v.storage_read_error),(0x1108,0));self.assertFalse(v.storage_unknown)
        self.assertEqual(v.invalid_mask,0);self.assertFalse(v.active)
        self.lib.tk_mock_fail(0);self.lib.tk_voice_host_audio(20,0,0)
        self.assertEqual(self.lib.tk_voice_request_enroll(2,61),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.example,v.counts[2]),(4,1,2));self.assertEqual(v.storage_write_error,0)
    def test_unknown_readback_masks_only_affected_word_until_fresh_bank_load(self):
        self.lib.tk_voice_host_audio(20,0,0)
        self.assertEqual(self.lib.tk_voice_request_enroll(1,70),0);self.lib.tk_voice_host_drain()
        other=self.dump(b'voice1');self.lib.tk_voice_host_audio(20,0,0);self.lib.tk_mock_fail(6)
        self.assertEqual(self.lib.tk_voice_request_enroll(2,71),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.error_stage),(6,3));self.assertFalse(v.active)
        self.assertTrue(v.storage_unknown);self.assertEqual((v.storage_write_error,v.storage_read_error),(0,-1))
        self.assertEqual(list(v.counts),[0,1,0,0,0,0,0]);self.assertEqual(v.invalid_mask,4)
        self.assertEqual(self.dump(b'voice1'),other);self.assertTrue(self.dump(b'voice2'))
        self.lib.tk_mock_fail(0);self.lib.tk_voice_host_audio(20,0,0)
        self.assertEqual(self.lib.tk_voice_request_enroll(2,72),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.example,v.counts[2]),(4,1,2));self.assertEqual(v.invalid_mask,0)
        self.assertFalse(v.storage_unknown);self.assertEqual(self.dump(b'voice1'),other)
    def test_unknown_missing_word_is_not_silently_reenrolled_and_other_word_stays_usable(self):
        for word in (1,2):
            self.lib.tk_voice_host_audio(20,0,0);self.assertEqual(self.lib.tk_voice_request_enroll(word,900+word),0);self.lib.tk_voice_host_drain()
        self.lib.tk_mock_fail(6);self.lib.tk_voice_host_audio(20,0,0)
        self.assertEqual(self.lib.tk_voice_request_enroll(2,903),0);self.lib.tk_voice_host_drain()
        self.assertTrue(self.lib.tk_voice_snapshot().storage_unknown);self.lib.tk_mock_fail(0)
        for suffix in (b'a',b'b'):self.lib.tk_mock_blob(b'vc2'+suffix,(C.c_uint8*1)(),0)
        self.lib.tk_voice_host_audio(20,0,0);self.assertEqual(self.lib.tk_voice_request_enroll(2,904),0)
        self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.error_stage),(6,3));self.assertEqual(self.lib.tk_voice_host_reads(),0)
        self.assertEqual(self.dump(b'voice2'),b'')
        self.assertEqual(self.lib.tk_voice_request_recognize(905),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.word,v.decision),(4,1,0));self.assertEqual(v.counts[1],1);self.assertEqual(v.invalid_mask,4)
    def test_operation_allocation_failure_and_late_cancel_release_base_and_operation(self):
        for fail,cancel,status,allocations in ((1,0,6,1),(2,0,6,2),(0,1,5,1),(0,2,5,2)):
            with self.subTest(fail=fail,cancel=cancel):
                self.lib.tk_voice_host_allocation_fault(fail,cancel);self.lib.tk_voice_host_audio(20,0,0)
                self.assertEqual(self.lib.tk_voice_request_enroll(3,950+fail+cancel),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
                self.assertEqual(v.status,status);self.assertFalse(v.active)
                self.assertEqual(self.lib.tk_voice_host_allocations(),allocations)
                self.assertEqual(self.lib.tk_voice_host_live_allocations(),0);self.assertEqual(self.lib.tk_voice_host_reads(),0)
                self.assertEqual(self.dump(b'voice3'),b'')
        self.lib.tk_voice_host_allocation_fault(0,0)
    def test_cancel_during_codec_read_stays_active_until_read_acknowledges(self):
        self.lib.tk_voice_host_audio(20,0,1);self.assertEqual(self.lib.tk_voice_request_enroll(0,77),0)
        thread=threading.Thread(target=self.lib.tk_voice_host_drain);thread.start()
        try:
            deadline=time.monotonic()+2
            while not self.lib.tk_voice_host_read_entered() and time.monotonic()<deadline:time.sleep(.005)
            self.assertTrue(self.lib.tk_voice_host_read_entered())
            self.assertFalse(self.lib.tk_voice_prepare_sleep());self.assertTrue(self.lib.tk_voice_active())
            self.assertTrue(self.lib.tk_voice_snapshot().active)
        finally:self.lib.tk_voice_host_release();thread.join(timeout=2)
        self.assertFalse(thread.is_alive());v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.token),(5,77));self.assertFalse(v.active);self.assertTrue(self.lib.tk_voice_prepare_sleep())
        self.assertEqual(self.dump(b'voice0'),b'')
    def test_queued_cancel_and_no_template_recognition_never_read_codec(self):
        self.assertEqual(self.lib.tk_voice_request_enroll(0,11),0);self.lib.tk_voice_cancel();self.lib.tk_voice_host_drain()
        self.assertEqual(self.lib.tk_voice_snapshot().status,5);self.assertEqual(self.lib.tk_voice_host_reads(),0)
        self.assertEqual(self.lib.tk_voice_request_recognize(12),0);self.lib.tk_voice_host_drain();v=self.lib.tk_voice_snapshot()
        self.assertEqual((v.status,v.decision,v.word),(4,4,-1));self.assertEqual(self.lib.tk_voice_host_reads(),0)
    def test_explicit_compaction_requires_idle_and_frees_scratch_without_codec_reads(self):
        self.lib.tk_voice_host_reset()
        self.assertNotEqual(self.lib.tk_voice_compact_legacy(),0)
        self.assertFalse(self.lib.tk_voice_active());self.assertEqual(self.lib.tk_voice_init(),0)
        self.lib.tk_voice_host_allocation_fault(1,0)
        self.assertNotEqual(self.lib.tk_voice_compact_legacy(),0)
        self.assertFalse(self.lib.tk_voice_active());self.assertEqual(self.lib.tk_voice_host_live_allocations(),0)
        self.lib.tk_voice_host_allocation_fault(0,0)
        self.assertEqual(self.lib.tk_voice_compact_legacy(),0)
        self.assertEqual((self.lib.tk_voice_host_reads(),self.lib.tk_voice_host_live_allocations()),(0,0))
        self.assertEqual(self.lib.tk_voice_request_enroll(0,981),0)
        self.assertNotEqual(self.lib.tk_voice_compact_legacy(),0)
        self.assertTrue(self.lib.tk_voice_active());self.lib.tk_voice_cancel();self.lib.tk_voice_host_drain()
