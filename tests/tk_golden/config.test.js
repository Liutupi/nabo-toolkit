'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const {root}=require('./model.js');
function context() {
  const c=vm.createContext({TextEncoder,TextDecoder,Uint8Array,setTimeout,clearTimeout,atob,btoa});
  for(const file of ['tk_hid.js','tk_config_schema.js','tk_core.js','tk_config_serial.js'])vm.runInContext(fs.readFileSync(path.join(root,'game-art/toolkit/prototype',file),'utf8'),c);
  return c;
}
const plain=(x)=>JSON.parse(JSON.stringify(x));
test('schema defaults preserve author bindings and fit 4000 UTF-8 bytes',()=>{
  const c=context(),cfg=c.TKConfig.defaults();assert.ok(c.TKConfig.bytes(c.TKConfig.encode(cfg)).length<=4000);
  assert.deepEqual(plain(cfg.groups[1].up.mac),{mod:96,key:0});assert.equal(cfg.groups[3].ok.label,'播放 / 暂停');
  assert.deepEqual(plain(c.TKConfig.parse(c.TKConfig.encode(cfg))),plain(cfg));
});
test('shared schema rejects malformed, duplicate, overlong and non-ASCII text atomically',()=>{
  const c=context(),good=plain(c.TKConfig.defaults()),s=c.TK.create(0),before=JSON.stringify(s);
  const bad=structuredClone(good);bad.groups[0].ok={label:'Text',text:'中文'};assert.equal(c.TK.applyConfig(s,bad),false);assert.equal(JSON.stringify(s),before);
  for(const raw of ['{"v":1,"v":1}','{"v":1e0}','{"v":1.0}','{"v":01}','{"v":1,"x":"\\u0000"}'])assert.throws(()=>c.TKConfig.parse(raw));
  bad.groups[0].ok.text='a'.repeat(65);assert.throws(()=>c.TKConfig.validate(bad));
});
test('QR length is UTF-8 bytes, disabled family emits nothing, variable groups clamp',()=>{
  const c=context(),cfg=plain(c.TKConfig.defaults());cfg.groups=cfg.groups.slice(0,1);cfg.groups[0].up={label:'Empty',mac:null,win:null};cfg.cards=cfg.cards.slice(0,1);cfg.cards[0].qr='中'.repeat(53)+'x';
  const s=c.TK.create(0);s.page='macro';s.macro.group=5;s.card.idx=2;assert.equal(c.TK.applyConfig(s,cfg),true);assert.equal(s.macro.group,0);assert.equal(s.card.idx,0);assert.equal(c.TK.press(s,'up',1).length,0);
  cfg.cards[0].qr+='x';assert.throws(()=>c.TKConfig.validate(cfg));
});
test('protocol client rejects corrupt reads, device errors and missing acknowledgements',async()=>{
  const c=context();let client=new c.TKConfigSerial.Client(async(line)=>{if(line.endsWith('abort'))client.receive('tk.cfg.aborted');else{client.receive('noise');client.receive('tk.cfg.begin 1');client.receive('tk.cfg.data eA==');client.receive('tk.cfg.end 00000000');}},100);
  await assert.rejects(client.read(),/crc/);assert.equal(client.busy,false);
  client=new c.TKConfigSerial.Client(async()=>client.receive('tk.cfg.err storage'),100);await assert.rejects(client.read(),/storage/);
  client=new c.TKConfigSerial.Client(async()=>{},15);await assert.rejects(client.read(),/timeout/);assert.equal(client.closed,true);
});
test('client enforces a single operation and disconnect rejects pending read',async()=>{
  const c=context(),client=new c.TKConfigSerial.Client(async()=>{},100);const pending=client.read();await assert.rejects(client.read(),/busy/);client.disconnect();await assert.rejects(pending,/connection/);
});
test('write refuses invalid input before sending and rejects a mismatched readback',async()=>{
  const c=context(),old=c.TKConfig.defaults(),cfg=plain(old);cfg.groups[0].name='Custom';let calls=0,received=0,client;
  client=new c.TKConfigSerial.Client(async(line)=>{
    calls++;
    if(line.endsWith('abort'))client.receive('tk.cfg.aborted');
    else if(line.startsWith('>tk.cfg.begin ')){received=0;client.receive('tk.cfg.ready '+line.slice(14));}
    else if(line.startsWith('>tk.cfg.data ')){received+=atob(line.slice(13)).length;client.receive('tk.cfg.more '+received);}
    else if(line.startsWith('>tk.cfg.end '))client.receive('tk.cfg.ok '+received+' '+line.slice(12));
    else{
      const bytes=c.TKConfig.bytes(c.TKConfig.encode(old));client.receive('tk.cfg.begin '+bytes.length);
      for(let i=0;i<bytes.length;i+=48)client.receive('tk.cfg.data '+btoa(String.fromCharCode(...bytes.slice(i,i+48))));
      client.receive('tk.cfg.end '+c.TKConfig.crc32(bytes).toString(16).padStart(8,'0'));
    }
  },1000);
  assert.throws(()=>client.write({...cfg,v:2}));assert.equal(calls,0);await assert.rejects(client.write(cfg),/readback/);
});
test('real JavaScript client writes, persists and reads back through production C protocol',async(t)=>{
  const c=context(),child=spawn('python',[path.join(root,'tests/tk_config_stdio.py')],{cwd:root,stdio:['pipe','pipe','pipe']});
  let text='',errors='';child.stderr.on('data',(d)=>{errors+=d;});
  const client=new c.TKConfigSerial.Client((line)=>child.stdin.write(JSON.stringify({line})+'\n'),20000);
  child.stdout.on('data',(data)=>{text+=data;let i;while((i=text.indexOf('\n'))>=0){const row=JSON.parse(text.slice(0,i));text=text.slice(i+1);for(const line of row.lines)client.receive(line);}});
  child.on('error',(e)=>client.disconnect(e));child.on('exit',(code)=>{if(code)client.disconnect(new Error('C endpoint: '+errors));});
  t.after(()=>{child.stdin.end();client.disconnect();});
  const cfg=await client.read();assert.equal(cfg.groups.length,6);cfg.groups=cfg.groups.slice(0,1);cfg.cards=cfg.cards.slice(0,1);
  cfg.groups[0].name='自定义';cfg.groups[0].ok={label:'Text',text:'Hello!\n'};cfg.groups[0].up={label:'Right',mac:{mod:96,key:0},win:null};cfg.cards[0].qr='https://example.org/test';
  assert.deepEqual(plain(await client.write(cfg)),plain(c.TKConfig.validate(cfg)));assert.deepEqual(plain(await client.read()),plain(c.TKConfig.validate(cfg)));
});
