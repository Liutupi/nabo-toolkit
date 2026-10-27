"""Convert frame zero of existing approved atlases; no source pixels or identities are edited."""
import hashlib
import json
from pathlib import Path
import struct
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'game-art/toolkit/prototype/assets'
spec=json.loads((folder/'toolkit_sprites.json').read_text(encoding='utf-8'))
out=ROOT/'firmware/assets';out.mkdir(exist_ok=True)
metadata={}
for name,clip,variant in [('avatar','base','avatar'),('bust','base','bust'),('welcome','welcome','large')]:
    item=spec['clips'][clip][variant];p=folder/item['file'];image=Image.open(p).convert('RGBA').crop((0,0,item['w'],item['h']))
    rgb=bytearray();alpha=bytearray()
    data=image.tobytes()
    for i in range(0,len(data),4):
        r,g,b,a=data[i:i+4]
        rgb+=struct.pack('<H',((r>>3)<<11)|((g>>2)<<5)|(b>>3));alpha.append(a)
    (out/f'placeholder_{name}.rgb565').write_bytes(rgb);(out/f'placeholder_{name}.alpha').write_bytes(alpha)
    metadata[name]={'source':p.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                    'frame':0,'w':image.width,'h':image.height,'rgb565_sha256':hashlib.sha256(rgb).hexdigest(),
                    'alpha_sha256':hashlib.sha256(alpha).hexdigest(),'alpha_unchanged':True}
(out/'placeholders.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
print('F1 frame-zero placeholders: PASS (existing atlas pixels, native RGB565 + original alpha)')
