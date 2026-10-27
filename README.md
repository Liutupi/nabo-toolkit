<p align="right"><a href="README.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# NABO Toolkit

[Configuration page](https://liutupi.github.io/nabo-toolkit/) · [Firmware / offline configurator](https://github.com/Liutupi/nabo-toolkit/releases) · [Upgrade instructions](docs/RELEASE_v0.3.0-f3-dev3.md)

**v0.3.0-f3-dev3 public test release**: exact accepted app1,999,600 bytes, SHA256 `d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`. Build PASS (IDF6.0.2), Host tests PASS (100/1710 full JS-C steps), Device tests PARTIAL PASS (user accepted full welcome, distinct tool animations, startup voice and clean key tones; 240 connected samples, minimum heap92,696/largest77,824 bytes, zero audio errors/crashes). Unverified: repeat final-image USB/power retention, physical boot skip, browser permissions, all hosts/three-slot/sleep/long stability. Historical 3s reconnect FAIL remains; F2 results are historical. See HANDOFF22-23 and validation/f3.json.

Desktop Chrome/Edge + USB: Connect → Read current configuration → Edit → Write and verify. The top Cards / Wi-Fi link opens card editing. Browser Save only saves local edits. Extract the offline ZIP and open config.html; no development tools required. Wi-Fi QR codes contain the password and let a phone join that network; the badge itself stays offline. No configuration upload or analytics service.

![Host preview from the actual C renderer, not an LCD photograph](docs/images/f3/overview.png)

**App-only upgrade at0x10000**. Tested legacy factory0x10000/0x1f0000 and FAT assets0x200000/0x600000 differ from build defaults. Do not use default idf.py flash, merged images or whole-chip erase. No first-install image is provided. Source is [MIT](LICENSE); creative assets are excluded; see [notices](NOTICE.md).

## Earlier F2 checkpoint (historical)

An offline Bluetooth HID remote for the FoloToy AI Passport (ESP32-C3): presentation controls, meeting shortcuts, media, camera shutter, configurable shortcuts/Typeless and QR contact cards.

Current checkpoint: **F2 dev2 installed app-only;87 host tests,1710 full JS–C steps and ESP-IDF6.0.2 builds pass.** Actual USB save/readback/rejections/two warm resets/20 reads pass and original configuration is restored. Windows re-pairing/paste/volume/connected memory pass; configured text/card/QR and committed-save cold power retention pass, prior3s FAIL retained. Firmware uses static placeholders; existing animations/full startup visuals/sound still require F3. See HANDOFF21.

Read [handoff](docs/HANDOFF.md), [firmware plan](game-art/toolkit/FIRMWARE_PLAN.md), [UI design](game-art/toolkit/UI_DESIGN.md) and [validation](docs/VALIDATION.md). Maintenance rules: `AGENTS.md`.

```sh
python3 -m http.server 8770 --directory game-art/toolkit/prototype
./tools/validate.sh --static
# Activate ESP-IDF 6.0.2 before the complete build gate:
./tools/validate.sh --f2
# Native Windows PowerShell: ./tools/validate.ps1 -Stage F2
```

The browser prototype simulates HID. [F2 configuration](docs/CONFIGURATION.md) covers schema/USB protocol; [firmware](firmware/README.md) retains F0 controls; [host tests](tests/README.md) and [sprites](game-art/toolkit/sprites/README.md) document validation/provenance. Original art/video remains unchanged.

No flashing, Git commit/push or publishing occurs during validation. This project is not affiliated with FoloToy. NABO imagery and art assets are not licensed with the source code; reused BSP licensing is retained separately.

[Windows continuation](docs/WINDOWS_CONTINUE.md) · `python tools/verify_assets.py` checks all 364 source/intermediate/runtime asset files.
