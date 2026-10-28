"""ctypes ABI + JSON projection; no rules or state transitions are implemented here."""
import ctypes as C
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OS=['mac','win','ios','android']
PAGES=['boot','menu','macro','ppt','meet','media','cam','card','conn','set']
KEYS=['up','down','ok','long_up','long_down','long_ok']
class Slot(C.Structure):
    _fields_=[('used',C.c_bool),('name',C.c_char*96),('os',C.c_int)]
class Card(C.Structure):
    _fields_=[('title',C.c_char*48),('name',C.c_char*96),('line',C.c_char*192),('qr',C.c_char*512)]
class CustomSlot(C.Structure):
    _fields_=[('label',C.c_char*33),('text',C.c_char*65),('media',C.c_uint16),('key',C.c_uint16*2),('kind',C.c_uint8),('mask',C.c_uint8),('mod',C.c_uint8*2)]
class CustomGroup(C.Structure):_fields_=[('name',C.c_char*33),('slots',CustomSlot*3)]
class Custom(C.Structure):_fields_=[('group_count',C.c_int),('card_count',C.c_int),('groups',CustomGroup*6),('cards',Card*3)]
class Packet(C.Structure):
    _fields_=[('kind',C.c_int),('mod',C.c_int),('usage',C.c_int),('text',C.c_char_p)]
class Effect(C.Structure):
    _fields_=[(k,C.c_int) for k in ['type','kind','mod','usage','frequency','ms']]+[('bytes',C.c_uint8*8),('length',C.c_int),('label',C.c_char*192)]
class Effects(C.Structure):
    _fields_=[('count',C.c_int),('overflow',C.c_bool),('items',Effect*128)]
class State(C.Structure):
    _fields_=[('page',C.c_int),('menu',C.c_int),('last_input',C.c_int64),('boot_start',C.c_int64),('boot_voiced',C.c_bool),
              ('slots',Slot*3),('bind_order',C.c_int*3),('bind_count',C.c_int),('active',C.c_int),('connected',C.c_bool),
              ('pairing',C.c_bool),('pair_until',C.c_int64),('passkey_valid',C.c_bool),('passkey',C.c_uint32),
              ('conn_sel',C.c_int),('confirm_del',C.c_int),('os_pick',C.c_bool),('os_slot',C.c_int),('os_sel',C.c_int),
              ('beep',C.c_bool),('voice',C.c_bool),('talk',C.c_int),('sleep',C.c_int),('set_sel',C.c_int),
              ('ppt_running',C.c_bool),('ppt_start',C.c_int64),('ppt_acc',C.c_int64),('ppt_pages',C.c_int),('ppt_black',C.c_bool),
              ('meet_app',C.c_int),('cam_delay',C.c_int),('cam_end',C.c_int64),('cam_last_sec',C.c_int),('burst_left',C.c_int),
              ('next_shot',C.c_int64),('shots',C.c_int),('macro_group',C.c_int),('card_idx',C.c_int),('card_zoom',C.c_bool),
              ('cards',Card*3),('card_count',C.c_int),('toast',C.c_bool),('toast_text',C.c_char*256),('toast_error',C.c_bool),
              ('toast_until',C.c_int64),('react',C.c_bool),('react_key',C.c_int),('react_until',C.c_int64),
              ('hit',C.c_bool),('hit_key',C.c_int),('hit_until',C.c_int64),('config',C.POINTER(Custom)),
              ('remote_dim',C.c_bool),('screen_off',C.c_bool),('screen_since',C.c_int64),
              ('media_mode',C.c_int),('media_select',C.c_bool)]

