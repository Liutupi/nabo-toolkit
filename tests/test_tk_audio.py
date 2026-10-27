import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import wave
from tk_native import ROOT,unload

class Mix(C.Structure):
    _fields_=[('pcm',C.c_void_p),('frames',C.c_size_t),('position',C.c_size_t),('phase',C.c_uint32),('step',C.c_uint32),('tone_left',C.c_uint),('tone_total',C.c_uint)]
class AudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();p=Path(cls.temp.name)/'audio.so'
        subprocess.run(['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-std=c11','-I',str(ROOT/'firmware/main'),str(ROOT/'firmware/main/tk_audio_mix.c'),'-o',str(p)],check=True,capture_output=True)
        cls.lib=C.CDLL(str(p));l=cls.lib
        l.tk_audio_mix_init.argtypes=[C.POINTER(Mix),C.c_void_p,C.c_size_t];l.tk_audio_mix_voice.argtypes=[C.POINTER(Mix),C.c_bool]
        l.tk_audio_mix_tone.argtypes=[C.POINTER(Mix),C.c_uint,C.c_uint];l.tk_audio_mix_fill.argtypes=[C.POINTER(Mix),C.POINTER(C.c_int16),C.c_size_t];l.tk_audio_mix_fill.restype=C.c_bool
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.temp.cleanup()
    def test_real_pcm_exact_playback_tail_silence_cancel_and_replay(self):
        data=(ROOT/'firmware/assets/boot-welcome.pcm').read_bytes();m=Mix();self.lib.tk_audio_mix_init(C.byref(m),data,len(data));out=(C.c_int16*320)()
        self.assertFalse(self.lib.tk_audio_mix_fill(C.byref(m),out,320));self.lib.tk_audio_mix_voice(C.byref(m),True);result=bytearray()
        while self.lib.tk_audio_mix_fill(C.byref(m),out,320):result.extend(bytes(out))
        self.assertEqual(result[:len(data)],data);self.assertFalse(any(result[len(data):]));self.assertFalse(any(out))
        self.lib.tk_audio_mix_voice(C.byref(m),True);self.lib.tk_audio_mix_fill(C.byref(m),out,320);self.assertEqual(bytes(out),data[:640])
        self.lib.tk_audio_mix_voice(C.byref(m),False);self.assertFalse(self.lib.tk_audio_mix_fill(C.byref(m),out,320));self.assertFalse(any(out))
    def test_voice_ducks_tone_to_quarter_and_saturates_safely(self):
        pcm=(C.c_int16*320)(*[10000]*320);voice=Mix();tone=Mix();empty=(C.c_int16*320)();mixed=(C.c_int16*320)()
        self.lib.tk_audio_mix_init(C.byref(voice),pcm,640);self.lib.tk_audio_mix_voice(C.byref(voice),True);self.lib.tk_audio_mix_tone(C.byref(voice),880,20)
        self.lib.tk_audio_mix_init(C.byref(tone),None,0);self.lib.tk_audio_mix_tone(C.byref(tone),880,20)
        self.lib.tk_audio_mix_fill(C.byref(voice),mixed,320);self.lib.tk_audio_mix_fill(C.byref(tone),empty,320)
        for a,b in zip(mixed,empty):self.assertEqual(a,10000+int(b/4))
        loud=(C.c_int16*320)(*[32760]*320);self.lib.tk_audio_mix_init(C.byref(voice),loud,640);self.lib.tk_audio_mix_voice(C.byref(voice),True);self.lib.tk_audio_mix_tone(C.byref(voice),880,20)
        self.lib.tk_audio_mix_fill(C.byref(voice),mixed,320);self.assertTrue(any(x==32767 for x in mixed));self.assertTrue(all(x>=0 for x in mixed))
    def test_welcome_source_hash_format_duration_and_no_clipping(self):
        m=json.loads((ROOT/'game-art/toolkit/audio/generation.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256((ROOT/m['source']).read_bytes()).hexdigest(),m['source_sha256'])
        with wave.open(str(ROOT/'game-art/toolkit/audio/boot-welcome.wav')) as w:
            self.assertEqual((w.getnchannels(),w.getsampwidth(),w.getframerate()),(1,2,16000));self.assertAlmostEqual(w.getnframes()/16000,2.65)
            data=w.readframes(w.getnframes());self.assertEqual(data,(ROOT/'firmware/assets/boot-welcome.pcm').read_bytes())
        self.assertEqual(m['clipped_samples'],0);self.assertTrue(m['audible_acceptance'].startswith('PASS'))
    def test_tone_zero_endpoints_and_five_ms_envelope_remove_abrupt_step(self):
        for ms in [1,5,40,100]:
            m=Mix();self.lib.tk_audio_mix_init(C.byref(m),None,0);self.lib.tk_audio_mix_tone(C.byref(m),880,ms)
            out=(C.c_int16*(ms*16))();self.assertTrue(self.lib.tk_audio_mix_fill(C.byref(m),out,len(out)))
            self.assertEqual(out[0],0);self.assertEqual(out[-1],0)
            self.assertLess(max(abs(out[i+1]-out[i]) for i in range(len(out)-1)),600)
            self.assertFalse(self.lib.tk_audio_mix_fill(C.byref(m),out,len(out)));self.assertFalse(any(out))
