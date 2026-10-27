#!/usr/bin/env python3
"""Verify a public release and Pages downloads without authentication."""
import argparse
import hashlib
import json
from pathlib import Path
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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--version', required=True)
    ap.add_argument('--commit', required=True)
    ap.add_argument('--site', action='store_true')
    args = ap.parse_args()
    api = 'https://api.github.com/repos/' + REPO
    repo = json.loads(get(api))
    if repo['private'] or repo['visibility'] != 'public':
        raise ValueError('Repository is not public')
    release = json.loads(get(api + '/releases/tags/' + args.version))
    if release['draft'] or not release['prerelease'] or release['tag_name'] != args.version:
        raise ValueError('Unexpected release metadata')
    ref = json.loads(get(api + '/git/ref/tags/' + args.version))['object']
    if ref['type'] == 'tag':
        ref = json.loads(get(ref['url']))['object']
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
    for line in (target / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
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
              'tag_commit': ref['sha'], 'authorization_header_used': False,
              'public_downloads': entries, 'zip_members_verified': len(names),
              'accepted_app_sha256': manifest['app']['sha256'], 'merged_image_published': False,
              'device_readbacks_published': False, 'status': 'PASS'}
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
    (target / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
