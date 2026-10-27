#!/bin/sh
# Project gate: host contracts, then isolated ESP-IDF F0 build and verified archive.
set -eu
TK_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$TK_ROOT"
TK_MODE=${1:-all}
case "$TK_MODE" in all|--static|--firmware) ;; *) echo 'Usage: tools/validate.sh [--static|--firmware]' >&2; exit 2;; esac
if [ "$TK_MODE" != --firmware ]; then
    node --test tests/tk_golden/model.test.js tests/tk_golden/prototype.test.js
    python3 -m unittest discover -s tests -p 'test_*.py' -v
    python3 tools/verify_golden.py
    git diff --check
fi
if [ "$TK_MODE" != --static ]; then
    idf.py --version | rg '^ESP-IDF v6\.0\.2$'
    mkdir -p "$TK_ROOT/build/f0"
    rm -f "$TK_ROOT/build/f0/sdkconfig" "$TK_ROOT/build/f0/sdkconfig.old"
    # New SDK config comes only from tracked defaults; managed dependencies stay pinned.
    idf.py -C firmware -B "$TK_ROOT/build/f0" -D SDKCONFIG="$TK_ROOT/build/f0/sdkconfig" reconfigure
    # macOS external-volume AppleDouble files must never enter LVGL's C source glob.
    find firmware/managed_components -name '._*' -delete
    idf.py -C firmware -B "$TK_ROOT/build/f0" build
    idf.py -C firmware -B "$TK_ROOT/build/f0" merge-bin -o nabo-toolkit-merged.bin
    python3 firmware/tools/verify_firmware.py "$TK_ROOT/build/f0"
    python3 tools/archive_firmware.py "$TK_ROOT/build/f0"
fi
