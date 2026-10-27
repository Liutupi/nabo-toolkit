#!/usr/bin/env python3
"""Fully decode unmodified Grok originals and produce 0.25s QA contact sheets."""
import hashlib
import json
import math
from pathlib import Path
import subprocess

from PIL import Image,ImageChops,ImageDraw,ImageFont,ImageStat

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'game-art/toolkit/art'
VIDEO=ART/'video/batch1'
OUT=ART/'qa/batch1'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'


def run(args):
    return subprocess.run(args,capture_output=True,check=True).stdout


def bounds(im):
    thumb=im.resize((180,180),Image.Resampling.BILINEAR)
    mask=Image.new('L',thumb.size)
    mask.putdata([0 if g>r+30 and g>b+30 else 255
                  for r,g,b in thumb.get_flattened_data()])
    box=mask.getbbox()
    return [v*4 for v in box] if box else None


def difference(a,b):
    diff=ImageChops.difference(a.resize((180,180)),b.resize((180,180)))
    return round(sum(ImageStat.Stat(diff).mean)/3,4)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ART/'delivery/NABO_Toolkit_Grok_Batch1/manifest.json').read_text())
    report={'visual_status':'See review.json for the source-bound manual contact-sheet and endpoint review','clips':[]}
    for clip in manifest['clips']:
        path=VIDEO/clip['output_video']; stem=path.stem
        probe=json.loads(run(['ffprobe','-v','error','-select_streams','v:0',
            '-show_entries','stream=width,height,r_frame_rate,nb_frames,codec_name:format=duration',
            '-of','json',str(path)]))
        stream=probe['streams'][0]; w,h=stream['width'],stream['height']
        numerator,denominator=map(int,stream['r_frame_rate'].split('/'))
        fps=numerator/denominator
        # Decoder consumes the entire stream, including frames not sampled below.
        raw=run(['ffmpeg','-v','error','-i',str(path),'-an','-f','rawvideo','-pix_fmt','rgb24','-'])
        stride=w*h*3; assert len(raw)%stride==0
        count=len(raw)//stride
        assert count==int(stream['nb_frames'])
        samples=[]; boxes=[]; previous=None; motion=[]
        step=max(1,round(fps/4))
        for index in range(count):
            frame=Image.frombytes('RGB',(w,h),raw[index*stride:(index+1)*stride])
            boxes.append(bounds(frame))
            small=frame.resize((180,180),Image.Resampling.BILINEAR)
            if previous is not None: motion.append((difference(previous,small),index))
            previous=small
            if index%step==0 or index==count-1: samples.append((index,frame.copy()))
        cols=5; cell=256; rows=math.ceil(len(samples)/cols)
        sheet=Image.new('RGB',(cols*cell,rows*(cell+28)),(239,235,229)); draw=ImageDraw.Draw(sheet)
        for i,(index,frame) in enumerate(samples):
            x=(i%cols)*cell; y=(i//cols)*(cell+28)
            sheet.paste(frame.resize((cell,cell),Image.Resampling.LANCZOS),(x,y+28))
            draw.text((x+8,y+6),f'{index/fps:.2f}s / frame {index}',font=ImageFont.truetype(FONT,15),fill=(25,35,50))
        sheet.save(OUT/f'{stem}_contact.png')
        first=Image.frombytes('RGB',(w,h),raw[:stride])
        last=Image.frombytes('RGB',(w,h),raw[-stride:])
        first.save(OUT/f'{stem}_first.png'); last.save(OUT/f'{stem}_last.png')
        reference=Image.open(ART/'start'/Path(clip['start_frame']).name).convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
        panel=Image.new('RGB',(960,660),(239,235,229)); draw=ImageDraw.Draw(panel)
        for i,(label,im) in enumerate(zip(('APPROVED INPUT','VIDEO FIRST','VIDEO LAST'),(reference,first,last))):
            x=i*320; draw.text((x+8,8),label,font=ImageFont.truetype(FONT,18),fill=(25,35,50))
            panel.paste(im.resize((320,320),Image.Resampling.LANCZOS),(x,36))
            face=im.crop((round(w*.24),round(h*.05),round(w*.77),round(h*.50)))
            face.thumbnail((320,280),Image.Resampling.LANCZOS)
            panel.paste(face,(x+(320-face.width)//2,376))
        panel.save(OUT/f'{stem}_endpoints.png')
        report['clips'].append({'id':clip['id'],'file':str(path.relative_to(ROOT)),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':w,'height':h,'fps':fps,
            'duration_seconds':float(probe['format']['duration']),'decoded_frames':count,
            'decode':'PASS','loop_requested':clip['loop'],
            'first_last_rgb_mae':difference(first,last),'input_first_rgb_mae':difference(reference,first),
            'frame_bounds':boxes,'largest_adjacent_changes':sorted(motion,reverse=True)[:5],
            'contact_sheet':f'{stem}_contact.png','endpoints':f'{stem}_endpoints.png'})
        print(path.name,count,'frames decoded; first/last MAE',report['clips'][-1]['first_last_rgb_mae'])
        del raw
    (OUT/'metadata.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__': main()
