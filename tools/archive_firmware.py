#!/usr/bin/env python3
"""Freeze exact Toolkit build artifacts and verify their hashes; never flash or publish."""
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
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
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
    desc=json.loads((build/'project_description.json').read_text(encoding='utf-8'))
    version=desc['git_revision']
    assert version=='v6.0.2', f'Unexpected IDF {version}'
    sdk=(build/'sdkconfig').read_text(encoding='utf-8')
    stage='F3' if 'CONFIG_NABO_TOOLKIT_F3=y' in sdk.splitlines() else 'F2' if 'CONFIG_NABO_TOOLKIT_F2=y' in sdk.splitlines() else 'F1' if 'CONFIG_NABO_TOOLKIT_F1=y' in sdk.splitlines() else 'F0'
    bonds=4 if stage!='F0' else 3
    for line in ['CONFIG_BT_NIMBLE_MAX_CONNECTIONS=1',f'CONFIG_BT_NIMBLE_MAX_BONDS={bonds}','CONFIG_BT_NIMBLE_NVS_PERSIST=y',
                 'CONFIG_BT_NIMBLE_ROLE_PERIPHERAL=y','CONFIG_BT_NIMBLE_ROLE_BROADCASTER=y','CONFIG_BT_NIMBLE_MEMPOOL_RUNTIME_ALLOC=y',
                 '# CONFIG_BT_NIMBLE_ROLE_CENTRAL is not set','# CONFIG_BT_NIMBLE_ROLE_OBSERVER is not set',
                 'CONFIG_ESPTOOLPY_FLASHSIZE="8MB"']:
        assert line in sdk, f'Wrong build configuration: {line}'
    symbols=subprocess.check_output([desc['c_compiler'].replace('-gcc','-nm'),str(build/'nabo-toolkit.elf')],text=True)
    names={line.split()[-1] for line in symbols.splitlines() if line.split()}
    assert not names & {'esp_wifi_init','esp_wifi_start','esp_wifi_connect'}, 'Wi-Fi initialization linked'
    assert (build/'nabo-toolkit.bin').stat().st_size<=0x1f0000, 'App exceeds the measured legacy factory capacity'
    key=digest((build/'nabo-toolkit-merged.bin').read_bytes())
    target=ROOT/'build/firmware'/key
    if target.exists(): verify(target);return
    target.mkdir(parents=True)
    artifacts={}
    for name in FILES:
        data=(build/name).read_bytes(); dest=target/name; dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data); artifacts[name]={'sha256':digest(data),'bytes':len(data)}
    sources={}
    for folder in [ROOT/'firmware/main',ROOT/'firmware/components/bsp',ROOT/'firmware/components/qrcodegen',ROOT/'firmware/fonts',ROOT/'firmware/assets']:
        for path in sorted(folder.rglob('*')):
            if path.is_file() and not path.name.startswith('._'): sources[path.relative_to(ROOT).as_posix()]=digest(path.read_bytes())
    for name in ['firmware/CMakeLists.txt','firmware/sdkconfig.defaults','firmware/partitions.csv','firmware/dependencies.lock']:
        sources[name]=digest((ROOT/name).read_bytes())
    if stage!='F0':sources['firmware/sdkconfig.f1.defaults']=digest((ROOT/'firmware/sdkconfig.f1.defaults').read_bytes())
    if stage in ('F2','F3'):sources['firmware/sdkconfig.f2.defaults']=digest((ROOT/'firmware/sdkconfig.f2.defaults').read_bytes())
    if stage=='F3':sources['firmware/sdkconfig.f3.defaults']=digest((ROOT/'firmware/sdkconfig.f3.defaults').read_bytes())
    if 'CONFIG_NABO_TOOLKIT_VOICE=y' in sdk.splitlines():
        for name in ['features.c','features.h','feature_tables.inc','matcher.c','matcher.h']:
            path=ROOT/'tools/voice_probe'/name
            sources[path.relative_to(ROOT).as_posix()]=digest(path.read_bytes())
    unverified=['Mac/Windows/iPhone/Android pairing','Restart reconnect under 3 s',
                'Connected heap >= 60 KiB and largest block >= 30 KiB','Keyboard/volume effects and stuck-key recovery']
    if stage!='F0':unverified+=['Ten switches across three real devices within 5 s each','PPT/Keynote/camera physical effects',
                              'One hour stability and 50 rapid keys','Sleep/wake and cold-power persistence',
                              'Physical LCD/input/audio acceptance','Animation/voice integration requires later art milestone']
    if stage=='F1':unverified+=['Custom shortcuts/cards require F2']
    if stage in ('F2','F3'):unverified+=['Physical USB Web Serial write/read, actual NVS power-loss/reboot retention and configured HID/QR effects']
    if stage=='F3':unverified+=['Original animations/startup voice/color/frame rate/connected memory and configuration-write memory peak on the actual LCD']
    manifest={'stage':stage,'board':'ai-passport-nabo','sdk':version,'artifacts':artifacts,'source_sha256':sources,
              'wifi_init_symbols':'ABSENT','device_tests':'NOT RUN','unverified':unverified,
              'flash_policy':'App-only at 0x10000 only after compatible device/partition identification and explicit user approval. Merged image starts at 0x0 and can reset stored data. No erase or readback requirement.'}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    verify(target)
if __name__=='__main__': main()
