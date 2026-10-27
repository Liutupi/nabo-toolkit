#!/usr/bin/env python3
"""Build fixed-anchor, <=64-color RGB565 sprites from reviewed Grok originals."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import PIL
from PIL import Image

from toolkit_sprite_codec import encode,decode

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'game-art/toolkit/art'
OUT=ROOT/'game-art/toolkit/sprites'
WEB=ROOT/'game-art/toolkit/prototype/assets'
BG=np.array((20,32,58),dtype=np.float32)
IDS=('welcome','base','ppt','meet','media','cam','macro')


def key(frame):
    c=np.asarray(frame,dtype=np.float32)
    r,g,b=c[:,:,0],c[:,:,1],c[:,:,2]
    dominance=np.minimum(g-r,g-b)
    a=np.where(g>70,np.clip((60-dominance)/40,0,1),1)
    background=c[0,0]
    rgb=np.clip((c-background*(1-a[:,:,None]))/np.maximum(a[:,:,None],.01),0,255)
    rgba=np.concatenate((rgb,a[:,:,None]*255),axis=2).round().astype(np.uint8)
    rgba[a<.01]=0
    return Image.fromarray(rgba).resize((256,256),Image.Resampling.LANCZOS)


def view(master,variant):
    if variant=='avatar':
        # One fixed head crop, including the entire downward nod, for all frames.
        result=master.crop((56,7,200,151)).resize((64,64),Image.Resampling.LANCZOS)
        yy,xx=np.mgrid[:64,:64]
        arr=np.array(result); arr[(xx-31.5)**2+(yy-31.5)**2>32**2,3]=0
        return Image.fromarray(arr)
    size=(115,150) if variant=='large' else (84,110)
    return master.crop((36,15,220,256)).resize(size,Image.Resampling.LANCZOS)


def flattened(image):
    arr=np.asarray(image,dtype=np.float32); alpha=arr[:,:,3:]/255
    rgb=np.clip(arr[:,:,:3]*alpha+BG*(1-alpha),0,255).round().astype(np.uint8)
    rgb &= np.array((248,252,248),dtype=np.uint8)
    return rgb,arr[:,:,3]>=128


def palette_for(images):
    pixels=np.concatenate([rgb[mask] for rgb,mask in images])
    height=(len(pixels)+255)//256
    training=np.zeros((height*256,3),dtype=np.uint8)
    training[:len(pixels)]=pixels; training[len(pixels):]=pixels[-1]
    pal=Image.fromarray(training.reshape(height,256,3)).quantize(colors=63,method=Image.Quantize.MEDIANCUT)
    colors=np.array(pal.getpalette()[:189],dtype=np.uint8).reshape(63,3)
    colors &= np.array((248,252,248),dtype=np.uint8)
    # A complete 16-bit lookup keeps transparent index zero separate from opaque black.
    values=np.arange(65536,dtype=np.int32)
    rgb=np.stack(((values>>11)<<3,((values>>5)&63)<<2,(values&31)<<3),axis=1)
    best=np.full(65536,2**31-1,dtype=np.int32); lookup=np.zeros(65536,dtype=np.uint8)
    for i,color in enumerate(colors):
        delta=rgb-color.astype(np.int32); distance=(delta*delta).sum(axis=1)
        better=distance<best; lookup[better]=i+1; best[better]=distance[better]
    palette=[0]+[int((int(r)>>3)<<11 | (int(g)>>2)<<5 | int(b)>>3) for r,g,b in colors]
    png_palette=[0,0,0]+colors.flatten().tolist()+[0]*(192*3)
    return palette,png_palette,lookup


def main():
    for p in (OUT/'bin',OUT/'master',OUT/'indexed',WEB/'sprites'): p.mkdir(parents=True,exist_ok=True)
    reviewed=json.loads((ART/'qa/batch1/metadata.json').read_text())
    approved={c['id']:c for c in reviewed['clips']}
    visual=json.loads((ART/'qa/batch1/review.json').read_text())
    assert visual['status']=='PASS_WITH_NOTES'
    for item in visual['clips']:
        assert approved[item['id']]['sha256']==item['source_sha256']
    sources=json.loads((ART/'delivery/NABO_Toolkit_Grok_Batch1/manifest.json').read_text())
    manifest={'version':1,'pillow':PIL.__version__,'numpy':np.__version__,
        'master_size':[256,256],'master_transform':'full source canvas -> 256 square; no per-frame bbox scaling',
        'bust_crop':[36,15,220,256],'avatar_crop':[56,7,200,151],
        'transparent_index':0,'edge_background':'#14203A','clips':{}}
    total=0
    for id,source in zip(IDS,sources['clips']):
        video=ROOT/approved[source['id']]['file']
        assert hashlib.sha256(video.read_bytes()).hexdigest()==approved[source['id']]['sha256']
        meta=approved[source['id']]; w,h=meta['width'],meta['height']; fps=meta['fps']
        raw=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-an','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
        stride=w*h*3; assert len(raw)//stride==meta['decoded_frames']
        indices=[0,18,30,42,54,66,78,96] if id=='welcome' else list(range(0,72,6))
        times=[round(i*1000/fps) for i in indices]
        duration=round(meta['duration_seconds']*1000) if id=='welcome' else 3000
        variants=['large'] if id=='welcome' else ['bust']+(['avatar'] if id=='base' else [])
        masters=[]
        (OUT/'master'/id).mkdir(exist_ok=True)
        for i,index in enumerate(indices):
            master=key(Image.frombytes('RGB',(w,h),raw[index*stride:(index+1)*stride]))
            master.save(OUT/'master'/id/f'{i:02d}.png'); masters.append(master)
        inputs={variant:[flattened(view(m,variant)) for m in masters] for variant in variants}
        palette,png_palette,lookup=palette_for([item for items in inputs.values() for item in items])
        clip={'durationMs':duration,'loop':id!='welcome','times':times,
            'source':str(video.relative_to(ROOT)),'source_sha256':meta['sha256'],'source_frame_indices':indices,
            'palette_rgb565':palette,'variants':{}}
        for variant in variants:
            iw,ih=view(masters[0],variant).size
            frames=[]; errors=[]; atlas=Image.new('P',(iw*len(masters),ih)); atlas.putpalette(png_palette); atlas.info['transparency']=0
            target=OUT/'indexed'/f'{id}_{variant}'; target.mkdir(exist_ok=True)
            for i,(rgb,mask) in enumerate(inputs[variant]):
                r,g,b=(rgb[:,:,k].astype(np.uint16) for k in range(3))
                color=(r>>3)<<11 | (g>>2)<<5 | b>>3
                indexed=lookup[color]; indexed[~mask]=0
                out=Image.fromarray(indexed); out.putpalette(png_palette); out.info['transparency']=0
                out.save(target/f'{i:02d}.png'); atlas.paste(out,(i*iw,0)); frames.append(indexed.tobytes())
                reconstructed=np.asarray(out.convert('RGB'),dtype=np.int16)
                difference=np.abs(reconstructed-rgb.astype(np.int16))[mask]
                errors.append({'mean':float(difference.mean()),'max':int(difference.max()),'p99':float(np.percentile(difference,99))})
                if errors[-1]['mean']>12 or errors[-1]['max']>96: raise ValueError(f'{id}/{variant}/{i}: quantization error {errors[-1]}')
            atlas.save(WEB/'sprites'/f'{id}_{variant}.png',transparency=0)
            data=encode(frames,iw,ih,palette,times,duration,id!='welcome',all_keys=variant=='large')
            result=decode(data)
            assert result['frames']==frames and result['times']==times and list(result['palette'])==palette
            file=OUT/'bin'/f'{id}_{variant}.tks'; file.write_bytes(data); total+=len(data)
            clip['variants'][variant]={'file':f'sprites/{id}_{variant}.png','w':iw,'h':ih,
                'binary':str(file.relative_to(ROOT)),'bytes':len(data),'decoded_pixel_differences':0,
                'sha256':hashlib.sha256(data).hexdigest(),'quantization':errors}
        manifest['clips'][id]=clip
        print(id, len(indices),'frames',sum(v['bytes'] for v in clip['variants'].values()),'bytes, exact decode PASS')
        del raw
    assert total<=1024*1024, f'Sprite budget exceeded: {total}'
    manifest['binary_bytes']=total
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    browser={'version':1,'audio':'boot-welcome.wav' if (WEB/'boot-welcome.wav').exists() else None,'clips':{}}
    for id,clip in manifest['clips'].items():
        browser['clips'][id]={'durationMs':clip['durationMs'],'loop':clip['loop'],'times':clip['times'],
            **{name:{k:v[k] for k in ('file','w','h')} for name,v in clip['variants'].items()}}
    (WEB/'toolkit_sprites.json').write_text(json.dumps(browser,indent=2)+'\n')
    print('Total:',total,'bytes; <=1 MiB PASS')


if __name__=='__main__': main()
