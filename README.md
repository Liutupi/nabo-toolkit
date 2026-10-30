<p align="right"><a href="README.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# NABO Toolkit

**v0.3.3-ai-dev1 candidate:** a default AI assistant shortcut group uses the [desktop bridge](desktop-bridge/README.md) to open Codex, Claude and Grok Bot; switch to Typeless and trigger dictation manually. Existing personal configurations are not replaced: read the badge first and explicitly add the group on the configurator. NABO artwork remains unchanged. The user confirmed the Mac workflow on the exact new app with a retained personal configuration; fresh-install defaults and Windows remain unverified on hardware.

**v0.3.2-voice-dev4 · experimental public test:** personally enrolled offline voice navigation now covers reading, Douyin, music, cards, camera, screenshot and voice input. Hold bottom OK in the main menu, enroll three examples per target, then briefly press OK to recognize. Voice input only opens Typeless; use its existing key afterwards.213 host checks and the requested bounded device/21-template retention checks passed. Lossless explicit compaction recovered NVS space without changing recorded samples, configuration or bonds. Original NABO art/animations are unchanged. [Release and protected upgrade](docs/RELEASE_v0.3.2-voice-dev4.md) · [Voice guide](docs/VOICE.md) · [Configurator](https://liutupi.github.io/nabo-toolkit/).

This is not general transcription or universal recognition. A real personal-card URL change, restart retention and phone scan passed. Long stability, broad noise/speaker coverage and complete first install remain unverified. Intermittent PC-USB headphone stutter remains unresolved. Community project1701 revision3977 is approved and public; the earlier image and submission evidence is in the [community update record](docs/community/v0.3.2-voice-dev4/README.md). See [all published works by the author](https://ai-passport.folotoy.cn/creators/?id=14101).

[v0.3.2-voice-dev4 is published](https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.2-voice-dev4): all eight assets were independently downloaded without authentication, with37 ZIP members and11 public configuration files matching bytes/SHA. See the [publication record](docs/validation/publication-v0.3.2-voice-dev4.json). The v0.3.1 paragraphs below are historical release/device evidence, not the current community status or a new full validation of v0.3.2.

**v0.3.1-remote-dev2 released on GitHub; community IN REVIEW (2026-10-28)**: source defaults now contain five groups—Screenshot (Esc cancel), Typeless, CapCut, WeRead and Edit. Media first offers Music or Douyin; Music retains volume/playback/track controls, while Douyin sends arrow keys. Screen and editor rows follow the physical top-to-bottom order UP, DOWN, OK. Optional remote display-off starts after 30 seconds without short keys extending that interval; short keys still send, dark-screen long OK only wakes the screen, lit-screen long OK retains its tool action, and long UP still returns. Candidate `0.3.1-remote-dev2` passed127 tests (37 Node+90 Python), zero skips,2,206 steps,3 deliberate mutations and the ESP-IDF6.0.2/F3 build. The fixed app passed authorized app-only installation, verification and reset. A separate USB migration removed only the matching old Douyin group, retained other groups/cards and passed automatic readback plus three further reads. The user accepted media selection, physical row order, display-off, dark-screen page turns and long-OK wake-only behavior on the current setup. Cold-power retention, measured power and the full app/platform matrix remain unverified; GitHub release and public configuration deployment passed verification; the existing community entry was updated/resubmitted and remains IN REVIEW, not public.

Current physical acceptance PASS: the user confirmed media/key order, screen-off, dark page turns and long-OK wake-only; headphones/keyboard were normal in this round. Independent dark-period capture also completed16 HID actions/32 notification transmissions while screen_off remained true and animation frame9 stayed frozen, with zero related errors; wake did not increase sent. This does not resolve the earlier intermittent Bluetooth connection cause or establish all-platform coexistence, and TX completion is not host acknowledgment.

**Published configuration, verified**: the [configuration page](https://liutupi.github.io/nabo-toolkit/) follows the current five-group source. The v0.3.0 packages and old `nabo-toolkit-config-shortcuts-20261028.zip` retain their original six-group snapshots; HANDOFF25 remains historical evidence. Old dev3 needs this version's app for the media picker/display-off features. Reading a personal configuration never deletes groups; default replacement and device writes remain explicit. The earlier102-test/build pass belongs to the shortcut-only candidate, separately from this version's127-test gate. The new Release's8 assets and the configuration site's11 accessible files passed anonymous byte/SHA checks; community public listing is a separate pending review.

[Configuration page](https://liutupi.github.io/nabo-toolkit/) · [Firmware / offline configurator](https://github.com/Liutupi/nabo-toolkit/releases) · [Upgrade instructions](docs/RELEASE_v0.3.1-remote-dev2.md)

**Community update:** existing project1701/mutable revision3928 was updated to v0.3.1-remote-dev2 and resubmitted; status is **IN REVIEW, not public**. The original five images/cover/order are unchanged, verified by individual byte/SHA re-download checks. The saved community firmware re-download is2,077,152 bytes, SHA256 `9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b`, identical to the published GitHub full image. See [current community records](docs/community/v0.3.1-remote-dev2/README.md). Current anonymous community download was not rechecked.

[Historical first-submission records](docs/community/v0.3.0-f3-dev3/README.md) retain v0.3.0 snapshots. Revision3928 is mutable: its firmware href now serves the new binary, so the old size/hash/HTTP401 receipt is not a current download result.

**v0.3.0-f3-dev3 public test release**: exact accepted app1,999,600 bytes, SHA256 `d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`. Build PASS (IDF6.0.2), Host tests PASS (100/1710 full JS-C steps), Device tests PARTIAL PASS (user accepted full welcome, distinct tool animations, startup voice and clean key tones; 240 connected samples, minimum heap92,696/largest77,824 bytes, zero audio errors/crashes). Unverified: repeat final-image USB/power retention, physical boot skip, browser permissions, all hosts/three-slot/sleep/long stability. Historical 3s reconnect FAIL remains; F2 results are historical. See HANDOFF22-23 and validation/f3.json.

Desktop Chrome/Edge + USB: Connect → Read current configuration → Edit → Write and verify. The top Cards / Wi-Fi link opens card editing. Browser Save only saves local edits. Extract the offline ZIP and open config.html; no development tools required. Wi-Fi QR codes contain the password and let a phone join that network; the badge itself stays offline. No configuration upload or analytics service.

The candidate's display-off switch uses independent NVS `remote_v1`; it does not migrate/erase existing settings or bonds. The authorized configuration migration deliberately saved the five retained groups to `cfg_v1`. General default replacement still requires reading the badge first and explicitly writing/verifying; a configuration-only update cannot add the new media/display features to old dev3 firmware. Current connection readiness and telemetry do not establish the cause of the Windows Bluetooth fault or full coexistence acceptance.

![Host preview from the actual C renderer, not an LCD photograph](docs/images/f3/overview.png)

**Data-preserving app-only upgrade at0x10000**. Tested legacy factory0x10000/0x1f0000 and FAT assets0x200000/0x600000 differ from build defaults. Do not use default idf.py flash, community full images or whole-chip erase to preserve data. A separately authorized community first-install image is now available:0x0, replacing partition table/NVS/settings/bonds, full-install path not device-tested. See [installation instructions](docs/RELEASE_v0.3.1-remote-dev2.md). Source is [MIT](LICENSE); creative assets are excluded; see [notices](NOTICE.md).

## Earlier F2 checkpoint (historical)

An offline Bluetooth HID remote for the FoloToy AI Passport (ESP32-C3): presentation controls, meeting shortcuts, media, camera shutter, configurable shortcuts/Typeless and QR contact cards.

Historical checkpoint: **F2 dev2 installed app-only;87 host tests,1710 full JS–C steps and ESP-IDF6.0.2 builds pass.** Actual USB save/readback/rejections/two warm resets/20 reads pass and original configuration is restored. Windows re-pairing/paste/volume/connected memory pass; configured text/card/QR and committed-save cold power retention pass, prior3s FAIL retained. Firmware uses static placeholders; existing animations/full startup visuals/sound still require F3. See HANDOFF21.

Read [handoff](docs/HANDOFF.md), [firmware plan](game-art/toolkit/FIRMWARE_PLAN.md), [UI design](game-art/toolkit/UI_DESIGN.md) and [validation](docs/VALIDATION.md). Maintenance rules: `AGENTS.md`.

```sh
python3 -m http.server 8770 --directory game-art/toolkit/prototype
./tools/validate.sh --static
# Activate ESP-IDF 6.0.2 before the complete build gate:
./tools/validate.sh --f3
# Native Windows PowerShell: ./tools/validate.ps1 -Stage F3
```

The browser prototype simulates HID. [F2 configuration](docs/CONFIGURATION.md) covers schema/USB protocol; [firmware](firmware/README.md) retains F0 controls; [host tests](tests/README.md) and [sprites](game-art/toolkit/sprites/README.md) document validation/provenance. Original art/video remains unchanged.

No flashing, Git commit/push or publishing occurs during validation. This project is not affiliated with FoloToy. NABO imagery and art assets are not licensed with the source code; reused BSP licensing is retained separately.

[Windows continuation](docs/WINDOWS_CONTINUE.md) · Current asset inventory:368 files/93,040,985 bytes, including the community cover; the original364 source/intermediate/runtime files remain unchanged.
