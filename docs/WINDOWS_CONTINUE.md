<p align="right"><a href="WINDOWS_CONTINUE.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# Continue on Windows

**Latest (2026-10-28, HANDOFF22-23)**: F3 dev3 installed; 100 host tests/1710 steps/build pass. User accepted full welcome, distinct animated tool costumes, startup voice and clean key tones. Original364 assets unchanged, now367. Public test release/configuration links are in README. IDF6.0.2 and legacy layout protections remain.

Reuse `Liutupi/nabo-toolkit`, main, baseline5fb23a0 and local work. Find existing checkout first, inspect `git status --short --branch`, preserve edits before synchronizing main; clone only if absent. Current increment is uncommitted/unpushed. Do not reset/overwrite it or create a replacement project. Read AGENTS, latest HANDOFF, VALIDATION, FIRMWARE_PLAN and UI_DESIGN.

All364 assets/90,980,640 bytes are present: original images/videos/prompts/scripts/reviews/RGBA/indexed frames/sprites/prototype. No re-upload/regeneration needed. Start with `python tools/verify_assets.py`. Prototype: `python -m http.server 8770 --directory game-art/toolkit/prototype`; HID is simulated, welcome about5.5s/any key skips. Firmware stays offline. Rules/default keys remain authoritative in tk_core.js/tk_hid.js.

Check nabo-passport-game and all five passport skills. Project requires **ESP-IDF6.0.2, ESP32-C3,8MiB,noPSRAM**, overriding generic skill SDK versions. Node, Python and native-loadable C11 host `cc` are required; cross compiler is not a substitute. This host already has the following tools; confirm actual paths elsewhere. Put host compiler on PATH before SDK activation so SDK CMake/Ninja take priority:

```powershell
$env:Path = 'D:\nabo-passport-tools\w64devkit\bin;' + $env:Path
. 'C:\Espressif\esp-idf-v6.0.2\export.ps1'
$env:PYTHONIOENCODING = 'utf-8'
idf.py --version  # ESP-IDF v6.0.2
./tools/validate.ps1 -Stage F3
./tools/validate.ps1 -Static
./tools/validate.ps1 -Stage F0 -FirmwareOnly
```

F2 gate regenerates isolated build/f2 config from `sdkconfig.defaults;sdkconfig.f1.defaults;sdkconfig.f2.defaults`; F0 uses build/f0. Fonts/derived placeholder files are checked-in build inputs: normal build needs no font conversion/Pillow/ffmpeg. Regenerate pinned dependencies, do not copy old SDK/managed_components/build. Native PowerShell gate was actually run. IDF6 does not support MSYS builds; Git Bash is static-only. Linux/WSL can use `./tools/validate.sh --f3` with its own IDF environment; USB access needs separate setup.

If WindowsApps owns python3, map only the static child process:

```powershell
& 'C:\Espressif\tools\git\bin\bash.exe' -c 'python3() { python "$@"; }; export -f python3; bash tools/validate.sh --static'
```

Full gate reconfigures before renderer tests to obtain pinned LVGL headers. Static-only mode explicitly SKIPs renderer tests without headers, which is not a pass. ctypes libraries unload before Windows cleanup. Complete replay covers defaults and F2 custom configuration. RAM providers do not prove actual power-loss/concurrency. `docs/images/f2/overview.png` is a host C screenshot with synthetic peers, not a device photograph. Preview regeneration needs Pillow; font regeneration additionally needs converter1.5.3 and exact existing font inputs identified by firmware/fonts/fonts.json. Normal build needs neither.

Three visible slots keep newest pairings, evict oldest on successful new pairing; ordinary reconnect does not reorder. No repeated FIFO consent needed. Fourth SDK key record is staging only, not a fourth product slot. F0 migration preserves keys and selected identity/OS; friendly-name lookup is not implemented. New-pair windows reject old auto-reconnects; explicitly delete an existing identity's slot before repairing it. Default DisplayOnly Harmony0x404 remains unresolved; optional numeric comparison still requires matching numbers and physical short OK.

Device testing has resumed under explicit F2 authorization. Current fixed app is dev2,49e596ca…3185d57; the badge no longer runs F0. Re-enumerate COM, verify actual device/capacity/legacy layout and fixed archive before another app-only installation. Serial open/reset can restart the badge.

Measured legacy layout: NVS0x9000/0x6000,PHY0xf000/0x1000,factory0x10000/0x1f0000,FAT0x200000/0x600000. Preserve table/NVS/assets; no default flash/merged image/full erase. Dev2 app1859696 bytes ends0x1d6070; erase ends0x1d7000. See validation/f2.json. Shared ADC may wake on any key.

Next: actual browser Web Serial permission/page flow, unplug during transfer and remaining F0/F1 gates. Windows re-pairing/default HID/custom text/card/QR/connected memory/committed-save cold power retention pass; original configuration restored. F3 animation/startup sound remain unimplemented; reuse existing assets. Keep firmware-specific evidence/private data protection; no publication authorization.
