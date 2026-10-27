'use strict';
const test=require('node:test'), assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {load,plain,root}=require('./model.js');
const {T,H,B}=load();
const hid=(out)=>out.filter((p)=>p.t==='hid');
function menu() {const st=T.create(0);T.press(st,'ok',0);return st;}
function pairing() {const st=menu();st.page='conn';st.connSel=3;T.press(st,'ok',10);return st;}

test('welcome plays fully at 5.5s, voice fires once at 1.4s',()=>{
  const st=T.create(0);
  assert.equal(T.tick(st,1399).length,0);
  assert.equal(T.tick(st,1400).filter((x)=>x.t==='voice').length,1);
  assert.equal(T.tick(st,1500).length,0);
  T.tick(st,5499);assert.equal(st.page,'boot');T.tick(st,5500);assert.equal(st.page,'menu');
});
test('every boot key skips without sending HID',()=>{
  for (const key of ['up','down','ok','long_up','long_down','long_ok']) {
    const st=T.create(0);assert.equal(hid(T.press(st,key,50)).length,0);assert.equal(st.page,'menu');
  }
});
test('passkey preserves leading zero and rejects invalid values',()=>{
  const st=pairing();T.sim(st,'passkey',20,123);assert.equal(st.pairing.passkey,'000123');
  for (const bad of [-1,1000000,1.5,'12x456',null]) {T.sim(st,'passkey',30,bad);assert.equal(st.pairing.passkey,'000123');}
  T.sim(st,'passkey',40,'012345');assert.equal(st.pairing.passkey,'012345');
});
test('passkey event outside pairing has no effect',()=>{
  const st=menu(), before=JSON.stringify(st);T.sim(st,'passkey',10,'123456');assert.equal(JSON.stringify(st),before);
});
test('cancel pairing stays in connection page; late pair result ignored',()=>{
  const st=pairing();T.press(st,'long_up',20);assert.equal(st.page,'conn');assert.equal(st.pairing,null);
  const before=JSON.stringify(st);T.sim(st,'paired',30,'Late device');assert.equal(JSON.stringify(st),before);
});
test('pair timeout, pairing success, type cancellation and slot capacity',()=>{
  let st=pairing();T.tick(st,60010);assert.equal(st.pairing,null);assert.equal(st.toast.kind,'err');
  st=pairing();T.sim(st,'paired',20,'Test device');assert.equal(st.slots[2].name,'Test device');
  const os=st.slots[2].os;T.press(st,'up',30);T.press(st,'long_up',40);assert.equal(st.osPick,null);assert.equal(st.slots[2].os,os);
  st.connSel=3;T.press(st,'ok',50);assert.equal(st.pairing,null);assert.equal(st.toast.kind,'err');
});
test('deleting active slot disconnects without modifying other bonds',()=>{
  const st=menu();st.page='conn';st.connSel=0;T.press(st,'long_down',10);T.press(st,'ok',20);
  assert.equal(st.slots[0],null);assert.equal(st.connected,false);assert.equal(st.slots[1].name,'iPhone');
});
test('disconnected actions produce no HID or fake camera success',()=>{
  const st=menu();T.sim(st,'disconnect',1);
  for (const page of ['macro','ppt','media','cam']) {st.page=page;assert.equal(hid(T.press(st,'ok',10)).length,0);}
  assert.equal(st.cam.shots,0);assert.equal(st.toast.kind,'err');
});
test('author Typeless defaults preserve right-side modifiers',()=>{
  const g=H.MACRO_GROUPS[1];
  assert.deepEqual(plain(H.reportBytes(H.resolve(g.up,'mac'))),[0x60,0,0,0,0,0,0,0]);
  assert.deepEqual(plain(H.reportBytes(H.resolve(g.ok,'mac'))),[0x40,0,0x10,0,0,0,0,0]);
  assert.deepEqual(plain(H.reportBytes(H.resolve(g.ok,'win'))),[0x40,0,0,0,0,0,0,0]);
  for (const os of H.OS_LIST) for (const group of H.MACRO_GROUPS) for (const key of ['up','ok','down']) {
    const p=H.resolve(group[key],os);assert.ok(!(p.usage>=0x68&&p.usage<=0x73));
  }
});
test('camera countdown cancellation and exact five-shot burst cadence',()=>{
  const st=menu();st.page='cam';T.press(st,'up',0);T.press(st,'ok',10);T.tick(st,1010);T.press(st,'ok',1011);T.tick(st,5010);assert.equal(st.cam.shots,0);
  T.press(st,'down',6000);assert.equal(hid(T.tick(st,6000)).length,1);assert.equal(hid(T.tick(st,6599)).length,0);
  for (const time of [6600,7200,7800,8400]) assert.equal(hid(T.tick(st,time)).length,1);
  assert.equal(st.cam.shots,5);assert.equal(st.cam.burstLeft,0);
});
test('PPT timer survives navigation, returns minimum page one, stops on end',()=>{
  const st=menu();st.page='ppt';T.press(st,'long_ok',100);T.press(st,'up',200);assert.equal(st.ppt.pages,1);
  T.press(st,'long_up',300);assert.equal(T.pptElapsed(st,1600),1500);
  st.page='ppt';T.press(st,'long_down',2000);assert.equal(T.pptElapsed(st,9000),1900);
});
test('phone meeting page refuses keyboard shortcuts',()=>{
  const st=menu();st.page='meet';st.slots[0].os='ios';assert.equal(hid(T.press(st,'ok',10)).length,0);assert.equal(st.toast.kind,'err');
});
test('wake resets inactivity and connection, returns to boot',()=>{
  const st=menu();T.sim(st,'wake',999999);assert.equal(st.lastInput,999999);assert.equal(st.connected,false);
  assert.equal(st.page,'boot');assert.equal(T.sleepDue(st,1000000),false);
});
test('short/long boundary, delayed release and single ADC owner',()=>{
  const st=B.create();B.down(st,'up',0);B.down(st,'down',1);assert.equal(st.active,'up');
  assert.deepEqual(plain(B.up(st,'up',499)),['up']);
  B.down(st,'ok',1000);assert.deepEqual(plain(B.tick(st,1499)),[]);assert.deepEqual(plain(B.tick(st,1500)),['long_ok']);
  assert.deepEqual(plain(B.up(st,'ok',1700)),[]);
  B.down(st,'down',2000);assert.deepEqual(plain(B.up(st,'down',2700)),['long_down']);
  B.down(st,'up',3000);B.cancel(st);assert.deepEqual(plain(B.up(st,'up',3100)),[]);
});

function contract(api) {
  const st=api.T.create(0);api.T.tick(st,5499);assert.equal(st.page,'boot');
  assert.equal(api.H.resolve(api.H.MACRO_GROUPS[1].up,'mac').mod,0x60);
  st.page='cam';api.T.press(st,'down',0);api.T.tick(st,0);api.T.tick(st,600);assert.equal(st.cam.shots,2);
}
test('contract catches timing, right-modifier and burst-cadence mutations',()=>{
  contract(load());
  for (const [file,from,to] of [
    ['tk_core.js','BOOT_MS = 5500','BOOT_MS = 3500'],
    ['tk_hid.js','ralt: 0x40','ralt: 0x04'],
    ['tk_core.js','gapMs: 600','gapMs: 800'],
  ]) {
    const source=fs.readFileSync(path.join(root,'game-art/toolkit/prototype',file),'utf8');assert.ok(source.includes(from));
    assert.throws(()=>contract(load({[file]:source.replace(from,to)})));
  }
});
