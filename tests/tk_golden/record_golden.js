#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path');
const {load,plain,hashes}=require('./model.js');
const {T,H}=load();
const output=path.resolve(process.argv[2]||__dirname);
fs.mkdirSync(output,{recursive:true});
const rows=[], pages=new Set(), events=new Set(), keys=new Set(),mediaModes=new Set(),screens=new Set(),voiceStatuses=new Set(),voiceTargets=new Set();
let scenario,st,now,step;
function record(call,out=[]) {
  pages.add(st.page);
  if(st.page==='media' && !st.media.choosing)mediaModes.add(st.media.mode);
  screens.add(st.display.off?'off':'on');
  voiceStatuses.add(st.voice.status);
  if(call.type==='voice_result' && call.accepted && call.outcome===1 && st.page!=='voice')voiceTargets.add(call.target);
  rows.push({scenario,step:step++,now,call,outputs:plain(out),state:plain(st),sleepDue:T.sleepDue(st,now)});
}
function start(name,os='mac') {
  scenario=name;now=0;step=0;st=T.create(now);st.slots[0].os=os;
  record({type:'init',fixture:'two demonstration bonds',os});
}
function press(key,dt=30) {now+=dt;keys.add(key);record({type:'press',key},T.press(st,key,now));}
function tick(ms) {now+=ms;record({type:'tick'},T.tick(st,now));}
function sim(event,arg) {now+=20;events.add(event);T.sim(st,event,now,arg);record({type:'sim',event,...(arg===undefined?{}:{arg})});}
function templates(counts) {now+=20;const accepted=T.voiceTemplates(st,counts);record({type:'voice_templates',counts,accepted});}
function progress(status,token=st.voice.token) {now+=20;const accepted=T.voiceProgress(st,token,status,now);record({type:'voice_progress',token,status,accepted});}
function voiceResult(outcome,target=-1,count=0,token=st.voice.token) {now+=20;const accepted=T.voiceResult(st,token,outcome,target,count,now);record({type:'voice_result',token,outcome,target,count,accepted});}
function page(id) {
  if (st.page==='boot') press('ok');
  let returns=0;
  while(st.page!=='menu') {if(++returns>4)throw new Error('Cannot return to menu');press('long_up');}
  while (st.menu!==T.MENU.indexOf(id)) press('down');
  press('ok');
}
function voicePage() {
  if(st.page==='boot')press('ok');
  let returns=0;while(st.page!=='menu'){if(++returns>4)throw new Error('Cannot return to voice menu');press('long_up');}
  press('long_ok');
}
function random(seed) {
  return ()=>{let t=seed+=0x6D2B79F5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};
}

