#!/usr/bin/env python3
"""Verify anonymous public downloads; GitHub metadata can fall back to gh on rate limits."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Liutupi/nabo-toolkit'


def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'NABO-public-verification', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 200:
            raise ValueError(f'HTTP {response.status}: {url}')
        return response.read()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def github_metadata(url, authenticated_fallbacks):
    repository_api = 'https://api.github.com/repos/' + REPO
    if url != repository_api and not url.startswith(repository_api + '/'):
        raise ValueError('Unexpected GitHub metadata destination')
    try:
        return json.loads(get(url))
    except urllib.error.HTTPError as error:
        if error.code not in (403, 429):
            raise
        # Metadata only. Asset and Pages downloads always keep the anonymous get() path.
        data = subprocess.check_output(['gh', 'api', url], text=True, encoding='utf-8')
        authenticated_fallbacks.append({'url': url, 'anonymous_http': error.code})
        return json.loads(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--version', required=True)
    ap.add_argument('--commit', required=True)
    ap.add_argument('--site', action='store_true')
    ap.add_argument('--validation', type=Path, help='Also compare uploaded validation.json with this accepted local record')
    ap.add_argument('--report', type=Path, help='Optional verification report destination')
    args = ap.parse_args()
    metadata_fallbacks = []
    api = 'https://api.github.com/repos/' + REPO
    repo = github_metadata(api, metadata_fallbacks)
    if repo['private'] or repo['visibility'] != 'public':
        raise ValueError('Repository is not public')
    release = github_metadata(api + '/releases/tags/' + args.version, metadata_fallbacks)
    if release['draft'] or not release['prerelease'] or release['tag_name'] != args.version:
        raise ValueError('Unexpected release metadata')
    ref = github_metadata(api + '/git/ref/tags/' + args.version, metadata_fallbacks)['object']
    if ref['type'] == 'tag':
        ref = github_metadata(ref['url'], metadata_fallbacks)['object']
    if ref['type'] != 'commit' or ref['sha'] != args.commit:
        raise ValueError('Tag does not target accepted source commit')
    local = ROOT / 'build/release' / args.version
    target = ROOT / 'build/public-verification' / args.version
    target.mkdir(parents=True, exist_ok=True)
    expected = {p.name for p in local.iterdir() if p.is_file()}
    if {a['name'] for a in release['assets']} != expected:
        raise ValueError('Release asset membership differs')
    entries = {}
    for asset in release['assets']:
        name = asset['name']
        data = get(asset['browser_download_url'])
        if data != (local / name).read_bytes() or len(data) != asset['size']:
            raise ValueError('Public asset mismatch: ' + name)
        (target / name).write_bytes(data)
        entries[name] = {'bytes': len(data), 'sha256': digest(data), 'url': asset['browser_download_url'], 'http': 200}
    for checksums in sorted(target.glob('*SHA256SUMS.txt')):
        for line in checksums.read_text(encoding='utf-8').splitlines():
            sha, name = line.split('  ', 1)
            if sha != digest((target / name).read_bytes()):
                raise ValueError('Downloaded checksum mismatch: ' + name)
    manifest = json.loads((target / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['source_commit'] != args.commit:
        raise ValueError('Manifest source commit differs')
    package_name = 'nabo-toolkit-' + args.version + '.zip'
    with zipfile.ZipFile(target / package_name) as package:
        names = set(package.namelist())
        if names != set(manifest['members']) | {'manifest.json', 'SHA256SUMS.txt'}:
            raise ValueError('Unexpected ZIP members')
        if package.read('manifest.json') != (target / 'manifest.json').read_bytes():
            raise ValueError('Inner/outer manifest mismatch')
        if package.read('nabo-toolkit-app.bin') != (target / 'nabo-toolkit-app.bin').read_bytes():
            raise ValueError('Inner/outer application mismatch')
        validation_data = package.read('validation.json')
        validation = json.loads(validation_data)
        validated_version = validation.get('version') or validation.get('candidate_version')
        if not isinstance(validated_version, str) or validated_version != manifest['firmware_version'] or 'v' + validated_version != args.version:
            raise ValueError('Packaged validation firmware version differs')
        if manifest.get('validation_record', {}).get('sha256', digest(validation_data)) != digest(validation_data):
            raise ValueError('Packaged validation identity differs')
        if args.validation and validation_data != args.validation.read_bytes():
            raise ValueError('Packaged validation differs from requested accepted record')
        for name, identity in manifest['members'].items():
            data = package.read(name)
            if len(data) != identity['bytes'] or digest(data) != identity['sha256']:
                raise ValueError('ZIP member mismatch: ' + name)
        for line in package.read('SHA256SUMS.txt').decode('utf-8').splitlines():
            sha, name = line.split('  ', 1)
            if digest(package.read(name)) != sha:
                raise ValueError('Inner checksum mismatch: ' + name)
        if {n for n in names if n.endswith('.bin')} != {'nabo-toolkit-app.bin'}:
            raise ValueError('Unexpected firmware/device readback')
        if any(n.startswith(('private/', 'build/')) or '..' in n.split('/') for n in names):
            raise ValueError('Private or unsafe ZIP path')
        with zipfile.ZipFile(target / 'nabo-toolkit-config-offline.zip') as config:
            if {'configuration/' + n for n in config.namelist()} != {n for n in names if n.startswith('configuration/')}:
                raise ValueError('Configuration ZIP membership mismatch')
            for name in config.namelist():
                if config.read(name) != package.read('configuration/' + name):
                    raise ValueError('Offline configuration differs')
    report = {'date': '2026-10-28', 'repo': repo['html_url'], 'visibility': 'PUBLIC',
              'release': release['html_url'], 'version': args.version, 'prerelease': True,
              'source_commit': args.commit, 'configuration_source_commit': manifest.get('configuration_source_commit', args.commit),
              'tag_commit': ref['sha'], 'authorization_header_used': bool(metadata_fallbacks),
              'download_authorization_header_used': False,
              'anonymous_release_asset_downloads': True,
              'github_metadata': {'authenticated_cli_fallback_used': bool(metadata_fallbacks),
                                  'fallbacks': metadata_fallbacks},
              'public_downloads': entries, 'zip_members_verified': len(names),
              'validation_firmware_version': validated_version,
              'validation_sha256': digest(validation_data), 'unverified': manifest['unverified'],
              'accepted_app_sha256': manifest['app']['sha256'], 'merged_image_published': False,
              'device_readbacks_published': False, 'status': 'PASS'}
    if (target / 'community-manifest.json').exists():
        community = json.loads((target / 'community-manifest.json').read_text(encoding='utf-8'))
        data = (target / community['image']['file']).read_bytes()
        if digest(data) != community['image']['sha256'] or data[0x10000:] != (target / 'nabo-toolkit-app.bin').read_bytes():
            raise ValueError('Community full image differs from fixed build/accepted app')
        if data[0x9000:0x10000] != b'\xff' * 0x7000:
            raise ValueError('Community image contains unexpected NVS/PHY content')
        report['merged_image_published'] = True
        report['community_first_install'] = community
    if args.site:
        base = 'https://liutupi.github.io/nabo-toolkit/'
        site_manifest_data = get(base + 'site-manifest.json')
        site_manifest = json.loads(site_manifest_data)
        if site_manifest != json.loads((ROOT / 'build/pages/site-manifest.json').read_text(encoding='utf-8')):
            raise ValueError('Site manifest content differs')
        checked = []
        for name, identity in site_manifest['files'].items():
            if name == '.nojekyll':
                continue  # Build control file, not a browser dependency.
            data = get(base + name)
            if data != (ROOT / 'build/pages' / name).read_bytes() or digest(data) != identity['sha256']:
                raise ValueError('Site file differs: ' + name)
            checked.append(name)
        report['site'] = {'url': base, 'manifest_http': 200, 'files_http_200_sha256_match': checked,
                          'browser_physical_serial_permission': 'UNVERIFIED'}
    destination = args.report or target / 'verification.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
