<p align="right"><a href="README.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# NABO Toolkit

**Unreleased media/display candidate (2026-10-28)**: source defaults now contain five groups—Screenshot (Esc cancel), Typeless, CapCut, WeRead and Edit. Media first offers Music or Douyin; Music retains volume/playback/track controls, while Douyin sends arrow keys. Screen and editor rows follow the physical top-to-bottom order UP, DOWN, OK. Optional remote display-off starts after 30 seconds without short keys extending that interval; short keys still send, long OK only wakes the screen, and long UP still returns. Candidate `0.3.1-remote-dev2` passed the complete gate:127 tests (37 Node+90 Python), zero skips,2,206 steps,3 deliberate mutations and the ESP-IDF6.0.2/F3 build. It is not flashed or published; device migration, dark-screen HID/wake behavior and power consumption remain unverified.

**Published configuration snapshot (HANDOFF25)**: the [online page](https://liutupi.github.io/nabo-toolkit/) still serves f8b8ad8 with six groups, including Douyin. The separately named `nabo-toolkit-config-shortcuts-20261028.zip` matches that snapshot; the original firmware/offline ZIPs retain their publication-time contents. The earlier 102-test/build pass belongs to the shortcut-only candidate, not the media/display candidate. Existing personal six-group configurations remain supported and are never silently deleted or replaced.

[Configuration page](https://liutupi.github.io/nabo-toolkit/) · [Firmware / offline configurator](https://github.com/Liutupi/nabo-toolkit/releases) · [Upgrade instructions](docs/RELEASE_v0.3.0-f3-dev3.md)

Community submission: **project1701/revision3928 submitted and under review; public listing not yet confirmed**. Complete firmware, cover and bilingual six-tool instructions are saved; see [submission/verification records](docs/community/v0.3.0-f3-dev3/README.md).

**v0.3.0-f3-dev3 public test release**: exact accepted app1,999,600 bytes, SHA256 `d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`. Build PASS (IDF6.0.2), Host tests PASS (100/1710 full JS-C steps), Device tests PARTIAL PASS (user accepted full welcome, distinct tool animations, startup voice and clean key tones; 240 connected samples, minimum heap92,696/largest77,824 bytes, zero audio errors/crashes). Unverified: repeat final-image USB/power retention, physical boot skip, browser permissions, all hosts/three-slot/sleep/long stability. Historical 3s reconnect FAIL remains; F2 results are historical. See HANDOFF22-23 and validation/f3.json.

Desktop Chrome/Edge + USB: Connect → Read current configuration → Edit → Write and verify. The top Cards / Wi-Fi link opens card editing. Browser Save only saves local edits. Extract the offline ZIP and open config.html; no development tools required. Wi-Fi QR codes contain the password and let a phone join that network; the badge itself stays offline. No configuration upload or analytics service.

The candidate's display-off switch uses independent NVS `remote_v1`; existing `settings_v1`, `cfg_v1` and Bluetooth bonds are preserved. Applying draft default groups still requires reading the badge first and explicitly writing/verifying. A configuration-only update cannot add the candidate's media picker or display-off behavior to the old dev3 firmware.

![Host preview from the actual C renderer, not an LCD photograph](docs/images/f3/overview.png)

**Data-preserving app-only upgrade at0x10000**. Tested legacy factory0x10000/0x1f0000 and FAT assets0x200000/0x600000 differ from build defaults. Do not use default idf.py flash, community full images or whole-chip erase to preserve data. A separately authorized community first-install image is now available:0x0, replacing partition table/NVS/settings/bonds, full-install path not device-tested. See [installation instructions](docs/RELEASE_v0.3.0-f3-dev3.md). Source is [MIT](LICENSE); creative assets are excluded; see [notices](NOTICE.md).

## Earlier F2 checkpoint (historical)

An offline Bluetooth HID remote for the FoloToy AI Passport (ESP32-C3): presentation controls, meeting shortcuts, media, camera shutter, configurable shortcuts/Typeless and QR contact cards.

Historical checkpoint: **F2 dev2 installed app-only;87 host tests,1710 full JS–C steps and ESP-IDF6.0.2 builds pass.** Actual USB save/readback/rejections/two warm resets/20 reads pass and original configuration is restored. Windows re-pairing/paste/volume/connected memory pass; configured text/card/QR and committed-save cold power retention pass, prior3s FAIL retained. Firmware uses static placeholders; existing animations/full startup visuals/sound still require F3. See HANDOFF21.

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

[Windows continuation](docs/WINDOWS_CONTINUE.md) · Current asset inventory:368 files/93,040,985 bytes, including the community cover; the original364 source/intermediate/runtime files remain unchanged.
