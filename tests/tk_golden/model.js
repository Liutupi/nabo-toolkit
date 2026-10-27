'use strict';
const fs=require('node:fs'), path=require('node:path'), vm=require('node:vm'), crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..');
const sources=['tk_hid.js','tk_config_schema.js','tk_core.js','tk_buttons.js'];
function load(overrides={}) {
  const context=vm.createContext({Date:undefined,performance:undefined,TextEncoder});
  for (const file of sources) {
    const text=overrides[file] ?? fs.readFileSync(path.join(root,'game-art/toolkit/prototype',file),'utf8');
    vm.runInContext(text,context,{filename:file});
  }
  return {T:context.TK,H:context.TKHID,B:context.TKButtons};
}
const plain=(value)=>JSON.parse(JSON.stringify(value));
function hashes() {
  return Object.fromEntries(sources.map((file)=>[file,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'game-art/toolkit/prototype',file))).digest('hex')]));
}
module.exports={load,plain,hashes,root};
