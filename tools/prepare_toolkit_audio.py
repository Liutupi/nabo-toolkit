"""Normalize the approved Dreamina welcome once; never overwrite its original."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import wave
from array import array

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ffmpeg',required=True);args=ap.parse_args()
    src=ROOT/'game-art/toolkit/audio/originals/boot-welcome-dreamina.mp3'
    assert sha(src)=='9080e0c83ae09c12580805eb9f3751bce8805c32710fd5d2f776f715e43c9d0e'
    out=ROOT/'game-art/toolkit/audio/boot-welcome.wav'
    af='atrim=start=0.34:end=2.99,asetpts=PTS-STARTPTS,highpass=f=90,lowpass=f=6500,loudnorm=I=-16:TP=-3:LRA=7,afade=t=in:d=0.01,afade=t=out:st=2.62:d=0.03'
    stamp=hashlib.sha256(af.encode()).hexdigest()[:12]
    candidate=ROOT/f'build/boot-welcome-{stamp}.wav'
    if not candidate.exists():
        subprocess.run([args.ffmpeg,'-hide_banner','-nostdin','-n','-i',str(src),'-af',af,'-ac','1','-ar','16000','-c:a','pcm_s16le',str(candidate)],check=True,capture_output=True)
    out.write_bytes(candidate.read_bytes()) # Rebuild only our normalized derivative.
    with wave.open(str(out)) as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,16000)
        pcm=w.readframes(w.getnframes())
    a=array('h');a.frombytes(pcm);peak=max(map(abs,a));clipped=sum(abs(x)>=32767 for x in a)
    assert peak<32767 and not clipped and len(a)<=43200 and abs(a[-1])<8
    dest=ROOT/'firmware/assets/boot-welcome.pcm';dest.write_bytes(pcm)
    review='PENDING user review';record=out.parent/'generation.json'
    if record.exists():
        previous=json.loads(record.read_text(encoding='utf-8'))
        if previous.get('source_sha256')==sha(src) and previous.get('wav_sha256')==sha(out) and previous.get('filter')==af:review=previous.get('audible_acceptance',review)
    meta={'generator':'Dreamina Canvas TTS','cli_version':'1.0.2','text':'那波，陪你遥控万物！','voice':'阳光小男孩',
        'canvas':'https://jimeng.jianying.com/ai-tool/ai-canvas/981d91a0-7cb3-4f6b-9f40-cac2069c55aa','node_id':'node_kcce8dvk37','resource_id':'5421f4ea-be7c-481e-8705-f43e755a1783',
        'source':src.relative_to(ROOT).as_posix(),'source_sha256':sha(src),'trim_start_seconds':0.34,'duration_seconds':len(a)/16000,'filter':af,
        'runtime':'PCM s16le mono16000Hz; start at1400ms; duck other tones to1/4; any-key skip cancels voice',
        'peak_pcm':peak,'clipped_samples':clipped,'wav_sha256':sha(out),'pcm_sha256':sha(dest),'audible_acceptance':review}
    (out.parent/'generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Welcome PCM: {len(a)/16000:.3f}s, peak{peak}, clipped{clipped}, final{a[-1]}')
if __name__=='__main__':main()
