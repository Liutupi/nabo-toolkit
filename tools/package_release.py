#!/usr/bin/env python3
"""Package an exact accepted app and configurator; never build, flash or publish."""
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


def accepted_version(record):
    version = record.get('version') or record.get('candidate_version')
    if not isinstance(version, str) or not version:
        raise ValueError('Validation record has no firmware version')
    if record.get('version') and record.get('candidate_version') and record['version'] != record['candidate_version']:
        raise ValueError('Validation firmware versions disagree')
    if record.get('build') != 'PASS' or record.get('host_tests', {}).get('status') != 'PASS':
        raise ValueError('Validation build/host gate is not PASS')
    # New candidate records must refer to the exact app already installed and accepted.
    # Historical f3.json uses its original device_tests structure and remains supported.
    if 'candidate_version' in record:
        installed = record.get('device_install', {})
        app = record.get('artifacts', {}).get('nabo-toolkit.bin', {})
        if record.get('candidate_flashed') is not True or installed.get('status') != 'PASS':
            raise ValueError('Candidate app has not passed exact-image installation')
        if installed.get('app_sha256') != app.get('sha256') or installed.get('app_bytes') != app.get('bytes'):
            raise ValueError('Installed candidate identity differs from accepted app')
        device = record.get('device_tests', '')
        status = device.get('status', '') if isinstance(device, dict) else device
        if not isinstance(status, str) or not status.upper().startswith(('PASS', 'PARTIAL PASS')):
            raise ValueError('Candidate physical acceptance is incomplete')
        physical = record.get('physical_acceptance', {}).get('status', '')
        if not isinstance(physical, str) or not physical.upper().startswith('PASS'):
            raise ValueError('Candidate requested behavior has no physical acceptance record')
    return version


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive', type=Path, required=True)
    ap.add_argument('--version', required=True)
    ap.add_argument('--commit', required=True)
    ap.add_argument('--configuration-commit', help='Separate configuration-page commit; firmware tag remains unchanged')
    ap.add_argument('--validation', type=Path, default=ROOT / 'docs/validation/f3.json',
                    help='Accepted device validation JSON (default: docs/validation/f3.json)')
    args = ap.parse_args()
    validation_path = args.validation.resolve()
    validation_name = validation_path.relative_to(ROOT).as_posix()
    if not validation_name.startswith('docs/validation/'):
        raise ValueError('Validation must be a maintained docs/validation record')
    validation_data = validation_path.read_bytes()
    accepted = json.loads(validation_data)
    version = accepted_version(accepted)
    if args.version != 'v' + version:
        raise ValueError('Release version differs from accepted firmware')
    archive = args.archive.resolve()
    subprocess.run([sys.executable, str(ROOT / 'tools/archive_firmware.py'), 'verify', str(archive)], check=True)
    original = json.loads((archive / 'manifest.json').read_text(encoding='utf-8'))
    firmware_commit = subprocess.check_output(['git', 'rev-parse', '--verify', args.commit + '^{commit}'], cwd=ROOT, text=True).strip()
    configuration_commit = subprocess.check_output(['git', 'rev-parse', '--verify',
                                                   (args.configuration_commit or args.commit) + '^{commit}'], cwd=ROOT, text=True).strip()
    for name, sha in original['source_sha256'].items():
        if digest((ROOT / name).read_bytes()) != sha:
            raise ValueError('Accepted firmware source mismatch: ' + name)
        committed = subprocess.check_output(['git', 'show', firmware_commit + ':' + name], cwd=ROOT)
        if digest(committed) != sha:
            raise ValueError('Accepted firmware commit mismatch: ' + name)
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
             'validation.json': validation_data,
             'LICENSE': (ROOT / 'LICENSE').read_bytes(),
             'NOTICE.md': (ROOT / 'NOTICE.md').read_bytes()}
    for name in ('flash_candidate.py', 'verify_firmware.py'):
        files['tools/' + name] = (ROOT / 'firmware/tools' / name).read_bytes()
    # Public desktop bridge source only; never package build output or private settings.
    for name in ('README.md', 'README.zh_CN.md', 'macos/NaboBridge.swift', 'windows/NaboBridge.ps1'):
        files['desktop-bridge/' + name] = (ROOT / 'desktop-bridge' / name).read_bytes()
    for path in sorted((ROOT / 'licenses').glob('*')):
        if path.is_file():
            files['licenses/' + path.name] = path.read_bytes()
    for path in sorted((ROOT / 'build/pages').iterdir()):
        if path.is_file():
            files['configuration/' + path.name] = path.read_bytes()
    members = {name: {'bytes': len(data), 'sha256': digest(data)} for name, data in sorted(files.items())}
    manifest = {'schema': 1, 'version': args.version, 'firmware_version': version,
                'source_commit': firmware_commit, 'configuration_source_commit': configuration_commit,
                'validation_record': {'source': validation_name, 'sha256': digest(validation_data)},
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
