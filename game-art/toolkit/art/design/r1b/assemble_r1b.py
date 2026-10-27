#!/usr/bin/env python3
"""R1b: decontaminate only the black-matted source edge and lock a 3x head."""
from collections import deque
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent
R1=ROOT.parent/'r1'
ART=ROOT.parent.parent
spec=importlib.util.spec_from_file_location('r1',R1/'assemble_r1.py')
r1=importlib.util.module_from_spec(spec); spec.loader.exec_module(r1)
SCALE=3
OFFSET=(176,30)
BODY_START=494
PROTECTED_END=499
HEAD_END=510
HEAD_BOX=(250,50,780,510)
NAMES=('S0_base','S0R_remote','S1_ppt')


def clean_reference():
    source=Image.open(r1.REFERENCE).crop((0,0,224,224)).convert('RGB')
    original=Image.open(R1/'reference_left_cutout.png').getchannel('A')
    core=original.filter(ImageFilter.MinFilter(5))
    expanded=original.filter(ImageFilter.MaxFilter(3))
    colors=list(source.get_flattened_data())
    inside=list(core.get_flattened_data())
    allowed=list(expanded.get_flattened_data())
    nearest=[None]*len(colors)
    q=deque()
    for i,a in enumerate(inside):
        if a: nearest[i]=colors[i]; q.append(i)
    while q:
        i=q.popleft(); x,y=i%224,i//224
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=nx<224 and 0<=ny<224:
                j=ny*224+nx
                if allowed[j] and nearest[j] is None:
                    nearest[j]=nearest[i]; q.append(j)
    out=[]
    for i,c in enumerate(colors):
        if inside[i]: out.append(c+(255,)); continue
        fg=nearest[i]
        if fg is None or max(c)<10:
            out.append((0,0,0,0)); continue
        denominator=sum(v*v for v in fg)
        alpha=min(1,max(0,sum(a*b for a,b in zip(c,fg))/max(denominator,1)))
        if alpha<0.04:
            out.append((0,0,0,0)); continue
        out.append(tuple(round(max(0,min(255,v/alpha))) for v in c)+(round(alpha*255),))
    cutout=Image.new('RGBA',(224,224)); cutout.putdata(out)
    assert all(tuple(c[:3])==rgb for c,rgb,a in zip(out,colors,inside) if a)
    cutout.save(ROOT/'reference_edge_clean.png')
    core.save(ROOT/'reference_interior_mask.png')
    base=Image.new('RGBA',(1024,1024))
    base.alpha_composite(cutout.resize((672,672),Image.Resampling.LANCZOS),OFFSET)
    head=base.copy(); head.paste((0,0,0,0),(0,HEAD_END,1024,1024))
    alpha=head.getchannel('A')
    for y in range(PROTECTED_END,HEAD_END):
        f=(HEAD_END-y)/(HEAD_END-PROTECTED_END)
        alpha.paste(alpha.crop((0,y,1024,y+1)).point(lambda a:round(a*f)),(0,y))
    head.putalpha(alpha); head.save(ROOT/'head_locked.png')
    r1.over_background(base).save(ROOT/'S0_edit_input.png')
    # Edge evidence at native 224px, then exact nearest-neighbor 4x enlargement.
    sheet=Image.new('RGB',(448,224))
    sheet.paste(r1.over_background(Image.open(R1/'reference_left_cutout.png')),(0,0))
    sheet.paste(r1.over_background(cutout),(224,0))
    sheet.resize((1792,896),Image.Resampling.NEAREST).save(ROOT/'edge_check.png')
    return head


