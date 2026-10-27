"""Bounded indexed sprite format: 64 RGB565 colors, row RLE and delta rows."""
import struct
import zlib

MAGIC=b'TKSPR1\0\0'
HEADER=struct.Struct('<8s4H2I')
ENTRY=struct.Struct('<5I')


def row_encode(row,previous=None):
    out=bytearray(); i=0
    while i<len(row):
        if previous is not None and row[i]==previous[i]:
            n=1
            while n<128 and i+n<len(row) and row[i+n]==previous[i+n]: n+=1
            out.append(128+n-1); i+=n; continue
        n=1
        if previous is None:
            while n<128 and i+n<len(row) and row[i+n]==row[i]: n+=1
            if n>=3: out.extend((128+n-1,row[i])); i+=n; continue
        start=i; i+=1
        while i-start<128 and i<len(row):
            if previous is not None and row[i]==previous[i]: break
            if previous is None and i+2<len(row) and row[i]==row[i+1]==row[i+2]: break
            i+=1
        out.append(i-start-1); out.extend(row[start:i])
    return bytes(out)


def frame_encode(frame,w,h,previous=None):
    rows=[row_encode(frame[y*w:(y+1)*w],None if previous is None else previous[y*w:(y+1)*w]) for y in range(h)]
    offset=(h+1)*4; offsets=[offset]
    for row in rows: offset+=len(row); offsets.append(offset)
    return struct.pack('<'+str(h+1)+'I',*offsets)+b''.join(rows)


def encode(frames,w,h,palette,times,duration,loop=False,all_keys=False):
    if not frames or len(frames)!=len(times) or len(palette)!=64: raise ValueError('frame/palette count')
    if not 1<=w<=256 or not 1<=h<=256 or len(frames)>64: raise ValueError('dimensions')
    if times[0]!=0 or any(a>=b for a,b in zip(times,times[1:])) or times[-1]>=duration: raise ValueError('timestamps')
    chunks=[]; entries=[]; offset=HEADER.size+128+len(frames)*ENTRY.size
    for i,frame in enumerate(frames):
        if len(frame)!=w*h or max(frame)>=64: raise ValueError('indexed pixels')
        key=frame_encode(frame,w,h)
        delta=frame_encode(frame,w,h,frames[i-1]) if i and not all_keys else None
        is_key=delta is None or len(key)<=len(delta)
        payload=key if is_key else delta
        entries.append((times[i],offset,len(payload),zlib.crc32(frame),int(is_key)))
        chunks.append(payload); offset+=len(payload)
    return HEADER.pack(MAGIC,w,h,len(frames),64,duration,int(loop))+struct.pack('<64H',*palette)+b''.join(ENTRY.pack(*e) for e in entries)+b''.join(chunks)


def decode(data):
    if len(data)<HEADER.size+128: raise ValueError('short header')
    magic,w,h,count,colors,duration,loop=HEADER.unpack_from(data)
    if magic!=MAGIC or colors!=64 or not 1<=w<=256 or not 1<=h<=256 or not 1<=count<=64 or loop>1: raise ValueError('header')
    table_end=HEADER.size+128+count*ENTRY.size
    if len(data)<table_end: raise ValueError('short index')
    palette=struct.unpack_from('<64H',data,HEADER.size)
    frames=[]; times=[]; expected=table_end
    for i in range(count):
        at,offset,length,crc,key=ENTRY.unpack_from(data,HEADER.size+128+i*ENTRY.size)
        if offset!=expected or offset+length>len(data) or key>1 or (not i and not key) or (not i and at) or (i and at<=times[-1]) or at>=duration: raise ValueError('index')
        payload=data[offset:offset+length]; expected=offset+length
        if len(payload)<4*(h+1): raise ValueError('row index')
        rows=struct.unpack_from('<'+str(h+1)+'I',payload)
        if rows[0]!=4*(h+1) or rows[-1]!=length: raise ValueError('row offsets')
        current=bytearray(w*h) if key else bytearray(frames[-1])
        for y in range(h):
            pos,end=rows[y:y+2]; x=0
            if pos>end or end>length: raise ValueError('row bounds')
            while pos<end:
                header=payload[pos]; pos+=1; n=(header&127)+1
                if x+n>w: raise ValueError('row overflow')
                if header&128:
                    if key:
                        if pos>=end: raise ValueError('short run')
                        value=payload[pos]; pos+=1
                        if value>=64: raise ValueError('palette index')
                        current[y*w+x:y*w+x+n]=bytes([value])*n
                else:
                    if pos+n>end: raise ValueError('short literal')
                    pixels=payload[pos:pos+n]; pos+=n
                    if max(pixels)>=64: raise ValueError('palette index')
                    current[y*w+x:y*w+x+n]=pixels
                x+=n
            if x!=w: raise ValueError('short row')
        if zlib.crc32(current)!=crc: raise ValueError('frame checksum')
        frames.append(bytes(current)); times.append(at)
    if expected!=len(data): raise ValueError('trailing data')
    return {'w':w,'h':h,'frames':frames,'palette':palette,'times':times,'duration':duration,'loop':bool(loop)}
