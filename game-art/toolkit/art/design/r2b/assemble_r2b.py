#!/usr/bin/env python3
"""R2b: approved 3x head, complete waist-up edits, transformed ear gear."""
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image,ImageChops,ImageDraw

ROOT=Path(__file__).resolve().parent
ART=ROOT.parent.parent
R1B=ROOT.parent/'r1b'
R2=ROOT.parent/'r2'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


b=module('r1b',R1B/'assemble_r1b.py')
old=module('r2',R2/'assemble_r2.py')
old.r1.HEAD_BOX=b.HEAD_BOX
NAMES=('S2_meet','S3_media','S4_cam','S5_macro')
LABELS=('S2 MEETING','S3 MEDIA','S4 CAMERA','S5 SHORTCUTS')


def gear_layer(name):
    if name not in NAMES[:2]: return Image.new('RGBA',(1024,1024))
    gear=Image.open(R2/f'{name}_accessory.png').convert('RGBA')
    # Old frame: 4.5x at (8,24). Approved frame: 3x at (176,30).
    # Inverse affine maps new coordinates to old: (1.5*x-256,1.5*y-21).
    gear=gear.transform((1024,1024),Image.Transform.AFFINE,
                        (1.5,0,-256,0,1.5,-21),Image.Resampling.BICUBIC)
    gear.save(ROOT/f'{name}_accessory.png')
    return gear


def small_check(layers):
    out=Image.new('RGB',(512,432)); draw=ImageDraw.Draw(out)
    for row,bg in enumerate(b.r1.BACKGROUNDS):
        y=row*216; draw.rectangle((0,y,511,y+215),fill=bg)
        draw.text((6,y+4),'#%02X%02X%02X  110px bust / 64px avatar'%bg,font=b.r1.font(10),fill='white')
        for i,(layer,label) in enumerate(zip(layers,('S2','S3','S4','S5'))):
            x=i*128
            bust=layer.crop((0,60,1024,1024)).resize((117,110),Image.Resampling.LANCZOS)
            out.paste(b.r1.over_background(bust,bg),(x+5,y+32))
            head=layer.crop(b.HEAD_BOX)
            square=Image.new('RGBA',(530,530)); square.alpha_composite(head,(0,35))
            avatar=square.resize((64,64),Image.Resampling.LANCZOS)
            circle=Image.new('L',(64,64)); ImageDraw.Draw(circle).ellipse((0,0,63,63),fill=255)
            avatar.putalpha(ImageChops.multiply(avatar.getchannel('A'),circle))
            out.paste(b.r1.over_background(avatar,bg),(x+32,y+147))
            draw.text((x+47,y+18),label,font=b.r1.font(10),fill='white')
    out.save(ROOT/'small_check_1x.png')
    out.resize((2048,1728),Image.Resampling.NEAREST).save(ROOT/'small_check.png')


