import ctypes as C
import json
import subprocess
import tempfile
import unittest
from tk_native import ROOT, Packet, build, unload

class HidMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.lib=build(cls.temp.name)
        script="""const {H}=require('./tests/tk_golden/model.js').load();
const specs=[];['prev','next','black','end','start'].forEach((k,i)=>specs.push([0,i,0,H.PPT[k]]));
H.MEET_APPS.forEach((a,i)=>['mute','cam','hand'].forEach((k,j)=>specs.push([1,i,j,a[k]])));
['up','down','ok','long_up','long_down','long_ok'].forEach((k,i)=>specs.push([2,i,0,H.MEDIA_KEYS[k]]));
H.MACRO_GROUPS.forEach((g,i)=>['up','ok','down'].forEach((k,j)=>specs.push([3,i,j,g[k]])));specs.push([4,0,0,H.SHUTTER]);
console.log(JSON.stringify({bindings:H.OS_LIST.flatMap((os,n)=>specs.map(([t,i,j,s])=>{const p=H.resolve(s,os);return {t,i,j,os:n,p,chord:H.chordLabel(p,os),bytes:p?H.reportBytes(p):[]}})),
 ascii:Array.from({length:128},(_,i)=>H.textPackets(String.fromCharCode(i))),names:Array.from({length:256},(_,i)=>H.keyName(i))}));"""
        cls.reference=json.loads(subprocess.check_output(['node','-e',script],cwd=ROOT))
    @classmethod
    def tearDownClass(cls):
        unload(cls.lib);cls.lib=None;cls.temp.cleanup()
    def test_c_export_matches_current_author_table(self):
        subprocess.run(['node','tools/export_hid_map.js','--check'],cwd=ROOT,check=True,capture_output=True)
    def test_all_168_default_bindings_chords_and_exact_reports_match_js(self):
        for row in self.reference['bindings']:
            p=self.lib.tk_host_binding(row['t'],row['i'],row['j'],row['os'])
            if row['p'] is None:self.assertFalse(p);continue
            self.assertTrue(p);q=p.contents
            actual={'kind':'key' if q.kind==1 else 'media','usage':q.usage}
            if q.kind==1:actual['mod']=q.mod
            self.assertEqual(actual,row['p'],row)
            label=C.create_string_buffer(192);self.lib.tk_hid_chord(p,row['os'],label,len(label));self.assertEqual(label.value.decode(),row['chord'])
            data=(C.c_uint8*8)();length=self.lib.tk_hid_report(p,data);self.assertEqual(list(data[:length]),row['bytes'])
    def test_ascii_expansion_and_all_usage_names_match_js(self):
        for i,expected in enumerate(self.reference['ascii']):
            p=Packet();ok=self.lib.tk_hid_char(i,C.byref(p))
            self.assertEqual(bool(expected),ok,i)
            if ok:self.assertEqual({'kind':'key','mod':p.mod,'usage':p.usage},expected[0],i)
        for i,expected in enumerate(self.reference['names']):
            label=C.create_string_buffer(32);self.lib.tk_hid_key_name(i,label,len(label));self.assertEqual(label.value.decode(),expected,i)