start('boot_and_voice');tick(1399);tick(1);tick(4099);tick(1);sim('wake');press('up');
start('binding_fifo_replacement');page('conn');
while(st.connSel!==3)press('down');press('ok');sim('paired','Reader');press('ok');
while(st.connSel!==3)press('down');press('ok');press('ok'); // Cancel: keep all bonds.
press('ok');sim('paired','Office Xiaomi TV');press('ok');
while(st.connSel!==3)press('down');press('ok');sim('paired','New computer');press('ok');
for (const os of H.OS_LIST) {
  start('all_tools_'+os,os);press('ok');
  page('macro');
  for (let i=0;i<H.MACRO_GROUPS.length;i++) {for(const k of ['up','ok','down'])press(k);press('long_ok');}
  press('long_down');press('long_ok');
  page('ppt');press('long_ok');press('down');press('up');press('ok');press('ok');tick(480000);tick(120001);press('long_down');
  page('meet');
  for (let i=0;i<4;i++) {for(const k of ['up','ok','down'])press(k);press('long_ok');}
  page('media');press('ok');for(const k of ['up','down','ok','long_ok','long_down'])press(k);
  press('long_up');press('down');press('ok');for(const k of ['up','down','ok','long_ok','long_down'])press(k);
  page('cam');press('up');press('ok');tick(1000);tick(1000);tick(1000);
  press('up');press('ok');tick(1000);press('ok');tick(10000);
  press('down');tick(0);for(let i=0;i<4;i++)tick(600);
  page('card');press('ok');press('long_up');press('down');press('up');press('down');press('down');
  page('conn');sim('disconnect');sim('reconnect');press('long_ok');press('down');press('long_up');
  while(st.connSel!==3)press('down');press('ok');sim('passkey','000123');sim('paired','Fixture device');press('ok');
  while(st.connSel!==3)press('down');press('ok');press('up');press('long_down');press('ok');
  while(st.connSel!==3)press('down');press('ok');sim('passkey',654321);press('long_up');
  press('ok');tick(60000);
  page('set');for(let i=0;i<6;i++){press('ok');press('down');}
  tick(1800001);sim('wake');tick(5500);
}
for(const os of H.OS_LIST) {
  start('screen_deadline_long_ok_'+os,os);page('macro');press('long_ok',30000);
  page('media');press('ok');press('long_ok',30000);
  start('screen_off_remote_'+os,os);page('macro');
  for(let i=0;i<3;i++)press('long_ok');
  for(let i=0;i<31;i++)press('down',1000); // Continuous use must not keep the display lit.
  press('ok');press('up');press('long_ok'); // Dark long OK only wakes.
  tick(30000);press('long_down');tick(30000);sim('disconnect');sim('reconnect');
  tick(30000);press('long_up');page('media');press('ok');
  tick(30000);press('long_down');press('long_ok');press('long_ok'); // Previous while dark; wake; next while lit.
  press('long_up');press('down');press('ok');tick(30000);press('up');press('ok');press('down');press('long_ok');
  press('long_up');press('long_up');page('set');
  while(st.setSel!==4)press('down');press('ok');page('macro');tick(30001);press('down');
  page('set');press('ok');page('macro');tick(30000);press('long_ok');
  start('screen_off_binding_error_'+os,os);page('macro');
  const slot={label:'Unset',mac:null,win:null},empty={v:1,groups:[{name:'Custom',up:slot,ok:slot,down:slot}],cards:st.cards};
  if(!T.applyConfig(st,empty))throw new Error('Empty binding fixture invalid');
  record({type:'config',config:plain({v:1,groups:st.groups,cards:st.cards})});tick(30000);press('up');
}
for(const os of H.OS_LIST) {
  start('voice_async_navigation_'+os,os);voicePage();press('ok');
  for(const count of [1,2,3,3]){press('long_ok');progress(8);press('down');progress(2);voiceResult(0,0,count);}
  templates([3,1,1,1,1,1,1]);
  for(const outcome of [2,3,4,5,6]){press('ok');progress(1);voiceResult(outcome);}
  for(let target=0;target<T.VOICE_TARGETS.length;target++){voicePage();press('ok');progress(8);progress(1);voiceResult(1,target);tick(1);}
  voicePage();press('ok');const old=st.voice.token;press('long_up');progress(1,old);voiceResult(1,1,0,old);
  voicePage();press('ok');progress(2);progress(3);voiceResult(0,0,1);voiceResult(1,7);voiceResult(1,1,0,old);voiceResult(2);
  const slot={label:'Test',mac:{mod:0,key:4},win:{mod:0,key:4}};
  const cfg={v:1,groups:['截图','Other','读书','语音输入'].map(name=>({name,up:slot,ok:slot,down:slot})),cards:st.cards};
  if(!T.applyConfig(st,cfg))throw new Error('Voice named-group fixture invalid');
  record({type:'config',config:plain({v:1,groups:st.groups,cards:st.cards})});
  press('ok');progress(1);voiceResult(1,0);voicePage();press('ok');voiceResult(1,5);voicePage();press('ok');voiceResult(1,6);
  voicePage();cfg.groups=cfg.groups.slice(1,2);T.applyConfig(st,cfg);
  record({type:'config',config:plain({v:1,groups:st.groups,cards:st.cards})});
  for(const target of [0,5,6]){press('ok');progress(1);voiceResult(1,target);}
}
const choices=['up','down','ok','long_up','long_down','long_ok'];
for(const [index,os] of H.OS_LIST.entries()) {
  const seed=(0x4E41424F+index)>>>0, rng=random(seed);
  start('random_'+os+'_'+seed,os);
  for(let i=0;i<250;i++) {
    const action=Math.floor(rng()*12);
    if(action<6)press(choices[action],Math.floor(rng()*600));
    else if(action<8)tick(Math.floor(rng()*7000));
    else if(action===8)sim('disconnect');
    else if(action===9)sim('reconnect');
    else if(action===10)sim('wake');
    else sim(st.pairing?'passkey':'paired',st.pairing?Math.floor(rng()*1000000):'Ignored late device');
  }
}
for(const os of H.OS_LIST) {
  start('custom_config_'+os,os);page('macro');
  const custom={v:1,groups:[{name:'Custom',up:{label:'Right',mac:{mod:96,key:0},win:null},ok:{label:'Text',text:'Hi!\n'},down:{label:'Media',media:233}},
    {name:'Second',up:{label:'Empty',mac:null,win:null},ok:{label:'64 chars',text:'A'.repeat(64)},down:{label:'Chord',mac:{mod:8,key:5},win:{mod:1,key:5}}}],
    cards:[{title:'Card',name:'TEST',line:'Synthetic fixture',qr:'https://example.org/card'},{title:'More',name:'TEST2',line:'Second fixture',qr:'https://example.org/other'}]};
  if(!T.applyConfig(st,custom))throw new Error('Custom fixture invalid');record({type:'config',config:plain({v:1,groups:st.groups,cards:st.cards})});
  for(const key of ['up','ok','down','long_ok','up','ok','down','long_ok','long_down'])press(key);
  page('card');press('down');press('ok');press('long_up');
  custom.groups=custom.groups.slice(0,1);custom.cards=custom.cards.slice(0,1);
  if(!T.applyConfig(st,custom))throw new Error('Shrunk fixture invalid');record({type:'config',config:plain({v:1,groups:st.groups,cards:st.cards})});
  press('down');page('macro');press('long_ok');press('ok');
}
start('legacy_six_group_configuration');page('macro');
const legacy={v:1,groups:Array.from({length:6},(_,i)=>({name:i===5?'抖音':'Legacy'+i,
  up:{label:'Previous',mac:{mod:0,key:0x52},win:{mod:0,key:0x52}},
  ok:{label:'Right',mac:{mod:0,key:0x4f},win:{mod:0,key:0x4f}},
  down:{label:'Next',mac:{mod:0,key:0x51},win:{mod:0,key:0x51}}})),
  cards:[{title:'Keep',name:'SYNTHETIC',line:'Legacy card preserved',qr:'https://example.org/legacy'}]};
