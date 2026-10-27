'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {root}=require('./model.js');
function prototype() {
  const listeners={},elements={},buttons={};let clock=0,nextFrame;
  const element=()=>({checked:false,value:'1',classList:{add(){},remove(){}},addEventListener(type,fn){this[type]=fn;},prepend(){this.childElementCount++;},childElementCount:0,appendChild(){}});
  for(const id of ['lcd','log','speed','sound','rgb565','disc','reconn','wake','passkey','autopair','info'])elements[id]=element();
  elements.lcd.getContext=()=>({getImageData:()=>({data:new Uint8ClampedArray(0)}),putImageData(){}});
  for(const key of ['up','down','ok'])buttons[key]=Object.assign(element(),{dataset:{k:key},setPointerCapture(){}});
  const sandbox={performance:{now:()=>clock},Image:class{constructor(){this.complete=true;}},
    document:{getElementById:(id)=>elements[id],createElement:element,createTextNode:(s)=>s,
      querySelector:(s)=>buttons[s.match(/data-k="(.*?)"/)[1]],querySelectorAll:()=>Object.values(buttons)},
    localStorage:{getItem:()=>null},fetch:()=>Promise.resolve({ok:true,json:()=>Promise.resolve({clips:{}})}),
    addEventListener:(name,fn)=>(listeners[name]||(listeners[name]=[])).push(fn),
    requestAnimationFrame:(fn)=>{nextFrame=fn;},TKDraw:{draw(){}},NABO_IDLE:{},Date:undefined};
  sandbox.window=sandbox;const context=vm.createContext(sandbox);
  const dir=path.join(root,'game-art/toolkit/prototype');
  for(const file of ['tk_hid.js','tk_core.js','tk_buttons.js'])vm.runInContext(fs.readFileSync(path.join(dir,file),'utf8'),context,{filename:file});
  const html=fs.readFileSync(path.join(dir,'index.html'),'utf8');
  vm.runInContext(html.match(/<script>\s*([\s\S]*?)<\/script>/)[1],context,{filename:'prototype-inline.js'});
  function event(type,key){for(const fn of listeners[type]||[])fn({key,repeat:false,preventDefault(){}});}
  function key(name,ms=30){event('keydown',name);clock+=ms;event('keyup',name);}
  function frame(ms){clock+=ms;nextFrame(clock);}
  return {context,key,event,frame,elements,buttons,setClock:(ms)=>{clock=ms;}};
}
test('real inline DOM wiring: short key fires once without stale release variables',()=>{
  const app=prototype();app.key('Enter');assert.equal(app.context.TOOLKIT.state().page,'menu');
  app.key('Enter');assert.equal(app.context.TOOLKIT.state().page,'macro');
  app.key('ArrowUp');assert.equal(app.elements.log.childElementCount,1);
});
test('real inline DOM wiring: delayed release emits long once; blur cancels',()=>{
  const app=prototype();app.key('Enter');app.key('Enter');app.key('Enter',700);
  assert.equal(app.context.TOOLKIT.state().macro.group,1);assert.equal(app.elements.log.childElementCount,0);
  app.event('keydown','ArrowUp');app.event('blur');app.event('keyup','ArrowUp');
  assert.equal(app.elements.log.childElementCount,0);
});
test('real inline DOM wiring: pairing-code button and background tick are safe',()=>{
  const app=prototype();app.elements.passkey.onclick();
  assert.equal(app.context.TOOLKIT.state().pairing.passkey,'123456');
  app.frame(100);assert.equal(app.context.TOOLKIT.state().page,'conn');
});