def all_seven(layers):
    headliners=[Image.open(R1B/f'{n}_cutout.png').convert('RGBA')
                 for n in ('S0_base','S0R_remote','S1_ppt')]
    all_layers=headliners+layers
    labels=('S0 DOCTOR','S0R BOOT REMOTE','S1 B PPT')+LABELS
    out=Image.new('RGB',(1120,660),(239,235,229)); draw=ImageDraw.Draw(out)
    for i,(layer,label) in enumerate(zip(all_layers,labels)):
        x=(i%4)*280; y=(i//4)*330
        draw.text((x+10,y+8),label,font=b.r1.font(17),fill=(25,35,50))
        thumb=layer.resize((272,272),Image.Resampling.LANCZOS)
        out.paste(b.r1.over_background(thumb,b.r1.BACKGROUNDS[0]),(x+4,y+38))
    approved=(ROOT/'acceptance.json').exists()
    draw.text((850,380),'ALL 7 FRAMES APPROVED' if approved else 'S0/S0R/S1 B APPROVED',font=b.r1.font(15),fill=(25,35,50))
    draw.text((850,411),'GROK BATCH 1 READY' if approved else 'S2-S5: USER REVIEW',font=b.r1.font(15),fill=(25,35,50))
    out.save(ROOT/'all_seven.png')
    return all_layers


def main():
    head=Image.open(R1B/'head_locked.png').convert('RGBA')
    base=Image.open(ART/'start/S0_base.png').convert('RGB')
    assert base.tobytes()==Image.open(R1B/'S0_base.png').convert('RGB').tobytes()
    layers=[]; finals=[]; gears=[]; transforms={}
    for name in NAMES:
        raw=Image.open(ROOT/f'generated/{name}_raw.png')
        layer=b.r1.key_green(raw).resize((1024,1024),Image.Resampling.LANCZOS)
        bottom=layer.getchannel('A').point(lambda a:255 if a>127 else 0).getbbox()[3]
        factor=(1024-b.BODY_START)/(bottom-b.BODY_START)
        torso=layer.crop((0,b.BODY_START,1024,bottom))
        torso=torso.resize((round(1024*factor),1024-b.BODY_START),Image.Resampling.LANCZOS)
        layer=Image.new('RGBA',(1024,1024))
        layer.alpha_composite(torso,((1024-torso.width)//2,b.BODY_START))
        layer.alpha_composite(head)
        gear=gear_layer(name); layer.alpha_composite(gear)
        layer.save(ROOT/f'{name}_cutout.png')
        final=b.r1.over_background(layer); final.save(ROOT/f'{name}.png')
        layers.append(layer); finals.append(final); gears.append(gear)
        transforms[name]={'uniform_body_scale':factor,'raw_bottom':bottom}
    original=Image.new('RGB',(1024,1024))
    original.paste(Image.open(b.r1.REFERENCE).crop((0,0,224,224)).resize((672,672),Image.Resampling.LANCZOS),b.OFFSET)
    old.comparison([original,base]+finals,['REFERENCE','S0 APPROVED']+list(LABELS),ROOT/'compare.png')
    small_check(layers); all_seven(layers)
    qa={'status':'R1b and R2b approved by user; Grok batch 1 ready' if (ROOT/'acceptance.json').exists() else 'R1b approved by user; R2b technical QA complete, visual review pending',
        'head_source':'../r1b/head_locked.png','scale':3,'offset':[176,30],
        'head_sha256':hashlib.sha256((R1B/'head_locked.png').read_bytes()).hexdigest(),
        'gear_inverse_affine':[1.5,0,-256,0,1.5,-21],
        'body_transforms':transforms,'outputs':{}}
    for name,final,layer,gear in zip(NAMES,finals,layers,gears):
        diff=ImageChops.difference(final,base).crop((0,0,1024,b.BODY_START))
        protected=head.getchannel('A').crop((0,0,1024,b.BODY_START))
        overlay=gear.getchannel('A').crop((0,0,1024,b.BODY_START))
        changed=sum(any(rgb) and a==255 and g==0 for rgb,a,g in
                    zip(diff.get_flattened_data(),protected.get_flattened_data(),overlay.get_flattened_data()))
        cap=ImageChops.difference(final.crop((410,80,620,200)),base.crop((410,80,620,200))).getbbox()
        mouth=ImageChops.difference(final.crop((490,440,565,478)),base.crop((490,440,565,478))).getbbox()
        bad=sum(a==0 and rgb!=b.r1.GREEN for a,rgb in zip(layer.getchannel('A').get_flattened_data(),final.get_flattened_data()))
        bounds=layer.getchannel('A').point(lambda a:255 if a>127 else 0).getbbox()
        assert changed==0 and cap is None and mouth is None and bad==0
        assert bounds[3]==1024 and final.size==(1024,1024)
        qa['outputs'][name]={'size':[1024,1024],'subject_bounds':bounds,
            'head_difference_outside_accessory':changed,'cap_mark_unchanged':True,
            'mouth_unchanged':True,'background_errors':bad,
            'sha256':hashlib.sha256((ROOT/f'{name}.png').read_bytes()).hexdigest()}
    (ROOT/'qa.json').write_text(json.dumps(qa,indent=2)+'\n')
    print(json.dumps(qa,indent=2))


if __name__=='__main__': main()