def build(folder, source=None):
    source=source or ROOT/'firmware/main'
    dest=Path(folder)/'model.so'
    subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror','-std=c11','-I',str(source),
                    *[str(source/n) for n in ['tk_model.c','tk_model_config.c','tk_model_tools.c','tk_model_connection.c','tk_hid_map.c']],
                    str(ROOT/'tests/tk_model_host.c'),'-o',str(dest)],check=True,capture_output=True,encoding='utf-8',errors='replace')
    lib=C.CDLL(str(dest))
    lib.tk_host_state_size.restype=C.c_size_t;lib.tk_host_effects_size.restype=C.c_size_t
    assert lib.tk_host_state_size()==C.sizeof(State)
    assert lib.tk_host_effects_size()==C.sizeof(Effects)
    lib.tk_host_demo.argtypes=[C.POINTER(State),C.c_int]
    lib.tk_model_init.argtypes=[C.POINTER(State),C.c_int64]
    lib.tk_model_press.argtypes=[C.POINTER(State),C.c_int,C.c_int64,C.POINTER(Effects)]
    lib.tk_model_tick.argtypes=[C.POINTER(State),C.c_int64,C.POINTER(Effects)]
    lib.tk_model_event.argtypes=[C.POINTER(State),C.c_char_p,C.c_int64,C.c_char_p]
    lib.tk_model_apply_config.argtypes=[C.POINTER(State),C.POINTER(Custom)]
    lib.tk_model_sleep_due.argtypes=[C.POINTER(State),C.c_int64];lib.tk_model_sleep_due.restype=C.c_bool
    lib.tk_model_screen_reset.argtypes=[C.POINTER(State),C.c_int64]
    lib.tk_host_binding.argtypes=[C.c_int]*4;lib.tk_host_binding.restype=C.POINTER(Packet)
    lib.tk_hid_chord.argtypes=[C.POINTER(Packet),C.c_int,C.c_char_p,C.c_size_t]
    lib.tk_hid_key_name.argtypes=[C.c_uint,C.c_char_p,C.c_size_t]
    lib.tk_hid_char.argtypes=[C.c_ubyte,C.POINTER(Packet)];lib.tk_hid_char.restype=C.c_bool
    lib.tk_hid_report.argtypes=[C.POINTER(Packet),C.POINTER(C.c_uint8)];lib.tk_hid_report.restype=C.c_uint
    return lib

def unload(lib):
    if sys.platform=='win32':
        import _ctypes
        _ctypes.FreeLibrary(lib._handle)

def snapshot(s):
    return dict(page=PAGES[s.page],menu=s.menu,lastInput=s.last_input,boot=dict(start=s.boot_start,voiced=s.boot_voiced),
                slots=[dict(name=x.name.decode(),os=OS[x.os]) if x.used else None for x in s.slots],
                bindOrder=list(s.bind_order[:s.bind_count]),active=s.active,connected=s.connected,
                pairing=dict(until=s.pair_until,passkey=f'{s.passkey:06d}' if s.passkey_valid else None) if s.pairing else None,
                connSel=s.conn_sel,confirmDel=s.confirm_del,osPick=dict(slot=s.os_slot,sel=s.os_sel) if s.os_pick else None,
                settings=dict(beep=s.beep,voice=s.voice,talk=s.talk,sleep=s.sleep,remoteDim=s.remote_dim),setSel=s.set_sel,
                ppt=dict(running=s.ppt_running,startMs=s.ppt_start,accMs=s.ppt_acc,pages=s.ppt_pages,black=s.ppt_black),
                meet=dict(app=s.meet_app),media=dict(mode=s.media_mode,choosing=s.media_select),
                display=dict(off=s.screen_off,since=s.screen_since),cam=dict(delay=s.cam_delay,endMs=s.cam_end,lastSec=s.cam_last_sec,
                    burstLeft=s.burst_left,nextShot=s.next_shot,shots=s.shots),macro=dict(group=s.macro_group),groups=None,
                card=dict(idx=s.card_idx,zoom=s.card_zoom),cards=[{k:getattr(c,k).decode() for k in ['title','name','line','qr']} for c in s.cards[:s.card_count]],
                toast=dict(text=s.toast_text.decode(),kind='err' if s.toast_error else 'ok',until=s.toast_until) if s.toast else None,
                react=dict(until=s.react_until,key=KEYS[s.react_key]) if s.react else None,
                hit=dict(key=KEYS[s.hit_key],until=s.hit_until) if s.hit else None) | {'groups':custom_groups(s.config.contents) if s.config else None}

