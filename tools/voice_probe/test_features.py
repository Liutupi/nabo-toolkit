"""Acoustic/DSP checks on synthetic PCM, not speech-accuracy acceptance."""
import ctypes as C
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Workspace(C.Structure):
    _fields_ = [('real', C.c_int32*512), ('imag', C.c_int32*512)]


def tone(hz, amplitude=12000, phase=0, offset=0):
    return [max(-32768, min(32767, round(offset+amplitude*math.sin(
        2*math.pi*hz*i/16000+phase)))) for i in range(320)]


def reference(pcm):
    """Independent floating-point DFT/mel/DCT reference, only on the host."""
    dc = math.trunc(sum(pcm)/320)
    signal = [v-dc for v in pcm]
    peak = max(map(abs, signal))
    if peak < 16:
        return [0]*12
    samples = [v*16384/peak*(.5-.5*math.cos(2*math.pi*n/319))
               for n, v in enumerate(signal)]
    spectrum = []
    for k in range(257):
        real = sum(v*math.cos(2*math.pi*k*n/512) for n,v in enumerate(samples))/512
        imag = sum(-v*math.sin(2*math.pi*k*n/512) for n,v in enumerate(samples))/512
        spectrum.append(real*real+imag*imag)
    lo, hi = [2595*math.log10(1+f/700) for f in (80,7600)]
    edges = [math.floor(513*700*(10**((lo+(hi-lo)*n/21)/2595)-1)/16000)
             for n in range(22)]
    bands = []
    for band in range(20):
        a,b,c = edges[band:band+3]
        energy = sum(spectrum[k]*(k-a)/(b-a) for k in range(a+1,b))
        energy += spectrum[b]
        energy += sum(spectrum[k]*(c-k)/(c-b) for k in range(b+1,c))
        bands.append(256*math.log2(energy+1))
    return [sum(x*math.cos(math.pi*k*(n+.5)/20)
                for n,x in enumerate(bands))/20 for k in range(1,13)]


class FeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = os.environ.get('CC') or shutil.which('cc')
        if not compiler and os.name == 'nt':
            candidate = Path('D:/nabo-passport-tools/w64devkit/bin/cc.exe')
            if candidate.exists():
                compiler = str(candidate)
        if not compiler:
            raise RuntimeError('A host C11 compiler is required; no skipped checks')
        cls.temp = tempfile.TemporaryDirectory(prefix='nabo-voice-features-')
        dest = Path(cls.temp.name)/('features.dll' if os.name == 'nt' else 'features.so')
        subprocess.run([compiler, '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-shared', '-fPIC', str(HERE/'features.c'), '-o', str(dest)],
                       check=True, capture_output=True)
        cls.lib = C.CDLL(str(dest))
        cls.lib.vp_features_frame.argtypes = [C.POINTER(Workspace),
            C.POINTER(C.c_int16), C.POINTER(C.c_int16), C.POINTER(C.c_uint32)]

    @classmethod
    def tearDownClass(cls):
        if os.name == 'nt':
            import _ctypes
            _ctypes.FreeLibrary(cls.lib._handle)
        cls.temp.cleanup()

    def frame(self, pcm):
        ctx, out, level = Workspace(), (C.c_int16*12)(), C.c_uint32()
        self.lib.vp_features_frame(C.byref(ctx), (C.c_int16*320)(*pcm), out, C.byref(level))
        return list(out), level.value, ctx

    def test_silence_and_dc_are_not_speech(self):
        for level in (0, 12000, -16000, 32767, -32768):
            features, energy, _ = self.frame([level]*320)
            self.assertEqual(features, [0]*12)
            self.assertEqual(energy, 0)

    def test_fft_bin_locations_on_actual_pcm(self):
        for hz in (500,1500,3500,6000):
            _, level, ctx = self.frame(tone(hz))
            powers = [ctx.real[k]**2+ctx.imag[k]**2 for k in range(1,256)]
            peak = max(range(1,256), key=lambda k:powers[k-1])
            self.assertLessEqual(abs(peak-hz*512/16000), 1)
            self.assertGreater(level, 7000)

    def test_gain_and_dc_normalization(self):
        a,_,_ = self.frame(tone(1234,12000))
        b,_,_ = self.frame(tone(1234,3000,offset=6000))
        self.assertLessEqual(max(abs(x-y) for x,y in zip(a,b)), 8)

    def test_matches_independent_dft_reference_for_wideband_pcm(self):
        rng = random.Random(927)
        pcm = [rng.randint(-15000,15000) for _ in range(320)]
        actual,_,_ = self.frame(pcm)
        expected = reference(pcm)
        self.assertLessEqual(max(abs(a-b) for a,b in zip(actual,expected)), 12)

    def test_two_spectral_shapes_are_distinct(self):
        low,_,_ = self.frame(tone(500))
        high,_,_ = self.frame(tone(3500))
        self.assertGreater(sum(abs(a-b) for a,b in zip(low,high)), 400)

    def test_extreme_pcm_stays_bounded_and_repeatable(self):
        for pcm in ([32767,-32768]*160,
                    [32767]+[-32768]*319,
                    tone(50,32767), tone(7999,32767)):
            a,level,_ = self.frame(pcm)
            b,_,_ = self.frame(pcm)
            self.assertEqual(a,b)
            self.assertTrue(all(-32768<=x<=32767 for x in a))
            self.assertLessEqual(level,65535)

    def test_frontend_has_fixed_workspace_and_no_audio_history(self):
        self.assertEqual(C.sizeof(Workspace),4096)
        ctx = Workspace()
        out = (C.c_int16*12)()
        self.lib.vp_features_frame(C.byref(ctx),(C.c_int16*320)(*tone(500)),out,None)
        self.lib.vp_features_frame(C.byref(ctx),(C.c_int16*320)(),out,None)
        self.assertEqual(list(out),[0]*12)

    def test_generated_tables_are_reproducible(self):
        subprocess.run([os.sys.executable,str(HERE/'gen_tables.py'),'--check'],check=True)


if __name__ == '__main__':
    unittest.main()
