#!/usr/bin/env python3
"""Freeze exact F0 build artifacts and verify their hashes; never flash or publish."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['nabo-toolkit-merged.bin','nabo-toolkit.bin','nabo-toolkit.elf','nabo-toolkit.map',
       'bootloader/bootloader.bin','partition_table/partition-table.bin','flash_args','sdkconfig',
       'project_description.json','flasher_args.json']
def digest(data): return hashlib.sha256(data).hexdigest()
def verify(folder):
    manifest=json.loads((folder/'manifest.json').read_text())
    assert manifest['board']=='ai-passport-nabo' and manifest['sdk']=='v6.0.2'
    for name,expected in manifest['artifacts'].items():
        data=(folder/name).read_bytes()
        assert len(data)==expected['bytes'] and digest(data)==expected['sha256'], f'Artifact mismatch: {name}'
    subprocess.run([sys.executable,str(ROOT/'firmware/tools/verify_firmware.py'),str(folder)],check=True)
    print('Archive: PASS',folder)
    return manifest

def main():
    if len(sys.argv)>1 and sys.argv[1]=='verify':
        verify(Path(sys.argv[2]).resolve());return
    build=Path(sys.argv[1]).resolve()
    desc=json.loads((build/'project_description.json').read_text())
    version=desc['git_revision']
    assert version=='v6.0.2', f'Unexpected IDF {version}'
    sdk=(build/'sdkconfig').read_text()
    for line in ['CONFIG_BT_NIMBLE_MAX_CONNECTIONS=1','CONFIG_BT_NIMBLE_MAX_BONDS=3','CONFIG_BT_NIMBLE_NVS_PERSIST=y',
                 'CONFIG_BT_NIMBLE_ROLE_PERIPHERAL=y','CONFIG_BT_NIMBLE_ROLE_BROADCASTER=y','CONFIG_BT_NIMBLE_MEMPOOL_RUNTIME_ALLOC=y',
                 '# CONFIG_BT_NIMBLE_ROLE_CENTRAL is not set','# CONFIG_BT_NIMBLE_ROLE_OBSERVER is not set',
                 'CONFIG_ESPTOOLPY_FLASHSIZE="8MB"']:
        assert line in sdk, f'Wrong build configuration: {line}'
    symbols=subprocess.check_output([desc['c_compiler'].replace('-gcc','-nm'),str(build/'nabo-toolkit.elf')],text=True)
    names={line.split()[-1] for line in symbols.splitlines() if line.split()}
    assert not names & {'esp_wifi_init','esp_wifi_start','esp_wifi_connect'}, 'Wi-Fi initialization linked'
    key=digest((build/'nabo-toolkit-merged.bin').read_bytes())
    target=ROOT/'build/firmware'/key
    if target.exists(): verify(target);return
    target.mkdir(parents=True)
    artifacts={}
    for name in FILES:
        data=(build/name).read_bytes(); dest=target/name; dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data); artifacts[name]={'sha256':digest(data),'bytes':len(data)}
    sources={}
    for folder in [ROOT/'firmware/main',ROOT/'firmware/components/bsp']:
        for path in sorted(folder.rglob('*')):
            if path.is_file() and not path.name.startswith('._'): sources[str(path.relative_to(ROOT))]=digest(path.read_bytes())
    for name in ['firmware/CMakeLists.txt','firmware/sdkconfig.defaults','firmware/partitions.csv','firmware/dependencies.lock']:
        sources[name]=digest((ROOT/name).read_bytes())
    manifest={'stage':'F0','board':'ai-passport-nabo','sdk':version,'artifacts':artifacts,'source_sha256':sources,
              'wifi_init_symbols':'ABSENT','device_tests':'NOT RUN','unverified':['Mac/Windows/iPhone/Android pairing','Restart reconnect under 3 s',
              'Connected heap >= 60 KiB and largest block >= 30 KiB','Keyboard/volume effects and stuck-key recovery'],
              'flash_policy':'App-only at 0x10000 only after compatible device/partition identification and explicit user approval. Merged image starts at 0x0 and can reset stored data. No erase or readback requirement.'}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    verify(target)
if __name__=='__main__': main()
