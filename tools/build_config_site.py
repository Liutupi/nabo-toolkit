#!/usr/bin/env python3
"""Build the public config site and offline ZIP from an explicit file allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ('tk_hid.js', 'tk_config_schema.js', 'tk_core.js',
           'tk_config_serial.js', 'config.js')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/pages')
    parser.add_argument('--zip', type=Path, default=ROOT / 'build/config/nabo-toolkit-config-offline.zip')
    args = parser.parse_args()
    target = args.output.resolve()
    # Only create a new output or reuse an output owned by this builder.
    if target.exists() and any(target.iterdir()) and not (target / 'site-manifest.json').exists():
        raise ValueError('Refusing a nonempty output not owned by this builder')
    target.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'game-art/toolkit/prototype'
    files = {name: (source / name).read_bytes() for name in ('config.html',) + SCRIPTS}
    portrait = ROOT / 'game-art/toolkit/sprites/master/base/00.png'
    html = files['config.html'].decode('utf-8')
    if html.count('../sprites/master/base/00.png') != 1:
        raise ValueError('Expected the approved original NABO portrait exactly once')
    files['config.html'] = html.replace('../sprites/master/base/00.png', 'nabo.png').encode('utf-8')
    files['nabo.png'] = portrait.read_bytes()
    files['index.html'] = files['config.html']
    files['.nojekyll'] = b''
    files['LICENSE'] = (ROOT / 'LICENSE').read_bytes()
    files['NOTICE.md'] = (ROOT / 'NOTICE.md').read_bytes()
    files['README.txt'] = (
        'NABO 工具箱配置\n\n'
        '解压整个 ZIP，在电脑 Chrome/Edge 打开 config.html。无需安装 Node、Python 或 ESP-IDF。\n'
        '用 USB 数据线连接工牌，点“连接工牌”选择串口，再“从工牌读回”。\n'
        '修改后点“写入工牌并核对”，显示核对一致才表示工牌保存成功。\n'
        '“保存到浏览器”只保存本机编辑内容，不修改工牌。\n'
        '名片在快捷键分组下方，也可点顶部“名片 / Wi-Fi 二维码”直达。\n'
        'Wi-Fi 二维码供手机扫码，工牌不联网；密码包含在二维码和导出配置中。\n'
        '网页：https://liutupi.github.io/nabo-toolkit/\n'
        '固件：https://github.com/Liutupi/nabo-toolkit/releases\n'
    ).encode('utf-8')
    # Remove only previously recorded generated files, never recurse outside target.
    previous = target / 'site-manifest.json'
    if previous.exists():
        for name in json.loads(previous.read_text(encoding='utf-8'))['files']:
            path = target / name
            if path.parent != target or not path.is_file():
                raise ValueError('Unexpected previous output')
            if name not in files:
                path.unlink()
    entries = {}
    for name, data in sorted(files.items()):
        (target / name).write_bytes(data)
        entries[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    manifest = {'schema': 1, 'entry': 'index.html', 'offline_entry': 'config.html',
                'portrait_source': portrait.relative_to(ROOT).as_posix(), 'files': entries}
    (target / 'site-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    args.zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(target.iterdir()):
            if not path.is_file() or path.is_symlink():
                raise ValueError('Unexpected site member')
            info = zipfile.ZipInfo(path.name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(f'Config site: {len(entries)} files + manifest; offline ZIP: {args.zip.stat().st_size} bytes')


if __name__ == '__main__':
    main()
