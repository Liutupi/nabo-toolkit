#!/usr/bin/env python3
"""Check that every versioned art source, intermediate and runtime asset is present."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'docs/validation/assets.json'
FOLDERS=['game-art/toolkit/art/','game-art/toolkit/sprites/','game-art/toolkit/prototype/assets/','game-art/toolkit/audio/']
def files():
    raw=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z','--',*FOLDERS],cwd=ROOT)
    return sorted(set(p for p in raw.decode().split('\0') if p and not Path(p).name.startswith('._')))
def entry(name):
    data=(ROOT/name).read_bytes()
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
if '--write' in sys.argv:
    manifest={'version':1,'files':{name:entry(name) for name in files()}}
    INDEX.parent.mkdir(exist_ok=True)
    INDEX.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
else:
    manifest=json.loads(INDEX.read_text(encoding='utf8'))
    assert set(files())==set(manifest['files']), 'Asset inventory changed; review and regenerate with --write'
    for name,expected in manifest['files'].items():assert entry(name)==expected, f'Missing or changed: {name}'
print(f"Asset inventory: PASS ({len(manifest['files'])} files, {sum(x['bytes'] for x in manifest['files'].values()):,} bytes)")
