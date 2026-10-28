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
  st.connSel=3;T.press(st,'ok',50);assert.notEqual(st.pairing,null);
  assert.equal(st.slots[0].name,'MacBook'); // Opening the window does not evict.
  T.sim(st,'paired',60,'Fourth device');assert.equal(st.slots[0].name,'Fourth device');
  assert.equal(st.slots[1].name,'iPhone');assert.equal(st.slots[2].name,'Test device');
});
test('full-slot cancellation preserves bonds; new pairings replace oldest, not last used',()=>{
  const st=pairing();T.sim(st,'paired',20,'Reader');T.press(st,'long_up',30);
  st.connSel=3;T.press(st,'ok',40);
  const slots=JSON.stringify(st.slots), order=JSON.stringify(st.bindOrder);
  T.press(st,'ok',50);T.sim(st,'paired',60,'Ignored late pair');
  assert.equal(JSON.stringify(st.slots),slots);assert.equal(JSON.stringify(st.bindOrder),order);
  T.press(st,'ok',70);T.tick(st,60070);assert.equal(JSON.stringify(st.slots),slots);
  assert.equal(JSON.stringify(st.bindOrder),order);
  st.connSel=0;T.press(st,'ok',60080); // Using oldest MacBook does not make it newest.
  st.connSel=3;T.press(st,'ok',60090);T.sim(st,'paired',60100,'TV');
  assert.deepEqual(plain(st.slots.map(x=>x.name)),['TV','iPhone','Reader']);
  T.press(st,'long_up',60110);st.connSel=3;T.press(st,'ok',60120);T.sim(st,'paired',60130,'New computer');
  assert.deepEqual(plain(st.slots.map(x=>x.name)),['TV','New computer','Reader']);
  assert.deepEqual(plain(st.bindOrder),[2,0,1]);
});
test('deleting active slot disconnects without modifying other bonds',()=>{
  const st=menu();st.page='conn';st.connSel=0;T.press(st,'long_down',10);T.press(st,'ok',20);
  assert.equal(st.slots[0],null);assert.equal(st.connected,false);assert.equal(st.slots[1].name,'iPhone');
});
test('old bonded reconnect cannot occupy the new-device pairing window',()=>{
  const st=pairing();T.sim(st,'reconnect',20);assert.equal(st.connected,false);assert.ok(st.pairing);
  T.sim(st,'paired',30,'New host');assert.equal(st.connected,true);assert.equal(st.slots[2].name,'New host');
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
test('shortcut defaults retain reading and screenshot cancel while video moves to media on every host',()=>{
  assert.deepEqual(plain(H.MACRO_GROUPS.map(g=>g.name)),['截图','Typeless','剪映','微信读书','编辑']);
  for(const os of H.OS_LIST) {
    assert.deepEqual(plain(H.reportBytes(H.resolve(H.MACRO_GROUPS[0].down,os))),[0,0,0x29,0,0,0,0,0]);
    for(const group of [H.MACRO_GROUPS[3],H.DOUYIN_KEYS])
      for(const [key,usage] of [['up',0x52],['ok',0x4f],['down',0x51]])
        assert.deepEqual(plain(H.reportBytes(H.resolve(group[key],os))),[0,0,usage,0,0,0,0,0]);
    for(const [key,usage] of [['up',0x1d],['ok',0x06],['down',0x04]]) {
      const packet=H.resolve(H.MACRO_GROUPS[4][key],os);
      assert.equal(packet.mod,H.isApple(os)?8:1);assert.equal(packet.usage,usage);
    }
  }
});

test('media selection emits no HID and music/video short keys stay distinct on every host',()=>{
  for(const os of H.OS_LIST) {
    const st=menu();st.page='media';st.slots[0].os=os;
    assert.equal(st.media.choosing,true);assert.equal(st.media.mode,0);
    assert.equal(hid(T.press(st,'ok',10)).length,0);assert.equal(st.media.choosing,false);
    for(const key of ['up','ok','down']) {
      const packets=hid(T.press(st,key,20));assert.equal(packets.length,1);
      assert.equal(packets[0].kind,'media');assert.equal(packets[0].usage,H.resolve(H.MEDIA_KEYS[key],os).usage);
    }
    st.media.choosing=true;
    assert.equal(hid(T.press(st,'down',30)).length,0);assert.equal(st.media.mode,1);
    assert.equal(hid(T.press(st,'ok',40)).length,0);assert.equal(st.media.choosing,false);
    for(const [key,usage] of [['up',0x52],['ok',0x4f],['down',0x51]]) {
      const packets=hid(T.press(st,key,50));assert.equal(packets.length,1);
      assert.equal(packets[0].kind,'key');assert.equal(packets[0].mod,0);assert.equal(packets[0].usage,usage);
    }
  }
});

function remote(page='macro',mode=0) {
  const st=menu();st.page=page;
  if(page==='media'){st.media.mode=mode;st.media.choosing=false;}
  T.tick(st,10);return st;
}

test('continuous reading keys still turn the display off at 30 seconds without dropping HID',()=>{
  const st=remote();st.macro.group=3;
  for(let i=1;i<=31;i++) {
    const packets=hid(T.press(st,'down',10+i*1000));
    assert.equal(packets.length,1);assert.equal(packets[0].usage,0x51);
    assert.equal(st.display.off,i>=30);assert.equal(st.display.since,10);
  }
  assert.equal(st.connected,true);assert.equal(T.sleepDue(st,31010),false);
  assert.equal(hid(T.press(st,'ok',31020))[0].usage,0x4f);assert.equal(st.display.off,true);
});

test('dark long OK only wakes; at the exact timeout it cannot change groups or send next track',()=>{
  for(const page of ['macro','media']) {
    const st=remote(page),group=st.macro.group;
    assert.deepEqual(plain(T.press(st,'long_ok',30010)),[]);
    assert.equal(st.display.off,false);assert.equal(st.display.since,30010);
    assert.equal(st.macro.group,group);assert.equal(st.page,page);
    const lit=T.press(st,'long_ok',30020);
    if(page==='macro')assert.equal(st.macro.group,(group+1)%H.MACRO_GROUPS.length);
    else assert.equal(hid(lit)[0].usage,H.MEDIA.NEXT);
  }
});

test('dark long Down wakes on group navigation but previous music still works without lighting',()=>{
  let st=remote();T.tick(st,30010);assert.equal(st.display.off,true);
  assert.equal(hid(T.press(st,'long_down',30020)).length,0);
  assert.equal(st.macro.group,H.MACRO_GROUPS.length-1);assert.equal(st.display.off,false);
  assert.equal(st.display.since,30020);
  st=remote('media');T.tick(st,30010);
  assert.equal(hid(T.press(st,'long_down',30020))[0].usage,H.MEDIA.PREV);
  assert.equal(st.display.off,true);assert.equal(st.display.since,10);
});

test('long Up returns safely from dark remote and media returns through its selector',()=>{
  let st=remote();T.tick(st,30010);
  assert.equal(hid(T.press(st,'long_up',30020)).length,0);
  assert.equal(st.page,'menu');assert.equal(st.display.off,false);assert.equal(st.display.since,-1);
  st=remote('media',1);T.tick(st,30010);
  assert.equal(hid(T.press(st,'long_up',30020)).length,0);
  assert.equal(st.page,'media');assert.equal(st.media.choosing,true);assert.equal(st.display.off,false);
  assert.equal(hid(T.press(st,'long_up',30030)).length,0);assert.equal(st.page,'menu');
});

test('screen-saving setting, disconnection and visible dialogs keep the display available',()=>{
  const changes=[
    st=>{st.settings.remoteDim=false;},st=>{st.connected=false;},st=>{st.page='menu';},
    st=>{st.osPick={slot:0,sel:0};},st=>{st.pairing={until:999999,passkey:'123456'};},
    st=>{st.page='media';st.media.choosing=true;},
  ];
  for(const change of changes) {
    const st=remote();T.tick(st,30010);assert.equal(st.display.off,true);
    change(st);T.tick(st,30020);assert.equal(st.display.off,false);assert.equal(st.display.since,-1);
  }
  const st=menu();st.page='set';st.setSel=4;
  T.press(st,'ok',10);assert.equal(st.settings.remoteDim,false);
  T.press(st,'ok',20);assert.equal(st.settings.remoteDim,true);
  st.setSel=5;T.press(st,'down',30);assert.equal(st.setSel,0);
  T.press(st,'up',40);assert.equal(st.setSel,5);
});

test('an unavailable host binding lights the display so its error remains visible',()=>{
  const st=remote(),slot={label:'Unset',mac:null,win:null};
  assert.equal(T.applyConfig(st,{v:1,groups:[{name:'Custom',up:slot,ok:slot,down:slot}],cards:st.cards}),true);
  T.tick(st,30010);assert.equal(st.display.off,true);
  assert.equal(hid(T.press(st,'up',30020)).length,0);
  assert.equal(st.toast.kind,'err');assert.equal(st.display.off,false);
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
