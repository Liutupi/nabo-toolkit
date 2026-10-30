import base64
import copy
import ctypes as C
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zlib
from tk_native import ROOT,Custom,State,Effects,unload

def example():
    return {'v':1,'groups':[{'name':'Custom','up':{'label':'Right','mac':{'mod':96,'key':0},'win':None},
        'ok':{'label':'Text','text':'Hello!\n'},'down':{'label':'Media','media':233}}],
        'cards':[{'title':'Card','name':'TEST','line':'Synthetic data','qr':'https://example.org/nabo'}]}

class ConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();main=ROOT/'firmware/main';third=ROOT/'firmware/managed_components/espressif__cjson/cJSON'
        if not (third/'cJSON.c').exists():raise RuntimeError('Run ESP-IDF reconfigure to fetch pinned cJSON before config tests')
        sources=['tk_model.c','tk_model_config.c','tk_model_tools.c','tk_model_connection.c','tk_hid_map.c','tk_config_lex.c','tk_config_parse.c','tk_config_json.c','tk_config_store.c','tk_config_serial.c']
        p=Path(cls.temp.name)/'config.so'
        run=subprocess.run(['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-std=c11','-DCJSON_HIDE_SYMBOLS','-I',str(main),'-I',str(ROOT/'tests/support'),'-I',str(third),
            *[str(main/n) for n in sources],str(third/'cJSON.c'),str(ROOT/'tests/tk_store_mock.c'),str(ROOT/'tests/tk_config_host.c'),'-o',str(p)],capture_output=True,encoding='utf-8',errors='replace')
        if run.returncode:raise RuntimeError(run.stderr)
        cls.lib=C.CDLL(str(p));lib=cls.lib
        lib.tk_cfg_host_new.restype=C.c_void_p
        for name in ['free','clear','error','json','lines','state']:getattr(lib,'tk_cfg_host_'+name).argtypes=[C.c_void_p]
        for name in ['json','lines']:getattr(lib,'tk_cfg_host_'+name).restype=C.c_char_p
        lib.tk_cfg_host_state.restype=C.POINTER(State)
        lib.tk_cfg_host_line.argtypes=[C.c_void_p,C.c_char_p,C.c_int64,C.c_bool];lib.tk_cfg_host_tick.argtypes=[C.c_void_p,C.c_int64,C.c_bool]
        lib.tk_config_parse.argtypes=[C.POINTER(Custom),C.c_char_p,C.c_size_t];lib.tk_config_parse.restype=C.c_char_p
        lib.tk_config_json.argtypes=[C.POINTER(Custom),C.c_char_p,C.c_size_t];lib.tk_config_json.restype=C.c_size_t
        lib.tk_mock_blob.argtypes=[C.c_char_p,C.c_void_p,C.c_uint];lib.tk_mock_dump.argtypes=[C.c_char_p,C.c_void_p];lib.tk_mock_dump.restype=C.c_uint
        lib.tk_model_press.argtypes=[C.POINTER(State),C.c_int,C.c_int64,C.POINTER(Effects)]
        assert lib.tk_cfg_host_custom_size()==C.sizeof(Custom)
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'lib'):unload(cls.lib);cls.lib=None
        if hasattr(cls,'temp'):cls.temp.cleanup()
    def setUp(self):self.lib.tk_mock_reset();self.h=self.lib.tk_cfg_host_new();self.assertTrue(self.h);self.now=0
    def tearDown(self):self.lib.tk_cfg_host_free(self.h)
    def lines(self):
        value=self.lib.tk_cfg_host_lines(self.h).decode().splitlines();self.lib.tk_cfg_host_clear(self.h);return value
    def line(self,s,writable=True):self.now+=10;self.lib.tk_cfg_host_line(self.h,s.encode(),self.now,writable);return self.lines()
    def current(self):return json.loads(self.lib.tk_cfg_host_json(self.h))
    def stored(self):
        b=(C.c_ubyte*4016)();n=self.lib.tk_mock_dump(b'cfg_v1',b);return bytes(b[:n])
    def upload(self,c,crc=None):
        data=c if isinstance(c,bytes) else json.dumps(c,ensure_ascii=False,separators=(',',':')).encode()
        self.assertEqual(self.line(f'>tk.cfg.begin {len(data)}'),[f'tk.cfg.ready {len(data)}'])
        for i in range(0,len(data),48):self.assertEqual(self.line('>tk.cfg.data '+base64.b64encode(data[i:i+48]).decode()),[f'tk.cfg.more {min(i+48,len(data))}'])
        return self.line(f'>tk.cfg.end {zlib.crc32(data) if crc is None else crc:08x}')
    def test_defaults_match_author_and_full_write_read_reboot_model_effects(self):
        self.assertEqual(self.lib.tk_cfg_host_error(self.h),0);self.assertEqual(len(self.current()['groups']),6)
        self.assertEqual(next(g for g in self.current()['groups'] if g['name']=='Typeless')['up']['mac'],{'mod':96,'key':0})
        self.assertEqual(next(g for g in self.current()['groups'] if g['name']=='AI助手')['up']['mac'],{'mod':0,'key':0x68})
        c=example();self.assertTrue(self.upload(c)[0].startswith('tk.cfg.ok '));self.assertEqual(self.current(),c)
        self.assertEqual(self.line('>tk.cfg.read'),[f"tk.cfg.begin {len(self.lib.tk_cfg_host_json(self.h))}"])
        for _ in range(100):self.now+=16;self.lib.tk_cfg_host_tick(self.h,self.now,True)
        output=self.lines();raw=b''.join(base64.b64decode(x[12:]) for x in output if x.startswith('tk.cfg.data '))
        self.assertEqual(json.loads(raw),c);self.assertEqual(output[-1],f'tk.cfg.end {zlib.crc32(raw):08x}')
        self.lib.tk_cfg_host_free(self.h);self.h=self.lib.tk_cfg_host_new();self.assertEqual(self.current(),c)
        state=self.lib.tk_cfg_host_state(self.h);state.contents.page=2;state.contents.connected=True;state.contents.slots[0].used=True
        out=Effects();self.lib.tk_model_press(state,0,10000,C.byref(out));self.assertEqual(list(out.items[0].bytes),[96,0,0,0,0,0,0,0])
        self.lib.tk_model_press(state,2,10010,C.byref(out));self.assertEqual(out.count,7)
        state.contents.slots[0].os=1;self.lib.tk_model_press(state,0,10020,C.byref(out));self.assertEqual(out.count,0)
    def test_crc_json_and_schema_failures_leave_live_and_stored_configuration(self):
        self.upload(example());before=self.current();stored=self.stored()
        cases=[(b'{broken',None),(json.dumps(example()).encode(),0)]
        for field,value in [('text','中文'),('text','x'*65)]:
            c=example();c['groups'][0]['ok'][field]=value;cases.append((json.dumps(c).encode(),None))
        for data,crc in cases:
            with self.subTest(data=data[:20]):self.assertTrue(self.upload(data,crc)[0].startswith('tk.cfg.err '));self.assertEqual(self.current(),before);self.assertEqual(self.stored(),stored)
    def test_fragment_timeout_abort_bad_base64_size_and_test_mode(self):
        before=self.current();self.assertEqual(self.line('>tk.cfg.begin 4001'),['tk.cfg.err size'])
        self.line('>tk.cfg.begin 4');self.assertEqual(self.line('>tk.cfg.data Zh=='),['tk.cfg.err data'])
        self.line('>tk.cfg.begin 4');self.now+=10000;self.lib.tk_cfg_host_tick(self.h,self.now,True);self.assertEqual(self.lines(),['tk.cfg.err timeout'])
        self.line('>tk.cfg.begin 4');self.assertEqual(self.line('>tk.cfg.abort'),['tk.cfg.aborted'])
        self.assertEqual(self.line('>tk.cfg.begin 4',False),['tk.cfg.err test']);self.assertEqual(self.current(),before);self.assertEqual(self.stored(),b'')
    def test_storage_failures_do_not_apply_or_overwrite_previous_config(self):
        self.upload(example());before=self.current();old=self.stored();changed=example();changed['groups'][0]['name']='Changed'
        for fault in (1,2):
            self.lib.tk_mock_fail(fault);self.assertEqual(self.upload(changed),['tk.cfg.err storage']);self.assertEqual(self.current(),before);self.assertEqual(self.stored(),old)
    def test_capacity_precheck_preserves_live_and_stored_configuration(self):
        self.upload(example());before=self.current();old=self.stored();changed=example();changed['groups'][0]['name']='Changed'
        self.lib.tk_mock_capacity(630,629)
        self.assertEqual(self.upload(changed),['tk.cfg.err storage'])
        self.assertEqual(self.current(),before);self.assertEqual(self.stored(),old)
    def test_corrupted_persisted_record_is_preserved_and_not_applied(self):
        self.upload(example());data=bytearray(self.stored());data[-1]^=1;b=(C.c_ubyte*len(data)).from_buffer_copy(data);self.lib.tk_mock_blob(b'cfg_v1',b,len(data))
        self.lib.tk_cfg_host_free(self.h);self.h=self.lib.tk_cfg_host_new();self.assertNotEqual(self.lib.tk_cfg_host_error(self.h),0)
        self.assertEqual(len(self.current()['groups']),6);self.assertEqual(self.stored(),data)
    def test_six_group_legacy_config_survives_save_reload_without_implicit_migration(self):
        legacy=example();source=legacy['groups'][0]
        legacy['groups']=[dict(copy.deepcopy(source),name='抖音' if i==5 else f'Legacy{i}') for i in range(6)]
        self.assertTrue(self.upload(legacy)[0].startswith('tk.cfg.ok '));stored=self.stored()
        self.assertEqual(self.current(),legacy)
        self.lib.tk_cfg_host_free(self.h);self.h=self.lib.tk_cfg_host_new()
        self.assertEqual(self.lib.tk_cfg_host_error(self.h),0)
        self.assertEqual(self.current(),legacy);self.assertEqual(self.stored(),stored)
    def test_limits_unicode_duplicate_keys_and_numeric_spellings(self):
        good=example();good['groups'][0]['ok']['text']='x'*64;good['cards'][0]['qr']='中'*53+'x';self.assertTrue(self.upload(good)[0].startswith('tk.cfg.ok '))
        before=self.current();old=self.stored()
        raws=[b'{"v":1,"v":1,"groups":[],"cards":[]}',json.dumps(example()).replace('"v": 1','"v": 1.0').encode(),b'\xff',b'{"v":01}',b'{"v":1e0}']
        for transform in [lambda c:c.update(v=2),lambda c:c.update(groups=[]),lambda c:c.update(cards=[]),lambda c:c['cards'][0].update(qr='中'*54),lambda c:c['groups'][0]['up']['mac'].update(mod=256),lambda c:c['groups'][0]['up']['mac'].update(key=116),lambda c:c['groups'][0]['ok'].update(text='a\t'),lambda c:c['groups'][0].update(name='123456789')]:
            c=example();transform(c);raws.append(json.dumps(c,ensure_ascii=False).encode())
        for data in raws:
            with self.subTest(raw=data[:25]):self.assertTrue(self.upload(data)[0].startswith('tk.cfg.err '));self.assertEqual(self.current(),before);self.assertEqual(self.stored(),old)
    def test_web_and_c_schema_agree_on_shared_valid_invalid_corpus(self):
        good=example();cases=[good,dict(good,v=2),dict(good,groups=[]),dict(good,cards=[])]
        for text in ['', 'x'*64, '\n'*64, 'x'*65, '中文', '\t', '\r', '\x00']:
            c=example();c['groups'][0]['ok']['text']=text;cases.append(c)
        for qr in ['中'*53+'x','中'*54,'','https://example.org/😀']:
            c=example();c['cards'][0]['qr']=qr;cases.append(c)
        c=example();c['groups'][0]['up']={'label':'Empty'};cases.append(c)
        raws=[json.dumps(c,ensure_ascii=False,separators=(',',':')) for c in cases]
        raws+=['{"v":1,"v":1}',raws[0].replace('"v":1','"v":1.0'),raws[0].replace('"v":1','"v":1e0'),'\ufeff'+raws[0],raws[0]+' ',raws[0]+'null']
        source="const fs=require('fs'),vm=require('vm');let c=vm.createContext({TextEncoder});vm.runInContext(fs.readFileSync('game-art/toolkit/prototype/tk_config_schema.js','utf8'),c);console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(s=>{try{return c.TKConfig.parse(s)}catch(_){return null}})));"
        expected=json.loads(subprocess.check_output(['node','-e',source],input=json.dumps(raws).encode(),cwd=ROOT))
        for raw,reference in zip(raws,expected):
            with self.subTest(raw=raw[:30]):
                value=Custom();C.memset(C.byref(value),0x5a,C.sizeof(value));before=bytes(value);data=raw.encode();error=self.lib.tk_config_parse(C.byref(value),data,len(data))
                self.assertEqual(error is None,reference is not None)
                if error:self.assertEqual(bytes(value),before)
                else:
                    out=C.create_string_buffer(4001);self.assertGreater(self.lib.tk_config_json(C.byref(value),out,4001),0);self.assertEqual(json.loads(out.value),reference)
    def test_exact_transport_budget_truncation_overlap_and_invalid_utf8_preserve_current(self):
        data=json.dumps(example(),separators=(',',':')).encode();padded=data+b' '*(4000-len(data));self.assertTrue(self.upload(padded)[0].startswith('tk.cfg.ok '));before=self.current();stored=self.stored()
        for payload in [b'\xed\xa0\x80',b'\xc0\x80',b'\xf4\x90\x80\x80']:
            self.assertTrue(self.upload(payload)[0].startswith('tk.cfg.err '))
        self.line('>tk.cfg.begin 10');self.assertEqual(self.line('>tk.cfg.end 00000000'),['tk.cfg.err crc'])
        self.line('>tk.cfg.begin 10');self.assertEqual(self.line('>tk.cfg.begin 10'),['tk.cfg.err busy'])
        self.line('>tk.cfg.begin 10');self.assertEqual(self.line('>tk.cfg.invalid'),['tk.cfg.err line'])
        self.assertEqual(self.current(),before);self.assertEqual(self.stored(),stored)
