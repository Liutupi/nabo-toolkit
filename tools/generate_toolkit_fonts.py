"""Reproducible 4bpp subsets for the existing Toolkit UI; source fonts are build inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import re

ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--converter',type=Path,required=True)
    ap.add_argument('--font',type=Path,required=True)
    ap.add_argument('--numbers',type=Path,required=True)
    ap.add_argument('--subset-policy',type=Path,default=ROOT/'firmware/fonts/subset-symbols.json')
    args=ap.parse_args()
    version=subprocess.check_output(['node',str(args.converter),'--version'],text=True).strip()
    if version!='1.5.3':raise ValueError('lv_font_conv 1.5.3 required')
    files=list((ROOT/'firmware/main').glob('tk_*.c'))+[ROOT/'game-art/toolkit/prototype'/n for n in ('tk_core.js','tk_hid.js')]
    files=[p for p in files if not p.name.startswith('tk_font_')]
    symbols=''.join(sorted({c for p in files for c in p.read_text(encoding='utf-8') if ord(c)>127}))
    policy=json.loads(args.subset_policy.read_text(encoding='utf-8'))
    if policy.get('format')!='TKFONT_SUBSET1':raise ValueError('Unsupported font subset policy')
    primary=policy['symbols']
    if primary!=''.join(sorted(set(primary))):raise ValueError('Primary font symbols must be unique and sorted')
    fallback=''.join(c for c in symbols if c not in primary)
    # The existing 1bpp CJK font is already linked. New Han text uses this
    # fallback instead of duplicating its pixels in three 4bpp subsets.
    def cjk_range(c):return any(a<=ord(c)<=b for a,b in ((0x3000,0x303f),(0x4e00,0x9fff),(0xff00,0xffef)))
    if any(not cjk_range(c) for c in fallback):raise ValueError('Add new non-CJK symbols to the primary subset policy')
    check="const fs=require('fs'),path=require('path');const O=require(require.resolve('opentype.js',{paths:[process.argv[2]]}));const font=O.loadSync(process.argv[1]);const symbols=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(Array.from(symbols).filter(c=>!font.charToGlyphIndex(c))));"
    missing=json.loads(subprocess.check_output(['node','-e',check,str(args.font.resolve()),str(args.converter.resolve().parent)],input=json.dumps(symbols+primary).encode('utf-8')))
    if missing:raise ValueError('Missing source glyphs: '+repr(missing))
    out=ROOT/'firmware/fonts';out.mkdir(exist_ok=True)
    meta={'converter':'lv_font_conv 1.5.3','symbols':symbols,'primary_symbols':primary,'fallback_symbols':fallback,
          'subset_policy':args.subset_policy.resolve().relative_to(ROOT).as_posix(),
          'subset_policy_sha256':hashlib.sha256(args.subset_policy.read_bytes()).hexdigest(),
          'fallback_policy':'New CJK symbols use the existing 16px 1bpp fallback; legacy primary bitmaps remain unchanged.',
          'source_files':[p.relative_to(ROOT).as_posix() for p in sorted(files)],'outputs':{}}
    for size in (12,16,18,28,48):
        source=args.font if size<20 else args.numbers
        name=f'tk_font_{size}';dest=out/f'{name}.c'
        command=['node',str(args.converter),'--font',str(source),'--size',str(size),'--bpp','4','--format','lvgl',
                 '--no-compress','--no-kerning','--lv-font-name',name,'--output',str(dest)]
        command+=['--range','0x20-0x7e','--symbols',primary] if size<20 else ['--symbols',' 0123456789:+-'+('NABO' if size==28 else '')]
        subprocess.run(command,check=True,capture_output=True,text=True)
        generated=dest.read_text(encoding='utf-8')
        generated=generated.replace('#include "lvgl/lvgl.h"','#include "lvgl.h"')
        generated=generated.replace('.user_data = NULL',f'.user_data = (void *)(uintptr_t){size}')
        if size<20:
            generated=generated.replace('#include "lvgl.h"','#include "lvgl.h"\nextern const lv_font_t tk_font_cjk;')
            generated=generated.replace('.fallback = NULL','.fallback = &tk_font_cjk')
        generated=re.sub(r'(?m)^ \* Opts:.*$',f' * Toolkit subset: {source.name}, {size}px, 4bpp, converter 1.5.3; see fonts.json',generated)
        dest.write_text(generated,encoding='utf-8',newline='\n')
        meta['outputs'][name]={'size':size,'font':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                               'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size}
    # A compact 1bpp CJK fallback makes user-supplied Chinese labels usable without
    # three full 4bpp CJK fonts. It is read directly from Flash, scaled by the renderer.
    extract="const O=require(require.resolve('opentype.js',{paths:[process.argv[2]]}));const f=O.loadSync(process.argv[1]);let s='□';for(const [a,b] of [[0x3000,0x303f],[0x4e00,0x9fff],[0xff00,0xffef]])for(let n=a;n<=b;n++)if(f.charToGlyphIndex(String.fromCodePoint(n)))s+=String.fromCodePoint(n);console.log(JSON.stringify(s));"
    cjk=json.loads(subprocess.check_output(['node','-e',extract,str(args.font.resolve()),str(args.converter.resolve().parent)]))
    if len(cjk)<20000:raise ValueError('Incomplete CJK source font')
    if set(fallback)-set(cjk):raise ValueError('New UI text is missing from the existing CJK fallback')
    dest=out/'tk_font_cjk.c'
    subprocess.run(['node',str(args.converter),'--font',str(args.font),'--size','16','--bpp','1','--format','lvgl','--no-compress','--no-kerning','--lv-font-name','tk_font_cjk','--symbols',cjk,'--output',str(dest)],check=True,capture_output=True)
    generated=dest.read_text(encoding='utf-8').replace('#include "lvgl/lvgl.h"','#include "lvgl.h"')
    generated=generated.replace('.user_data = NULL','.user_data = (void *)(uintptr_t)16')
    generated=re.sub(r'(?m)^ \* Opts:.*$', ' * Toolkit user-label fallback: SourceHanSansCN-Medium, 16px, 1bpp; see fonts.json',generated)
    dest.write_text(generated,encoding='utf-8',newline='\n')
    meta['cjk_symbols']=cjk
    meta['outputs']['tk_font_cjk']={'size':16,'bpp':1,'font':args.font.name,'source_sha256':hashlib.sha256(args.font.read_bytes()).hexdigest(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size}
    (out/'fonts.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Toolkit fonts generated: legacy 12/16/18 Medium, 28/48 Archivo Black; {len(fallback)} UI symbols use CJK16 1bpp fallback')
if __name__=='__main__':main()
