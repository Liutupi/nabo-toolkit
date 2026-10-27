"""Lossless F3 runtime derivatives; original TKS, indexed frames and art stay intact."""
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib
from collections import defaultdict, deque
from toolkit_sprite_codec import decode

ROOT=Path(__file__).resolve().parents[1]
NAMES=['welcome_large','base_avatar','base_bust','macro_bust','ppt_bust','meet_bust','media_bust','cam_bust']

def lz(data):
    """Literal1..128 or match3..130 with LE16 distance<=4096; no entropy tables."""
    positions=defaultdict(deque);out=bytearray();literal=bytearray();i=0
    def flush():
        if literal:
            out.append(len(literal)-1)
            word=sum(v<<(i*6) for i,v in enumerate(literal))
            out.extend(word.to_bytes((len(literal)*6+7)//8,'little'));literal.clear()
    while i<len(data):
        key=data[i:i+3];q=positions[key]
        while q and i-q[0]>4096:q.popleft()
        length=0;distance=0
        if len(key)==3:
            for at in reversed(list(q)[-64:]):
                n=3
                while n<130 and i+n<len(data) and data[at+n]==data[i+n]:n+=1
                if n>length:length=n;distance=i-at
                if n==130:break
        if length>=3:
            flush();out.append(128+(min(length-3,7)<<4)+((distance-1)>>8));out.append((distance-1)&255)
            if length>=10:out.append(length-10)
            step=length
        else:
            literal.append(data[i]);step=1
            if len(literal)==128:flush()
        for at in range(i,i+step):positions[data[at:at+3]].append(at)
        i+=step
    flush();return bytes(out)

def unlz(data,size):
    out=bytearray();i=0
    while i<len(data):
        token=data[i];i+=1
        if token<128:
            n=token+1
            packed=(n*6+7)//8
            if i+packed>len(data):raise ValueError('literal')
            word=int.from_bytes(data[i:i+packed],'little');i+=packed
            if word>>(n*6):raise ValueError('padding')
            out.extend((word>>(j*6))&63 for j in range(n))
        else:
            n=((token>>4)&7)+3
            if i>=len(data):raise ValueError('match')
            distance=((token&15)<<8|data[i])+1;i+=1
            if n==10:
                if i>=len(data):raise ValueError('match length')
                n+=data[i];i+=1
            if not 1<=distance<=min(4096,len(out)):raise ValueError('distance')
            for _ in range(n):out.append(out[-distance])
        if len(out)>size:raise ValueError('overflow')
    if len(out)!=size:raise ValueError('length')
    return bytes(out)

def pack_clip(d):
    chunks=[];entries=[];offset=24+128+20*len(d['frames'])
    for i,frame in enumerate(d['frames']):
        key=lz(frame);delta=lz(bytes(x^y for x,y in zip(frame,d['frames'][i-1]))) if i else None
        is_key=delta is None or len(key)<=len(delta);payload=key if is_key else delta
        decoded=unlz(payload,len(frame))
        if not is_key:decoded=bytes(x^y for x,y in zip(decoded,d['frames'][i-1]))
        assert decoded==frame
        entries.append(struct.pack('<5I',d['times'][i],offset,len(payload),zlib.crc32(frame),int(is_key)))
        chunks.append(payload);offset+=len(payload)
    return struct.pack('<8s4H2I',b'TKANI1\0\0',d['w'],d['h'],len(chunks),64,d['duration'],int(d['loop']))+struct.pack('<64H',*d['palette'])+b''.join(entries)+b''.join(chunks)

def compact_font():
    source=ROOT/'firmware/fonts/tk_font_cjk.c';text=source.read_text(encoding='utf-8')
    pattern=r'static const lv_font_fmt_txt_glyph_dsc_t glyph_dsc\[\] = \{(.*?)\n\};'
    match=re.search(pattern,text,re.S);assert match
    fields=('bitmap_index','adv_w','box_w','box_h','ofs_x','ofs_y');glyphs=[]
    for row in re.findall(r'\{([^{}]+)\}',match[1]):
        values=[int(re.search(r'\.'+f+r'\s*=\s*(-?\d+)',row)[1]) for f in fields]
        offset,adv,w,h,x,y=values
        assert 0<=offset<1<<24 and 0<=adv<65536 and 0<=w<256 and 0<=h<256 and -128<=x<128 and -128<=y<128
        glyphs.append(offset.to_bytes(3,'little')+struct.pack('<HBBbb',adv,w,h,x,y))
    packed=b''.join(glyphs)
    lines=['static const uint8_t compact_glyphs[] = {']
    for i in range(0,len(packed),24):lines.append('    '+','.join(str(v) for v in packed[i:i+24])+',')
    lines.append('};\n')
    lines.append('bool tk_cjk_descriptor(uint32_t id,lv_font_fmt_txt_glyph_dsc_t *out)\n{\n'
                 f'    if(id>={len(glyphs)} || !out)return false;\n'
                 '    const uint8_t *p=compact_glyphs+id*9;\n'
                 '    *out=(lv_font_fmt_txt_glyph_dsc_t){.bitmap_index=(uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16,\n'
                 '        .adv_w=p[3]|(unsigned)p[4]<<8,.box_w=p[5],.box_h=p[6],.ofs_x=(int8_t)p[7],.ofs_y=(int8_t)p[8]};\n'
                 '    return true;\n}\n')
    text=text[:match.start()]+'\n'.join(lines)+text[match.end():]
    text=text.replace('#include "lvgl.h"','#include "lvgl.h"\n#include "tk_cjk_compact.h"')
    text=text.replace('.glyph_dsc = glyph_dsc','.glyph_dsc = NULL')
    text=text.replace('.get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt','.get_glyph_dsc = tk_cjk_get_glyph_dsc')
    text=text.replace('.get_glyph_bitmap = lv_font_get_bitmap_fmt_txt','.get_glyph_bitmap = tk_cjk_get_bitmap')
    dest=ROOT/'firmware/fonts/tk_font_cjk_compact.c';dest.write_text(text,encoding='utf-8',newline='\n')
    return {'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glyphs':len(glyphs)-1,'original_descriptor_bytes':len(glyphs)*16,'compact_descriptor_bytes':len(packed),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}

def main():
    header=16+len(NAMES)*8;offset=header;entries=[];chunks=[];meta={'format':'TKAB1/TKANI1, key or XOR, bounded LZ4096','clips':{}}
    for name in NAMES:
        p=ROOT/f'game-art/toolkit/sprites/bin/{name}.tks';d=decode(p.read_bytes());payload=pack_clip(d)
        entries.append(struct.pack('<2I',offset,len(payload)));offset+=len(payload);chunks.append(payload)
        meta['clips'][name]={'source':p.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frames':len(d['frames']),'bytes':len(payload),'decoded_pixel_differences':0}
    blob=b'TKAB1\0\0\0'+struct.pack('<2I',len(NAMES),offset)+b''.join(entries)+b''.join(chunks)
    dest=ROOT/'firmware/assets/animations.bin';dest.write_bytes(blob)
    (dest.parent/'runtime.h').write_text('#pragma once\n#define TK_ANIMATION_BANK_BYTES '+str(len(blob))+'u\n',encoding='utf-8',newline='\n')
    meta.update(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),font=compact_font())
    (dest.parent/'runtime.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Runtime sprites {len(blob)} bytes; original frames unchanged; font descriptors save {meta["font"]["original_descriptor_bytes"]-meta["font"]["compact_descriptor_bytes"]} bytes')
if __name__=='__main__':main()
