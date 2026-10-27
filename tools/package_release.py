#!/usr/bin/env python3
"""Package the exact accepted F3 app and configurator; never build, flash or publish."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive', type=Path, required=True)
    ap.add_argument('--version', required=True)
    ap.add_argument('--commit', required=True)
    ap.add_argument('--configuration-commit', help='Separate configuration-page commit; firmware tag remains unchanged')
    args = ap.parse_args()
    accepted = json.loads((ROOT / 'docs/validation/f3.json').read_text(encoding='utf-8'))
    if args.version != 'v' + accepted['version']:
        raise ValueError('Release version differs from accepted firmware')
    archive = args.archive.resolve()
    subprocess.run([sys.executable, str(ROOT / 'tools/archive_firmware.py'), 'verify', str(archive)], check=True)
    original = json.loads((archive / 'manifest.json').read_text(encoding='utf-8'))
    for name, sha in original['source_sha256'].items():
        if digest((ROOT / name).read_bytes()) != sha:
            raise ValueError('Accepted firmware source mismatch: ' + name)
    app = (archive / 'nabo-toolkit.bin').read_bytes()
    expected = accepted['artifacts']['nabo-toolkit.bin']
    if len(app) != expected['bytes'] or digest(app) != expected['sha256']:
        raise ValueError('Accepted application mismatch')
    if len(app) > 0x1f0000:
        raise ValueError('Legacy factory overflow')
    subprocess.run([sys.executable, str(ROOT / 'tools/build_config_site.py')], check=True)
    output = ROOT / 'build/release' / args.version
    output.mkdir(parents=True, exist_ok=True)
    files = {'nabo-toolkit-app.bin': app,
             'README.md': (ROOT / f'docs/RELEASE_{args.version}.md').read_bytes(),
             'validation.json': (ROOT / 'docs/validation/f3.json').read_bytes(),
             'LICENSE': (ROOT / 'LICENSE').read_bytes(),
             'NOTICE.md': (ROOT / 'NOTICE.md').read_bytes()}
    for name in ('flash_candidate.py', 'verify_firmware.py'):
        files['tools/' + name] = (ROOT / 'firmware/tools' / name).read_bytes()
    for path in sorted((ROOT / 'licenses').glob('*')):
        if path.is_file():
            files['licenses/' + path.name] = path.read_bytes()
    for path in sorted((ROOT / 'build/pages').iterdir()):
        if path.is_file():
            files['configuration/' + path.name] = path.read_bytes()
    members = {name: {'bytes': len(data), 'sha256': digest(data)} for name, data in sorted(files.items())}
    manifest = {'schema': 1, 'version': args.version, 'firmware_version': accepted['version'],
                'source_commit': args.commit, 'configuration_source_commit': args.configuration_commit or args.commit,
                'sdk': 'v6.0.2', 'target': 'esp32c3',
                'board': 'ai-passport-nabo', 'flash_bytes': 8388608, 'psram': False,
                'release_type': 'public test; app-only upgrade',
                'app': {'filename': 'nabo-toolkit-app.bin', **expected, 'offset': '0x10000'},
                'accepted_archive_merged_sha256': original['artifacts']['nabo-toolkit-merged.bin']['sha256'],
                'debug_artifact_identities_not_in_download': {k: original['artifacts'][k] for k in ('nabo-toolkit.elf', 'nabo-toolkit.map')},
                'legacy_factory_bytes': 0x1f0000, 'legacy_factory_remaining': 0x1f0000 - len(app),
                'preserved': ['bootloader', 'partition table', 'NVS', 'PHY', 'assets', 'files if present'],
                'merged_image_included': False, 'device_readbacks_included': False,
                'configuration_url': 'https://liutupi.github.io/nabo-toolkit/',
                'members': members, 'unverified': accepted['unverified']}
    manifest_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    files['manifest.json'] = manifest_data
    files['SHA256SUMS.txt'] = ''.join(f'{digest(data)}  {name}\n' for name, data in sorted(files.items())).encode('utf-8')
    package_name = 'nabo-toolkit-' + args.version + '.zip'
    with zipfile.ZipFile(output / package_name, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    (output / 'nabo-toolkit-app.bin').write_bytes(app)
    (output / 'manifest.json').write_bytes(manifest_data)
    (output / 'nabo-toolkit-config-offline.zip').write_bytes((ROOT / 'build/config/nabo-toolkit-config-offline.zip').read_bytes())
    downloads = ('nabo-toolkit-app.bin', package_name, 'nabo-toolkit-config-offline.zip', 'manifest.json')
    (output / 'SHA256SUMS.txt').write_text(''.join(f'{digest((output / name).read_bytes())}  {name}\n' for name in downloads), encoding='utf-8', newline='\n')
    with zipfile.ZipFile(output / package_name) as package:
        if set(package.namelist()) != set(files):
            raise ValueError('ZIP membership mismatch')
        for name, data in files.items():
            if package.read(name) != data:
                raise ValueError('ZIP member mismatch: ' + name)
    print(f'Release package PASS: {output}, {len(files)} members, exact accepted app')


if __name__ == '__main__':
    main()
