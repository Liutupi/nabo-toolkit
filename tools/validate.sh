#!/bin/sh
# Project gate: host contracts, then an isolated F0 or F1 build and verified archive.
set -eu
TK_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$TK_ROOT"
TK_MODE=${1:-all}
case "$TK_MODE" in all|--static|--firmware|--f1|--f1-firmware|--f2|--f2-firmware|--f3|--f3-firmware) ;; *) echo 'Usage: tools/validate.sh [--static|--firmware|--f1|--f1-firmware|--f2|--f2-firmware|--f3|--f3-firmware]' >&2; exit 2;; esac
TK_STAGE=f0
case "$TK_MODE" in --f1|--f1-firmware) TK_STAGE=f1;; --f2|--f2-firmware) TK_STAGE=f2;; --f3|--f3-firmware) TK_STAGE=f3;; esac
TK_IDF_ROOT=$TK_ROOT
if command -v cygpath >/dev/null 2>&1; then TK_IDF_ROOT=$(cygpath -m "$TK_ROOT"); fi
if [ "$TK_MODE" != --static ]; then
    case "$(uname -s)" in MINGW*|MSYS*) echo 'Use native PowerShell: ./tools/validate.ps1 -Stage F1 (ESP-IDF 6 does not support MSYS builds).' >&2; exit 2;; esac
    idf.py --version | tr -d '\r' | rg '^ESP-IDF v6\.0\.2$'
    mkdir -p "$TK_ROOT/build/$TK_STAGE"
    rm -f "$TK_ROOT/build/$TK_STAGE/sdkconfig" "$TK_ROOT/build/$TK_STAGE/sdkconfig.old"
    # New SDK config comes only from tracked defaults; managed dependencies stay pinned.
    TK_DEFAULTS=sdkconfig.defaults
    if [ "$TK_STAGE" != f0 ]; then TK_DEFAULTS='sdkconfig.defaults;sdkconfig.f1.defaults'; fi
    if [ "$TK_STAGE" = f2 ] || [ "$TK_STAGE" = f3 ]; then TK_DEFAULTS="$TK_DEFAULTS;sdkconfig.f2.defaults"; fi
    if [ "$TK_STAGE" = f3 ]; then TK_DEFAULTS="$TK_DEFAULTS;sdkconfig.f3.defaults"; fi
    idf.py -C firmware -B "$TK_IDF_ROOT/build/$TK_STAGE" -D SDKCONFIG="$TK_IDF_ROOT/build/$TK_STAGE/sdkconfig" -D SDKCONFIG_DEFAULTS="$TK_DEFAULTS" reconfigure
    # macOS external-volume AppleDouble files must never enter LVGL's C source glob.
    find firmware/managed_components -name '._*' -delete
fi
if [ "$TK_MODE" != --firmware ] && [ "$TK_MODE" != --f1-firmware ] && [ "$TK_MODE" != --f2-firmware ] && [ "$TK_MODE" != --f3-firmware ]; then
    # Reconfigure above fetches pinned LVGL headers needed by the native renderer tests.
    python3 tools/verify_assets.py
    node --test tests/tk_golden/model.test.js tests/tk_golden/prototype.test.js tests/tk_golden/config.test.js
    python3 -m unittest discover -s tests -p 'test_*.py' -v
    python3 tools/verify_golden.py
    git diff --check
fi
if [ "$TK_MODE" != --static ]; then
    idf.py -C firmware -B "$TK_IDF_ROOT/build/$TK_STAGE" build
    idf.py -C firmware -B "$TK_IDF_ROOT/build/$TK_STAGE" merge-bin -o nabo-toolkit-merged.bin
    python3 firmware/tools/verify_firmware.py "$TK_IDF_ROOT/build/$TK_STAGE"
    python3 tools/archive_firmware.py "$TK_IDF_ROOT/build/$TK_STAGE"
fi
