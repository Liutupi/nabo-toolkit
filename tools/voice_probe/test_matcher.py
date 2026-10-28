"""Synthetic coefficient-trajectory tests, not a speech-recognition accuracy test.

The production candidate firmware is not compiled or touched. These tests build
only matcher.c with a native C11 compiler. PCM/frontend checks live separately.
"""
import ctypes as C
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
DIM, WORDS, EXAMPLES, MAX_TEMPLATE, MAX_QUERY = 12, 7, 3, 48, 96
ACCEPTED, NO_SPEECH, TOO_SHORT, TOO_LONG, NO_TEMPLATE, NO_DURATION_MATCH, TOO_DISTANT, AMBIGUOUS, INVALID_INPUT = range(9)


class Frame(C.Structure):
    _fields_ = [('value', C.c_int8 * DIM)]


class Template(C.Structure):
    _fields_ = [('frame', Frame * MAX_TEMPLATE), ('count', C.c_uint8)]


class Bank(C.Structure):
    _fields_ = [('word', (Template * EXAMPLES) * WORDS)]


class Options(C.Structure):
    _fields_ = [('max_distance', C.c_uint8), ('min_margin', C.c_uint8)]


class Result(C.Structure):
    _fields_ = [('decision', C.c_int), ('word', C.c_int), ('speech_frames', C.c_uint),
                ('best_distance', C.c_uint16), ('runner_up_distance', C.c_uint16)]


def phrase(style, count=24):
    """Smooth, signed spectral-coefficient trajectories for algorithm testing."""
    bases = [
        [-60, 40, -20, 55, -35, 20, -45, 30, -15, 50, -25, 10],
        [50, -50, 40, -30, 60, -20, 45, -35, 25, -55, 15, -40],
        [-20, -30, -40, -50, -60, -45, -35, -25, -15, -5, 10, 25],
    ]
    return [Frame((C.c_int8 * DIM)(*[base + round(12 * math.sin((i / (count - 1)) * math.pi * (d % 3 + 1)))
                                    for d, base in enumerate(bases[style])])) for i in range(count)]


class MatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        suffix = '.dll' if sys.platform == 'win32' else '.so'
        library = Path(cls.temp.name) / ('matcher' + suffix)
        cls.object = Path(cls.temp.name) / 'matcher.o'
        budget = Path(cls.temp.name) / 'budget.c'
        budget.write_text('''#include "matcher.h"
#include "features.h"
typedef struct {
    vp_bank_t bank;
    union {vp_matcher_t matcher;vp_frame_t enrollment[VP_MAX_TEMPLATE_FRAMES];};
    vp_features_t features;
    int16_t pcm[VP_PCM_SAMPLES];
    uint8_t next[VP_MAX_WORDS];
} probe_workspace_t;
_Static_assert(sizeof(probe_workspace_t)<20u*1024u,"Seven-word probe job exceeds 20KiB");
size_t vp_probe_job_bytes(void){return sizeof(probe_workspace_t);}
size_t vp_probe_frontend_bytes(void){return sizeof(vp_features_t);}
''', encoding='utf-8')
        common = ['cc', '-std=c11', '-Os', '-Wall', '-Wextra', '-Werror', '-I', str(HERE)]
        subprocess.run(common + ['-c', str(HERE / 'matcher.c'), '-o', str(cls.object)], check=True)
        subprocess.run(common + ['-shared', '-fPIC', str(HERE / 'matcher.c'), str(budget), '-o', str(library)], check=True)
        cls.lib = C.CDLL(str(library))
        lib = cls.lib
        for name in ('vp_bank_bytes', 'vp_matcher_bytes', 'vp_enrollment_buffer_bytes', 'vp_probe_job_bytes', 'vp_probe_frontend_bytes'):
            getattr(lib, name).restype = C.c_size_t
        lib.vp_bank_init.argtypes = [C.POINTER(Bank)]
        lib.vp_bank_enroll.argtypes = [C.POINTER(Bank), C.c_uint, C.c_uint, C.POINTER(Frame), C.c_size_t]
        lib.vp_bank_enroll.restype = C.c_bool
        lib.vp_quantize_features.argtypes = [C.POINTER(C.c_int16), C.POINTER(Frame)]
        lib.vp_matcher_begin.argtypes = [C.c_void_p, C.POINTER(Bank), C.POINTER(Options)]
        lib.vp_matcher_push.argtypes = [C.c_void_p, C.POINTER(Frame), C.c_bool]
        lib.vp_matcher_push.restype = C.c_bool
        lib.vp_matcher_finish.argtypes = [C.c_void_p]
        lib.vp_matcher_finish.restype = Result

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'lib'):
            if sys.platform == 'win32':
                import _ctypes
                _ctypes.FreeLibrary(cls.lib._handle)
            cls.lib = None
        cls.temp.cleanup()

    def setUp(self):
        self.bank = Bank()
        self.lib.vp_bank_init(C.byref(self.bank))
        size = self.lib.vp_matcher_bytes()
        self.guarded = C.create_string_buffer(bytes([0xA5]) * (size + 32), size + 32)
        self.matcher = C.cast(C.byref(self.guarded, 16), C.c_void_p)

    def enroll(self, word, frames, example=0):
        data = (Frame * len(frames))(*frames)
        self.assertTrue(self.lib.vp_bank_enroll(C.byref(self.bank), word, example, data, len(frames)))

    def begin(self, options=None):
        self.lib.vp_matcher_begin(self.matcher, C.byref(self.bank), C.byref(options) if options else None)

    def query(self, frames, silence=False, options=None):
        self.begin(options)
        for frame in frames:
            self.lib.vp_matcher_push(self.matcher, C.byref(frame), not silence)
        result = self.lib.vp_matcher_finish(self.matcher)
        self.assertEqual(self.guarded.raw[:16], bytes([0xA5]) * 16)
        self.assertEqual(self.guarded.raw[-16:], bytes([0xA5]) * 16)
        return result

    def test_enrollment_required_and_no_builtin_words(self):
        r = self.query(phrase(0))
        self.assertEqual((r.decision, r.word), (NO_TEMPLATE, -1))

    def test_exact_query_and_twofold_time_stretch_match_the_enrolled_word(self):
        a, b = phrase(0), phrase(1)
        self.enroll(0, a); self.enroll(1, b)
        for query in (a, [x for frame in a for x in (frame, frame)], a[::2]):
            r = self.query(query)
            self.assertEqual((r.decision, r.word), (ACCEPTED, 0))
            self.assertLessEqual(r.best_distance, 2)
        self.assertEqual(self.query(b).word, 1)

    def test_small_feature_noise_and_same_word_examples_are_not_ambiguous(self):
        a = phrase(0)
        noisy = [Frame((C.c_int8 * DIM)(*[v + (1 if i % 2 else -1) for v in frame.value])) for i, frame in enumerate(a)]
        self.enroll(0, a, 0); self.enroll(0, noisy, 1); self.enroll(1, phrase(1))
        r = self.query(noisy)
        self.assertEqual((r.decision, r.word, r.best_distance), (ACCEPTED, 0, 0))

    def test_silence_is_vad_gated_and_not_recognized_as_a_word(self):
        self.enroll(0, phrase(0))
        r = self.query([Frame()] * MAX_QUERY, silence=True)
        self.assertEqual((r.decision, r.word, r.speech_frames), (NO_SPEECH, -1, 0))
        self.begin()
        self.assertTrue(self.lib.vp_matcher_push(self.matcher, None, False))
        self.assertEqual(self.lib.vp_matcher_finish(self.matcher).decision, NO_SPEECH)
        self.begin()
        for frame in phrase(0):
            self.assertTrue(self.lib.vp_matcher_push(self.matcher, None, False))
            self.assertTrue(self.lib.vp_matcher_push(self.matcher, C.byref(frame), True))
        r = self.lib.vp_matcher_finish(self.matcher)
        self.assertEqual((r.decision, r.word, r.speech_frames), (ACCEPTED, 0, 24))

    def test_unknown_acoustics_and_reversed_transitions_are_rejected(self):
        self.enroll(0, phrase(0)); self.enroll(1, phrase(1))
        unknown = [Frame((C.c_int8 * DIM)(*([120] * DIM)))] * 24
        self.assertEqual((self.query(unknown).decision, self.query(unknown).word), (TOO_DISTANT, -1))
        self.lib.vp_bank_init(C.byref(self.bank))
        transitions = [Frame((C.c_int8 * DIM)(*([level] * DIM))) for level in (-80, -25, 30, 80) for _ in range(8)]
        self.enroll(0, transitions)
        self.assertEqual(self.query(list(reversed(transitions)), options=Options(8, 4)).decision, TOO_DISTANT)

    def test_different_words_with_identical_or_too_close_templates_are_ambiguous(self):
        a = phrase(0)
        self.enroll(0, a); self.enroll(1, a)
        self.assertEqual((self.query(a).decision, self.query(a).word), (AMBIGUOUS, -1))
        self.assertEqual(self.query(a, options=Options(18, 0)).decision, AMBIGUOUS, 'Exact ties must still reject with margin zero')
        near = [Frame((C.c_int8 * DIM)(*[v + 1 for v in frame.value])) for frame in a]
        self.enroll(1, near)
        self.assertEqual(self.query(a).decision, AMBIGUOUS)

    def test_two_unit_default_margin_keeps_ties_and_one_unit_gaps_rejected(self):
        # Boundary behavior only; actual speech calibration is private and separate.
        a=[Frame((C.c_int8*DIM)(*[0]*DIM)) for _ in range(24)]
        self.enroll(0,a)
        for gap in (0,1,2,3):
            b=[Frame((C.c_int8*DIM)(*[gap]*DIM)) for _ in range(24)]
            self.enroll(1,b)
            result=self.query(a)
            self.assertEqual(result.decision,ACCEPTED if gap>=2 else AMBIGUOUS)
            self.assertEqual(result.word,0 if gap>=2 else -1)
        self.assertEqual(self.query(a,options=Options(18,4)).decision,AMBIGUOUS)

    def test_too_short_too_long_and_duration_mismatch_do_not_truncate_into_a_match(self):
        self.enroll(0, phrase(0, 48))
        self.assertEqual(self.query(phrase(0, 7)).decision, TOO_SHORT)
        self.assertEqual(self.query(phrase(0, 12)).decision, NO_DURATION_MATCH)
        self.assertEqual(self.query(phrase(0, MAX_QUERY + 1)).decision, TOO_LONG)
        self.begin(); self.assertFalse(self.lib.vp_matcher_push(self.matcher, None, True))
        self.assertEqual(self.lib.vp_matcher_finish(self.matcher).decision, INVALID_INPUT)

    def test_invalid_enrollment_preserves_bank_and_corrupt_lengths_stay_bounded(self):
        self.enroll(0, phrase(0)); before = bytes(self.bank)
        frames = (Frame * 49)(*phrase(1, 49))
        for word, example, count in [(WORDS, 0, 24), (0, 3, 24), (0, 0, 7), (0, 0, 49)]:
            self.assertFalse(self.lib.vp_bank_enroll(C.byref(self.bank), word, example, frames, count))
            self.assertEqual(bytes(self.bank), before)
        self.bank.word[0][0].count = 255
        self.assertEqual(self.query(phrase(0)).decision, NO_TEMPLATE)

    def test_fixed_point_quantization_rounds_saturates_and_is_symmetric(self):
        values = [-32768, -2048, -24, -8, -7, 0, 7, 8, 24, 2048, 32767, 16]
        output = Frame()
        self.lib.vp_quantize_features((C.c_int16 * DIM)(*values), C.byref(output))
        self.assertEqual(list(output.value), [-127, -127, -2, -1, 0, 0, 0, 1, 2, 127, 127, 1])

    def test_all_seven_words_three_examples_and_maximum_query_fit_the_same_guarded_workspace(self):
        for word in range(WORDS):
            frame = Frame((C.c_int8 * DIM)(*([-90 + word * 30] * DIM)))
            for example in range(EXAMPLES):
                self.enroll(word, [frame] * MAX_TEMPLATE, example)
        query = [Frame((C.c_int8 * DIM)(*([90] * DIM)))] * MAX_QUERY
        r = self.query(query)
        self.assertEqual((r.decision, r.word, r.speech_frames, r.best_distance), (ACCEPTED, 6, MAX_QUERY, 0))
        self.assertEqual(r.runner_up_distance, 30)

    def test_full_scale_feature_difference_never_wraps_the_cost_accumulator(self):
        self.enroll(0, [Frame((C.c_int8 * DIM)(*([127] * DIM)))] * MAX_TEMPLATE)
        r = self.query([Frame((C.c_int8 * DIM)(*([-128] * DIM)))] * MAX_QUERY)
        self.assertEqual((r.decision, r.word, r.best_distance), (TOO_DISTANT, -1, 255))

    def test_memory_budget_and_native_object_size_are_bounded(self):
        self.assertEqual(self.lib.vp_bank_bytes(), C.sizeof(Bank))
        self.assertEqual(self.lib.vp_enrollment_buffer_bytes(), MAX_TEMPLATE * C.sizeof(Frame))
        core = self.lib.vp_bank_bytes() + self.lib.vp_matcher_bytes() + self.lib.vp_enrollment_buffer_bytes()
        self.assertLess(core, 16 * 1024)
        job = self.lib.vp_probe_job_bytes()
        self.assertEqual(self.lib.vp_probe_frontend_bytes(),4096)
        self.assertLess(job,20*1024,'Measured seven-word union + actual frontend + PCM + slot counters')
        size = shutil.which('size')
        self.assertIsNotNone(size, 'Native binutils size is required for this probe check')
        output = subprocess.check_output([size, str(self.object)], text=True)
        text = int(output.splitlines()[-1].split()[0])
        self.assertLess(text, 20 * 1024, 'Native object estimate only; C3 size still needs its own build')
        type(self).metrics = {'bank_bytes': self.lib.vp_bank_bytes(), 'matcher_bytes': self.lib.vp_matcher_bytes(),
                              'enrollment_buffer_bytes': self.lib.vp_enrollment_buffer_bytes(),
                              'core_ram_bytes': core, 'frontend_bytes': self.lib.vp_probe_frontend_bytes(),
                              'probe_union_job_bytes': job,
                              'native_object_text_bytes': text}


if __name__ == '__main__':
    suite = unittest.main(verbosity=2, exit=False)
    if suite.result.wasSuccessful():
        print('Host feasibility metrics (not device acceptance):', MatcherTests.metrics)
    sys.exit(0 if suite.result.wasSuccessful() else 1)