def compare(images, labels):
    out=Image.new('RGB',(1600,830),(239,235,229)); draw=ImageDraw.Draw(out)
    for i,(im,label) in enumerate(zip(images,labels)):
        x=i*400
        draw.text((x+12,12),label,font=r1.font(19),fill=(25,35,50))
        out.paste(im.resize((384,384),Image.Resampling.LANCZOS),(x+8,50))
        draw.text((x+12,460),'HEAD DETAIL',font=r1.font(18),fill=(25,35,50))
        detail=im.crop(HEAD_BOX); detail.thumbnail((384,334),Image.Resampling.LANCZOS)
        out.paste(detail,(x+(400-detail.width)//2,498))
    out.save(ROOT/'compare.png')


def small(layers):
    out=Image.new('RGB',(384,432)); draw=ImageDraw.Draw(out)
    for row,bg in enumerate(r1.BACKGROUNDS):
        y=row*216; draw.rectangle((0,y,383,y+215),fill=bg)
        draw.text((6,y+4),'#%02X%02X%02X  110px bust / 64px avatar'%bg,font=r1.font(10),fill='white')
        for i,(layer,label) in enumerate(zip(layers,('S0','S0R','S1 B'))):
            x=i*128
            # Fixed world bounds preserve the same head scale across all views.
            crop=layer.crop((220,60,804,1024))
            bust=crop.resize((67,110),Image.Resampling.LANCZOS)
            out.paste(r1.over_background(bust,bg),(x+30,y+32))
            head=layer.crop(HEAD_BOX)
            square=Image.new('RGBA',(530,530)); square.alpha_composite(head,(0,35))
            avatar=square.resize((64,64),Image.Resampling.LANCZOS)
            circle=Image.new('L',(64,64)); ImageDraw.Draw(circle).ellipse((0,0,63,63),fill=255)
            avatar.putalpha(ImageChops.multiply(avatar.getchannel('A'),circle))
            out.paste(r1.over_background(avatar,bg),(x+32,y+147))
            draw.text((x+44,y+18),label,font=r1.font(10),fill='white')
    out.save(ROOT/'small_check_1x.png')
    out.resize((1536,1728),Image.Resampling.NEAREST).save(ROOT/'small_check.png')


def main():
    ROOT.mkdir(exist_ok=True); (ROOT/'generated').mkdir(exist_ok=True)
    head=clean_reference()
    paths=[ROOT/f'generated/{n}_raw.png' for n in NAMES]
    if not any(p.exists() for p in paths):
        print('Prepared edit input and cleaned locked head; awaiting body edit outputs.'); return
    layers=[]; finals=[]
    body_transforms={}
    for name,path in zip(NAMES,paths):
        if not path.exists(): continue
        body=r1.key_green(Image.open(path)).resize((1024,1024),Image.Resampling.LANCZOS)
        bottom=body.getchannel('A').point(lambda a:255 if a>127 else 0).getbbox()[3]
        factor=(1024-BODY_START)/(bottom-BODY_START)
        torso=body.crop((0,BODY_START,1024,bottom))
        torso=torso.resize((round(1024*factor),1024-BODY_START),Image.Resampling.LANCZOS)
        extra=body.crop((250,460,370,BODY_START)) if name=='S0R_remote' else None
        body=Image.new('RGBA',(1024,1024))
        body.alpha_composite(torso,((1024-torso.width)//2,BODY_START))
        body_transforms[name]={'uniform_scale':factor,'neck_anchor':[512,BODY_START],'raw_bottom':bottom}
        body.paste((0,0,0,0),(0,0,1024,BODY_START))
        if extra is not None: body.alpha_composite(extra,(250,460))
        body.alpha_composite(head)
        body.save(ROOT/f'{name}_cutout.png')
        final=r1.over_background(body); final.save(ROOT/f'{name}.png')
        layers.append(body); finals.append(final)
    if not all(p.exists() for p in paths):
        print('Partial portraits prepared; awaiting remaining body edits.'); return
    original=Image.new('RGB',(1024,1024))
    original.paste(Image.open(r1.REFERENCE).crop((0,0,224,224)).resize((672,672),Image.Resampling.LANCZOS),OFFSET)
    compare([original]+finals,['REFERENCE - SAME SCALE','S0 - WIDER WAIST CROP','S0R - WHITE REMOTE','S1 B - CHARCOAL / BLUE'])
    small(layers)
    qa={'scale':SCALE,'offset':list(OFFSET),'protected_rows':[0,BODY_START-1],
        'neck_join_rows':[PROTECTED_END,HEAD_END-1],
        'reference_sha256':hashlib.sha256(r1.REFERENCE.read_bytes()).hexdigest(),
        'edge_treatment':'Nearest-interior black-matte alpha estimate and unpremultiplication only in 2px contour band; all native interior RGB pixels unchanged',
        'status':'R1b prepared per rework handoff; visual review pending','body_transforms':body_transforms,'outputs':{}}
    for name,im,layer in zip(NAMES,finals,layers):
        diff=ImageChops.difference(im.crop((0,0,1024,BODY_START)),finals[0].crop((0,0,1024,BODY_START)))
        bad=sum(a==0 and rgb!=r1.GREEN for a,rgb in zip(layer.getchannel('A').get_flattened_data(),im.get_flattened_data()))
        protected=head.getchannel('A').crop((0,0,1024,BODY_START))
        changed=sum(any(rgb) and a==255 for rgb,a in zip(diff.get_flattened_data(),protected.get_flattened_data()))
        assert changed==0 and bad==0 and im.size==(1024,1024)
        qa['outputs'][name]={'head_difference_vs_S0':changed,'background_errors':bad,
            'subject_bounds':layer.getchannel('A').point(lambda a:255 if a>127 else 0).getbbox(),
            'sha256':hashlib.sha256((ROOT/f'{name}.png').read_bytes()).hexdigest()}
    (ROOT/'qa.json').write_text(json.dumps(qa,indent=2)+'\n')
    print(json.dumps(qa,indent=2))


if __name__=='__main__': main()