def custom_groups(c):
    def slot(s):
        o={'label':s.label.decode()}
        if s.kind==2:return o|{'media':s.media}
        if s.kind==3:return o|{'text':s.text.decode()}
        return o|{family:dict(mod=s.mod[i],key=s.key[i]) if s.mask&(1<<i) else None for i,family in enumerate(['mac','win'])}
    return [dict(name=g.name.decode(),**{k:slot(g.slots[i]) for i,k in enumerate(['up','ok','down'])}) for g in c.groups[:c.group_count]]

def configure(lib,s,data):
    c=Custom();c.group_count=len(data['groups']);c.card_count=len(data['cards'])
    for index,group in enumerate(data['groups']):
        c.groups[index].name=group['name'].encode()
        for k,name in enumerate(['up','ok','down']):
            src=group[name];slot=c.groups[index].slots[k];slot.label=src['label'].encode()
            if 'text' in src:slot.kind=3;slot.text=src['text'].encode()
            elif 'media' in src:slot.kind=2;slot.media=src['media']
            else:
                slot.kind=1
                for i,family in enumerate(['mac','win']):
                    if src.get(family) is not None:slot.mask|=1<<i;slot.mod[i]=src[family]['mod'];slot.key[i]=src[family]['key']
    for index,card in enumerate(data['cards']):
        for key in ['title','name','line','qr']:setattr(c.cards[index],key,card[key].encode())
    s._config_keepalive=c;lib.tk_model_apply_config(C.byref(s),C.byref(c));return c

def outputs(out):
    assert not out.overflow
    result=[]
    for e in out.items[:out.count]:
        if e.type==1:
            item=dict(t='hid',kind='key' if e.kind==1 else 'media',usage=e.usage,bytes=list(e.bytes[:e.length]),label=e.label.decode())
            if e.kind==1:item['mod']=e.mod
        elif e.type==2:item=dict(t='beep',f=e.frequency,ms=e.ms)
        else:
            assert e.type==3
            item=dict(t='voice',id='boot-welcome',text='那波，陪你遥控万物！')
        result.append(item)
    return result

def first_diff(a,b,path=''):
    if type(a)!=type(b):return f'{path}: type/value {a!r} != {b!r}'
    if isinstance(a,dict):
        if a.keys()!=b.keys():return f'{path}: keys {a.keys()} != {b.keys()}'
        for k in a:
            diff=first_diff(a[k],b[k],path+'.'+k)
            if diff:return diff
    elif isinstance(a,list):
        if len(a)!=len(b):return f'{path}: lengths {len(a)} != {len(b)}'
        for i,(x,y) in enumerate(zip(a,b)):
            diff=first_diff(x,y,f'{path}[{i}]')
            if diff:return diff
    elif a!=b:return f'{path}: {a!r} != {b!r}'
    return None

def replay(lib,rows):
    s=State();out=Effects()
    for row in rows:
        call=row['call'];now=row['now'];kind=call['type'];out.count=0;out.overflow=False
        if kind=='init':lib.tk_host_demo(C.byref(s),OS.index(call['os']))
        elif kind=='press':lib.tk_model_press(C.byref(s),KEYS.index(call['key']),now,C.byref(out))
        elif kind=='tick':lib.tk_model_tick(C.byref(s),now,C.byref(out))
        elif kind=='config':configure(lib,s,call['config'])
        else:
            arg=call.get('arg')
            if call['event']=='passkey' and type(arg)==int and 0<=arg<=999999:arg=f'{arg:06d}'
            lib.tk_model_event(C.byref(s),call['event'].encode(),now,str(arg).encode() if arg is not None else None)
        actual=dict(state=snapshot(s),outputs=outputs(out),sleepDue=lib.tk_model_sleep_due(C.byref(s),now))
        expected={k:row[k] for k in actual}
        diff=first_diff(actual,expected)
        if diff:return f"{row['scenario']} step{row['step']} at{now}: {diff}"
    return None
