#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path');
const {load,plain,hashes}=require('./model.js');
const {T,H}=load();
const output=path.resolve(process.argv[2]||__dirname);
fs.mkdirSync(output,{recursive:true});
const rows=[], pages=new Set(), events=new Set(), keys=new Set();
let scenario,st,now,step;
function record(call,out=[]) {
  pages.add(st.page);
  rows.push({scenario,step:step++,now,call,outputs:plain(out),state:plain(st),sleepDue:T.sleepDue(st,now)});
}
function start(name,os='mac') {
  scenario=name;now=0;step=0;st=T.create(now);st.slots[0].os=os;
  record({type:'init',fixture:'two demonstration bonds',os});
}
function press(key,dt=30) {now+=dt;keys.add(key);record({type:'press',key},T.press(st,key,now));}
function tick(ms) {now+=ms;record({type:'tick'},T.tick(st,now));}
function sim(event,arg) {now+=20;events.add(event);T.sim(st,event,now,arg);record({type:'sim',event,...(arg===undefined?{}:{arg})});}
function page(id) {
  if (st.page==='boot') press('ok');
  if (st.page!=='menu') press('long_up');
  while (st.menu!==T.MENU.indexOf(id)) press('down');
  press('ok');
}
function random(seed) {
  return ()=>{let t=seed+=0x6D2B79F5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};
}

start('boot_and_voice');tick(1399);tick(1);tick(4099);tick(1);sim('wake');press('up');
for (const os of H.OS_LIST) {
  start('all_tools_'+os,os);press('ok');
  page('macro');
  for (let i=0;i<6;i++) {for(const k of ['up','ok','down'])press(k);press('long_ok');}
  press('long_down');press('long_ok');
  page('ppt');press('long_ok');press('down');press('up');press('ok');press('ok');tick(480000);tick(120001);press('long_down');
  page('meet');
  for (let i=0;i<4;i++) {for(const k of ['up','ok','down'])press(k);press('long_ok');}
  page('media');for(const k of ['up','down','ok','long_ok','long_down'])press(k);
  page('cam');press('up');press('ok');tick(1000);tick(1000);tick(1000);
  press('up');press('ok');tick(1000);press('ok');tick(10000);
  press('down');tick(0);for(let i=0;i<4;i++)tick(600);
  page('card');press('ok');press('long_up');press('down');press('up');press('down');press('down');
  page('conn');sim('disconnect');sim('reconnect');press('long_ok');press('down');press('long_up');
  while(st.connSel!==3)press('down');press('ok');sim('passkey','000123');sim('paired','Fixture device');press('ok');
  while(st.connSel!==3)press('down');press('ok');press('up');press('long_down');press('ok');
  while(st.connSel!==3)press('down');press('ok');sim('passkey',654321);press('long_up');
  press('ok');tick(60000);
  page('set');for(let i=0;i<5;i++){press('ok');press('down');}
  tick(1800001);sim('wake');tick(5500);
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
function resolveTable(table,os) {return Object.fromEntries(Object.entries(table).map(([k,s])=>[k,H.resolve(s,os)]));}
const tables={source_sha256:hashes()['tk_hid.js'],MOD:H.MOD,KEY:H.KEY,MEDIA:H.MEDIA,OS_LIST:H.OS_LIST,OS_NAME:H.OS_NAME,
  PPT:H.PPT,MEET_APPS:H.MEET_APPS,MEDIA_KEYS:H.MEDIA_KEYS,SHUTTER:H.SHUTTER,MACRO_GROUPS:H.MACRO_GROUPS,CODE_USAGE:H.CODE_USAGE,CODE_MOD:H.CODE_MOD,resolved:{}};
for(const os of H.OS_LIST) tables.resolved[os]={
  ppt:resolveTable(H.PPT,os),media:resolveTable(H.MEDIA_KEYS,os),
  meetings:H.MEET_APPS.map((app)=>({name:app.name,...resolveTable({mute:app.mute,cam:app.cam,hand:app.hand},os)})),
  macros:H.MACRO_GROUPS.map((g)=>({name:g.name,...resolveTable({up:g.up,ok:g.ok,down:g.down},os)})),
};
const coverage={schemaVersion:1,source_sha256:hashes(),rows:rows.length,scenarios:[...new Set(rows.map((r)=>r.scenario))],
  pages:[...pages].sort(),events:[...events].sort(),keys:[...keys].sort(),os:[...H.OS_LIST],
  boot_ms:T.BOOT_MS,voice_at_ms:T.VOICE_AT_MS,
  scope:'JavaScript reference fixtures only; C replay and device validation remain pending'};
for(const page of ['boot','menu',...T.MENU])if(!pages.has(page))throw new Error('Page not covered: '+page);
for(const event of ['passkey','paired','disconnect','reconnect','wake'])if(!events.has(event))throw new Error('Event not covered: '+event);
fs.writeFileSync(path.join(output,'traces.jsonl'),rows.map((r)=>JSON.stringify(r)).join('\n')+'\n');
fs.writeFileSync(path.join(output,'hid_tables.json'),JSON.stringify(tables,null,2)+'\n');
fs.writeFileSync(path.join(output,'coverage.json'),JSON.stringify(coverage,null,2)+'\n');
console.log(JSON.stringify(coverage,null,2));
