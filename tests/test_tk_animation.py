import ctypes as C
import hashlib
import json
from pathlib import Path
import random
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from tk_native import ROOT,unload
sys.path.insert(0,str(ROOT/'tools'))
from toolkit_sprite_codec import decode
from build_toolkit_runtime import NAMES,unlz

class AnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();p=Path(cls.temp.name)/'anim.so'
        subprocess.run(['cc','-shared','-fPIC','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT/'firmware/main'),str(ROOT/'firmware/main/tk_animation.c'),str(ROOT/'tests/tk_animation_host.c'),'-o',str(p)],check=True,capture_output=True)
        cls.lib=C.CDLL(str(p));l=cls.lib;l.tk_anim_new.restype=C.c_void_p;l.tk_anim_free.argtypes=[C.c_void_p]
        l.tk_anim_frame.argtypes=[C.c_void_p,C.c_void_p,C.c_size_t,C.c_uint,C.c_uint64];l.tk_anim_frame.restype=C.c_bool
        l.tk_anim_pixels.argtypes=[C.c_void_p];l.tk_anim_pixels.restype=C.c_void_p
        cls.blob=(ROOT/'firmware/assets/animations.bin').read_bytes()
    @classmethod
    def tearDownClass(cls):unload(cls.lib);cls.temp.cleanup()
    def test_all_original_indexed_pixels_frames_timestamps_seeks_and_loops(self):
        a=self.lib.tk_anim_new();calls=[]
        try:
            for id,name in enumerate(NAMES):
                d=decode((ROOT/f'game-art/toolkit/sprites/bin/{name}.tks').read_bytes())
                for frame,t in enumerate(d['times']):calls.append((id,t,frame,d))
                if d['loop']:calls.append((id,d['duration'],0,d))
                else:calls.append((id,100000,len(d['frames'])-1,d))
            for order in [calls,list(reversed(calls)),random.Random(4).sample(calls,len(calls))]:
                for id,t,frame,d in order:
                    self.assertTrue(self.lib.tk_anim_frame(a,self.blob,len(self.blob),id,t),(id,t))
                    self.assertEqual(C.string_at(self.lib.tk_anim_pixels(a),d['w']*d['h']),d['frames'][frame])
            self.assertLessEqual(self.lib.tk_anim_memory(),22000)
        finally:self.lib.tk_anim_free(a)
    def test_corrupt_headers_index_payload_crc_truncation_and_failed_frame_recovery(self):
        first=struct.unpack_from('<I',self.blob,16)[0];entry=first+152;payload=first+struct.unpack_from('<I',self.blob,entry+4)[0]
        mutants=[]
        for offset in [0,8,12,16,first,first+8,first+12,entry,entry+4,entry+8,entry+12,entry+16,payload]:
            b=bytearray(self.blob);b[offset]^=128;mutants.append(bytes(b))
        mutants += [self.blob[:n] for n in [0,79,100,len(self.blob)-1]]
        for bad in mutants:
            a=self.lib.tk_anim_new()
            try:
                self.assertFalse(self.lib.tk_anim_frame(a,bad,len(bad),0,0))
                self.assertTrue(self.lib.tk_anim_frame(a,self.blob,len(self.blob),0,0))
            finally:self.lib.tk_anim_free(a)
    def test_runtime_provenance_and_compact_font_descriptors_are_lossless(self):
        m=json.loads((ROOT/'firmware/assets/runtime.json').read_text());self.assertEqual(hashlib.sha256(self.blob).hexdigest(),m['sha256'])
        old=(ROOT/'firmware/fonts/tk_font_cjk.c').read_text(encoding='utf-8');new=(ROOT/'firmware/fonts/tk_font_cjk_compact.c').read_text(encoding='utf-8')
        bitmap=lambda text:re.search(r'static .*?glyph_bitmap\[\] = \{(.*?)\n\};',text,re.S)[1]
        self.assertEqual(bitmap(old),bitmap(new))
        raw=bytes(map(int,re.findall(r'\d+',re.search(r'compact_glyphs\[\] = \{(.*?)\n\};',new,re.S)[1])))
        rows=re.findall(r'\{([^{}]+)\}',re.search(r'glyph_dsc\[\] = \{(.*?)\n\};',old,re.S)[1]);self.assertEqual(len(raw),len(rows)*9)
        for i,row in enumerate(rows):
            wanted=[int(re.search(r'\.'+f+r'\s*=\s*(-?\d+)',row)[1]) for f in ['bitmap_index','adv_w','box_w','box_h','ofs_x','ofs_y']]
            p=raw[i*9:(i+1)*9];self.assertEqual([int.from_bytes(p[:3],'little'),*struct.unpack('<HBBbb',p[3:])],wanted)
        self.assertGreater(m['font']['original_descriptor_bytes']-m['font']['compact_descriptor_bytes'],140000)