if(!T.applyConfig(st,legacy))throw new Error('Legacy six-group fixture invalid');
record({type:'config',config:plain({v:1,groups:st.groups,cards:st.cards})});
for(let i=0;i<5;i++)press('long_ok');for(const key of ['up','ok','down'])press(key);
function resolveTable(table,os) {return Object.fromEntries(Object.entries(table).map(([k,s])=>[k,H.resolve(s,os)]));}
const tables={source_sha256:hashes()['tk_hid.js'],MOD:H.MOD,KEY:H.KEY,MEDIA:H.MEDIA,OS_LIST:H.OS_LIST,OS_NAME:H.OS_NAME,
  PPT:H.PPT,MEET_APPS:H.MEET_APPS,MEDIA_KEYS:H.MEDIA_KEYS,DOUYIN_KEYS:H.DOUYIN_KEYS,SHUTTER:H.SHUTTER,MACRO_GROUPS:H.MACRO_GROUPS,CODE_USAGE:H.CODE_USAGE,CODE_MOD:H.CODE_MOD,resolved:{}};
for(const os of H.OS_LIST) tables.resolved[os]={
  ppt:resolveTable(H.PPT,os),media:resolveTable(H.MEDIA_KEYS,os),douyin:resolveTable(H.DOUYIN_KEYS,os),
  meetings:H.MEET_APPS.map((app)=>({name:app.name,...resolveTable({mute:app.mute,cam:app.cam,hand:app.hand},os)})),
  macros:H.MACRO_GROUPS.map((g)=>({name:g.name,...resolveTable({up:g.up,ok:g.ok,down:g.down},os)})),
};
const coverage={schemaVersion:1,source_sha256:hashes(),rows:rows.length,scenarios:[...new Set(rows.map((r)=>r.scenario))],
  pages:[...pages].sort(),events:[...events].sort(),keys:[...keys].sort(),os:[...H.OS_LIST],
  media_modes:[...mediaModes].sort(),display_states:[...screens].sort(),
  voice_statuses:[...voiceStatuses].sort((a,b)=>a-b),voice_targets_opened:[...voiceTargets].sort(),
  boot_ms:T.BOOT_MS,voice_at_ms:T.VOICE_AT_MS,
  scope:'JavaScript reference fixtures; production C equality is checked separately by test_tk_model.py; device acceptance is separate'};
for(const page of ['boot','menu',...T.MENU,'voice'])if(!pages.has(page))throw new Error('Page not covered: '+page);
for(const event of ['passkey','paired','disconnect','reconnect','wake'])if(!events.has(event))throw new Error('Event not covered: '+event);
for(const mode of [0,1])if(!mediaModes.has(mode))throw new Error('Media mode not covered: '+mode);
for(const state of ['on','off'])if(!screens.has(state))throw new Error('Display state not covered: '+state);
for(let status=0;status<12;status++)if(!voiceStatuses.has(status))throw new Error('Voice status not covered: '+status);
for(let target=0;target<T.VOICE_TARGETS.length;target++)if(!voiceTargets.has(target))throw new Error('Voice target not covered: '+target);
fs.writeFileSync(path.join(output,'traces.jsonl'),rows.map((r)=>JSON.stringify(r)).join('\n')+'\n');
fs.writeFileSync(path.join(output,'hid_tables.json'),JSON.stringify(tables,null,2)+'\n');
fs.writeFileSync(path.join(output,'coverage.json'),JSON.stringify(coverage,null,2)+'\n');
console.log(JSON.stringify(coverage,null,2));
