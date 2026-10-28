"""PCM-to-template integration checks. Synthetic sounds are NOT spoken commands."""
import ctypes as C
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import unittest
import test_features as dsp
import test_matcher as dtw

HERE=Path(__file__).resolve().parent


def acoustic_pattern(style, count=28, amplitude=10000):
    """Deterministic moving formant-like tones, with no human speech labels."""
    result=[]
    for frame in range(count):
        t=frame/(count-1)
        f1,f2=[(350+650*t,1500+100*t),(1900-500*t,3400-200*t),
               (700+100*t,5200-800*t)][style]
        result.append([round(amplitude*(.65*math.sin(2*math.pi*f1*n/16000)+
                                       .35*math.sin(2*math.pi*f2*n/16000)))
                       for n in range(320)])
    return result


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc=os.environ.get('CC') or shutil.which('cc')
        if not cc and os.name=='nt':
            cc='D:/nabo-passport-tools/w64devkit/bin/cc.exe'
        cls.temp=tempfile.TemporaryDirectory(prefix='nabo-voice-pipeline-')
        dest=Path(cls.temp.name)/('pipeline.dll' if os.name=='nt' else 'pipeline.so')
        subprocess.run([cc,'-std=c11','-O2','-Wall','-Wextra','-Werror','-fPIC','-shared',
                        str(HERE/'features.c'),str(HERE/'matcher.c'),'-o',str(dest)],check=True)
        cls.lib=C.CDLL(str(dest))
        cls.lib.vp_features_frame.argtypes=[C.POINTER(dsp.Workspace),C.POINTER(C.c_int16),
                                           C.POINTER(C.c_int16),C.POINTER(C.c_uint32)]
        cls.lib.vp_quantize_features.argtypes=[C.POINTER(C.c_int16),C.POINTER(dtw.Frame)]
        cls.lib.vp_bank_init.argtypes=[C.POINTER(dtw.Bank)]
        cls.lib.vp_bank_enroll.argtypes=[C.POINTER(dtw.Bank),C.c_uint,C.c_uint,
                                       C.POINTER(dtw.Frame),C.c_size_t]
        cls.lib.vp_bank_enroll.restype=C.c_bool
        cls.lib.vp_matcher_bytes.restype=C.c_size_t
        cls.lib.vp_matcher_begin.argtypes=[C.c_void_p,C.POINTER(dtw.Bank),C.POINTER(dtw.Options)]
        cls.lib.vp_matcher_push.argtypes=[C.c_void_p,C.POINTER(dtw.Frame),C.c_bool]
        cls.lib.vp_matcher_finish.argtypes=[C.c_void_p]
        cls.lib.vp_matcher_finish.restype=dtw.Result

    @classmethod
    def tearDownClass(cls):
        if os.name=='nt':
            import _ctypes
            _ctypes.FreeLibrary(cls.lib._handle)
        cls.temp.cleanup()

    def setUp(self):
        self.bank=dtw.Bank()
        self.lib.vp_bank_init(C.byref(self.bank))
        self.workspace=dsp.Workspace()

    def features(self, pcm_frames):
        result=[]
        for samples in pcm_frames:
            coef,level,frame=(C.c_int16*12)(),C.c_uint32(),dtw.Frame()
            self.lib.vp_features_frame(C.byref(self.workspace),(C.c_int16*320)(*samples),
                                      coef,C.byref(level))
            self.lib.vp_quantize_features(coef,C.byref(frame))
            result.append((frame,level.value>=200)) # Experimental energy gate, NOT a speech VAD.
        return result

    def enroll(self, label, pcm_frames):
        frames=[frame for frame,voiced in self.features(pcm_frames) if voiced]
        self.assertTrue(self.lib.vp_bank_enroll(C.byref(self.bank),label,0,
                                              (dtw.Frame*len(frames))(*frames),len(frames)))

    def query(self, pcm_frames, options=None):
        # Word IDs/names are never passed to the acoustic frontend or query.
        matcher=C.create_string_buffer(self.lib.vp_matcher_bytes())
        self.lib.vp_matcher_begin(matcher,C.byref(self.bank),C.byref(options) if options else None)
        for frame,voiced in self.features(pcm_frames):
            self.lib.vp_matcher_push(matcher,C.byref(frame),voiced)
        return self.lib.vp_matcher_finish(matcher)

    def test_pcm_end_to_end_with_changed_labels_gain_and_time(self):
        self.enroll(4,acoustic_pattern(0))
        self.enroll(1,acoustic_pattern(1))
        # New amplitude and twice the duration, not the same PCM array.
        query=[frame for frame in acoustic_pattern(0,amplitude=4300) for _ in range(2)]
        result=self.query(query)
        self.assertEqual((result.decision,result.word),(dtw.ACCEPTED,4))
        result=self.query(acoustic_pattern(1,amplitude=5000))
        self.assertEqual((result.decision,result.word),(dtw.ACCEPTED,1))

    def test_pcm_silence_and_low_level_noise_do_not_open_a_word(self):
        self.enroll(0,acoustic_pattern(0))
        rng=random.Random(32)
        for query in ([[0]*320]*30,[[rng.randint(-8,8) for _ in range(320)] for _ in range(30)]):
            result=self.query(query)
            self.assertEqual((result.decision,result.word),(dtw.NO_SPEECH,-1))

    def test_identical_acoustics_with_two_labels_are_ambiguous(self):
        self.enroll(0,acoustic_pattern(0))
        self.enroll(3,acoustic_pattern(0))
        result=self.query(acoustic_pattern(0,amplitude=6000))
        self.assertEqual((result.decision,result.word),(dtw.AMBIGUOUS,-1))

    def test_unfamiliar_synthetic_sound_is_rejected(self):
        self.enroll(0,acoustic_pattern(0))
        self.enroll(1,acoustic_pattern(1))
        result=self.query(acoustic_pattern(2))
        self.assertNotEqual(result.decision,dtw.ACCEPTED)
        self.assertEqual(result.word,-1)


if __name__=='__main__':
    unittest.main()
