<p align="right"><a href="VALIDATION.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# Validation checkpoint — 2026-10-28

Media/display candidate0.3.1-remote-dev2: **Build PASS; Host tests PASS (127:37 Node+90 Python,2206 steps,3 mutations,zero skips); Device tests NOT RUN; Unverified: candidate hardware/power/config migration and the existing dev3 Windows coexistence cause.** Music/Douyin selection,physical UP/DOWN/OK rows,30-second display-off and dark long-OK-only wake passed host checks. No flash/publication;live page remains the old six groups. See [record](validation/remote-control-v0.3.1.json) and HANDOFF26.

Shortcut update: Build PASS (0.3.1-shortcuts-dev1 candidate,not flashed/published); Host tests PASS (102:29 Node+73 Python,1710 steps); Device config save/three reads on existing dev3 PASS,user accepted screenshot/Esc and reading/Douyin on the current end. Candidate device tests,separate phone/desktop acceptance and new-config cold retention remain unverified. See [record](validation/shortcuts-v0.3.1.json).

Configuration delivery PASS: Pages commit f8b8ad8 deployed;11 accessible files match anonymously over HTTP200/bytes/SHA. Public-browser preset/card-preservation/disconnected-write checks pass. A separately named config-only ZIP plus manifest/checksums supplements the Release;all11 assets anonymously re-downloaded,original8 unchanged. No candidate firmware published. See [delivery verification](validation/shortcuts-publication-20261028.json).

## Community submission verification — 2026-10-28

AI Passport project1701/revision3928 is **submitted and under review; public listing is not confirmed**. Five images, bilingual six-tool/controls/pairing instructions, the [configuration link](https://liutupi.github.io/nabo-toolkit/), and installation boundaries are saved. The user separately authorized the complete first-install image; the author's current badge was not flashed.

- Build: PASS. Reused and reverified the fixed2,065,136-byte complete image, SHA256 `9fa968de2a4837d130188bb9541ec55a67a3f1bd936b01eeeb4b81ea5047ad1c`; embedded app matches accepted dev3.
- Host tests: existing100 tests/1710 steps PASS for that app; publication verification is not a repeat full-install device test.
- Device tests: prior app audio/full welcome/animation PARTIAL PASS; no device flashed this round; complete first install NOT RUN.
- Unverified: public community listing, anonymous revision firmware download (currently HTTP401), complete-install device path and remaining compatibility/reconnect checks. Installation at0x0 changes the partition table and resets NVS/bonds; use app-only upgrade to preserve data.

Authenticated download from the saved current-revision firmware href matched local/GitHub bytes; all8 GitHub assets passed anonymous re-download checks. Asset inventory:368 files/93,040,985 bytes, original364 unchanged. See [community records](community/v0.3.0-f3-dev3/README.md). Subsequent WeRead/Douyin shortcut changes are not part of revision3928.

Initial GitHub/Pages publication PASS (HANDOFF23 stage record): public repository, test Release and NABO configuration page are live. Five assets anonymously re-downloaded,37 ZIP members and11 site files verified. Browser card/Wi-Fi editing/save/reload/portrait checks pass; no serial port opened. Physical browser permission/USB transfer remains unverified. See [publication verification](validation/publication-v0.3.0-f3-dev3.json).

- Build: PASS (F3 dev3, ESP-IDF6.0.2/C3/8MiB/no PSRAM; exact app installed).
- Host tests: PASS (100: 27 Node+73 Python; 1,710 full JS-C steps; zero skips).
- Device tests: PARTIAL PASS. User accepted full welcome, distinct tool costumes/animation, startup voice and clean key sounds. 240 connected samples: minimum heap92,696/largest77,824; audio errors0, crash markers0.
- Unverified: repeat final-image USB/power-retention, physical startup skip, browser permission flow, all hosts, three-slot stress, long stability and sleep. Historical 3s reconnect FAIL remains.

Exact accepted app: 1,999,600 bytes, SHA256 `d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`. Release uses this app only. See HANDOFF22-23 and [machine record](validation/f3.json). F2/dev1 results remain attributed to their own images.

## Historical F2 overview (2026-10-27)

- Build: PASS (F2 dev2,ESP-IDF6.0.2; installed app-only)
- Host tests: PASS (87:27 Node +60 Python;1,710-step full configured JS–C replay)
- Device tests: PARTIAL PASS: actual USB save/readback/rejections/two warm resets/20 reads; Windows re-pairing/paste/volume/connected memory pass; configured text/card/QR/committed-save cold power retention pass.
- Unverified: browser USB permission/unplug during transfer/power cut during commit/remaining F1/F3; prior3s FAIL retained.

Historical F2 details are at the end, HANDOFF21 and `validation/f2.json`. Chronological records below retain historical wording superseded by the latest development checkpoint.

The complete gate `./tools/validate.sh` passed using **ESP-IDF 6.0.2** and an isolated configuration generated from tracked defaults. It includes 18 Node tests, 7 C probe/input tests, 8 sprite-codec tests, 7 flash-guard tests, JS golden determinism, diff whitespace checks, firmware build/merge/layout verification and immutable archive hash verification. SDK version follows this project's FIRMWARE_PLAN rather than the reusable skill's generic 5.5.3 default.

| Historic Mac artifacts (installed) | Bytes | SHA256 |
|---|---:|---|
| F0 app | 643,392 | `ea6789e39fddc8a7063a94d45c6687cf71d61a11eb56c55cb9aa4bcce305074c` |
| Merged | 708,928 | `42b610327eb726941ef93bc4cf9a6caeecdf937b4a91bcebe1d656b8d7f0263b` |
| ELF | 8,540,112 | `70768e4ab69942875fc8d4e83dfec7b1e3fc99fcd99dd295355a3bafd854311f` |
| MAP | 5,738,838 | `2ecc8694beba91a46394ac10d7adbdff0d6c640446aed963a88319bbe8e9c289` |

Exact bundle: `build/firmware/42b610327eb726941ef93bc4cf9a6caeecdf937b4a91bcebe1d656b8d7f0263b/`. It contains the matching app/merged/ELF/MAP, bootloader, partition table, flash arguments and SDK/build metadata. Verify with `python3 tools/archive_firmware.py verify <bundle>`. The app fits the planned 4,128,768-byte factory partition. Generated binaries/debugging files are ignored by Git. Same-image revalidation retains the first verified archive; current default-file comments differ from that original source snapshot, with identical generated SDK configuration and image hashes.

NimBLE: peripheral/broadcaster only, one connection, three bonds, NVS persistence, runtime mempool allocation, DisplayOnly + MITM + secure connections. NVS startup errors do not erase stored data. In IDF 6.0.2 the hidden `ESP_WIFI_ENABLED` capability defaults to true and the BT component depends on Wi-Fi's component; forcing it off through defaults is ineffective. The gate checks that the final ELF contains none of `esp_wifi_init`, `esp_wifi_start`, `esp_wifi_connect`. No Wi-Fi stack is initialized.

F0 implements an independent diagnostic menu/test screen, one saved last peer and Mac/Windows preference. It is not the full model, three-slot UI, boot animation, voice or sleep. `ready_ms` starts at advertising, so boot-to-ready must also be checked against startup timestamps. A failed key-up retries, then disconnects.

| F0 physical gate | Required | Result |
|---|---|---|
| Pairing | Mac, Windows, iPhone, Android; six-digit passkey when requested | Mac/Windows/iPhone PASS; Android pending; fresh iPhone passkey ceremony not independently observed |
| Restart reconnect | Last peer automatically secured/subscribed within 3 s | Windows USB resets: 3/3 automatic reconnects; host upper bounds 2.219/3.125/2.812 s, strict timing gate unverified |
| Connected memory | Idle heap ≥60 KiB; largest block ≥30 KiB | Mac 195,604, Windows 195,848, iPhone 196,244; largest block 114,688 bytes on all, PASS |
| HID controls | Mac Cmd+V / Windows Ctrl+V, volume up, no stuck modifiers | User confirms Mac paste/volume, Windows paste/volume and iPhone volume PASS; Android pending |

The user connected and powered on the intended device. Read-only inspection at `/dev/cu.usbmodem212401` confirms ESP32-C3, 8 MiB, no secure-boot/flash-encryption restriction, and installed `nabo-adventure 0.1.0` / IDF 6.0.2. Initial strict-layout checking refused to write. The measured legacy layout has NVS `0x9000/0x6000`, PHY `0xf000/0x1000`, factory `0x10000/0x1f0000`, and FAT assets `0x200000/0x600000`, with a valid partition MD5. It differs from the build's planned table. F0 uses neither assets nor files, and its 643,392-byte app safely fits this smaller factory partition. The installer now explicitly accepts only the planned map or this measured legacy map, then checks the candidate against the actual factory size and sector boundary. Two added host tests cover the legacy layout and oversized candidates. Do not install the build's partition table on this device. Device MAC and raw inspection output remain under ignored `private/device/`; no full-flash backup was required or taken.

The user explicitly authorized flashing this F0 and starting tests in the current chat. The fixed archive was reverified, and the same port/private MAC were checked before an app-only write: image `[0x10000, 0xad140)`, erased app sectors `[0x10000, 0xae000)`. App verification passed. The legacy partition table, NVS and asset regions were not written; no merged image or full-chip erase was used. A subsequent 20-second serial observation received F0 menu status with no crash markers. Unconnected idle heap: 196,668 bytes; largest block: 114,688; minimum heap: 189,908. **These are not connected-memory acceptance results.** The user confirmed Mac pairing, OK/paste and UP/volume work; serial reports show 5 sends and 0 failures. Mac connected heap was at least 195,604 bytes, largest block 114,688, above thresholds. Opening serial causes USB_UART_CHIP_RESET on this setup: one actual restart auto-reconnected, 701 ms from advertising; repeated full boot-to-ready timing is pending. The preserved bootloader reports IDF 5.5.3. The user has an iPhone, but deferred its test when leaving work; Windows/iPhone/Android continue in the next session. Full physical screen acceptance remains pending. F1 waits for the complete agreed F0 gate.

Prototype: all ten pages were exercised through actual browser controls; passkey modal, Typeless right modifiers, PPT timer, camera countdown and menu/connection/settings/contact screens were inspected. Browser warnings/errors after the final reload: none. Screenshots are under `docs/images/prototype/`; `overview.png` is a crop montage of actual browser screenshots, not device evidence. The browser performs no real HID transmissions.

The JS reference contains 1,559 deterministic steps over ten pages, four OS values, six key events and five connection events. Three deliberate timing/modifier/cadence mutations are caught. C input classification matches JS for 4,000 events including 500 ms boundaries; uint32 wrap is separately tested. Full JS–C application-state replay remains pending F1.

Video: seven 720×720/24 fps originals, 535 frames automatically decoded. Manual checks used 0.25-second samples and endpoints/head comparisons; notes bind source hashes in `art/qa/batch1/review.json`. Welcome is 4,042 ms and plays from 1.4 s to about 5.44 s; the user selected menu entry at 5.5 s with any-key skip. Eight binary sprite variants total 405,362 bytes. Lossless decode equals every indexed target pixel; RGBA-to-indexed quantization error is recorded separately. Physical LCD readability/frame rate and the C sprite decoder remain pending F3. Boot voice, UI art and the second Grok action batch remain pending.

The user requested committing/pushing the current source and all assets to the private main branch. See WINDOWS_CONTINUE.md; git log identifies the checkpoint. No release has been published.

## Windows continuation — 2026-10-27

Baseline: `5fb23a0`, initially clean local `main`. **Asset inventory PASS: 364 files / 90,980,640 bytes**; no art/video regeneration. The installed game skill matches the private canonical text after line-ending normalization. All five Passport skills were installed; relevant stage instructions were read directly.

**Host tests PASS**: the existing Git Bash static gate ran successfully on Windows: 18 Node + 26 Python = 44 tests, byte-identical 1,559-step JS regeneration and clean diff whitespace. The original 40 checks remain; four new observer tests cover privacy/type filtering, excluding simulated/disconnected memory and keeping advertising timing separate from full boot timing. Explicit ctypes library unloading fixes Windows temporary-directory cleanup (WinError 5). Full JS–C application-state replay remains unimplemented.

**Build PASS**: the existing `C:\Espressif\esp-idf-v6.0.2` installation reports v6.0.2. ESP32-C3, 8 MiB, no PSRAM; dependency lock unchanged. Native build, merge, partition MD5/layout/image-offset verification, absence of Wi-Fi initialization symbols, archive creation and independent archive verification passed. The archive script now reads UTF-8 explicitly instead of Windows GBK and records portable `/` source paths.

| Windows artifacts (not installed) | Bytes | SHA256 |
|---|---:|---|
| F0 app | 643,392 | `dbefb160c7cae4b9eb5513e28034395b94d419035c18ee4357bb4781b96eb1b4` |
| Merged | 708,928 | `dec04d19d09f5ac57a86433d30572a6841a96922cd50640f595e67c8e4f05df9` |
| ELF | 8,537,344 | `352874748b796795215eb1e49d250ad9323b10e2912cd8bb9160c5d74fa25af6` |
| MAP | 5,810,140 | `8592ded5becbe110aa75f4a605332fe1426c06f2659f8d4f2e61c554c42ea924` |

The local verified archive is `build/firmware/dec04d19d09f5ac57a86433d30572a6841a96922cd50640f595e67c8e4f05df9/`. The older Mac archive path above is historical and was not migrated through Git. This new build does not inherit the Mac binary's device acceptance. The device still uses the handed-off `ea6789e…5074c` app; this session neither read it back to rehash nor flashed it. The generated default partition table differs from the device's measured legacy table; merged/default flashing remains prohibited.

**Device tests partial**: fresh Windows enumeration identified `COM12` (Espressif USB); runtime output identifies `NABO Toolkit F0 / ai-passport-nabo / no Wi-Fi`. State: `menu / windows / ready=false / test=false`, heap 196,516, largest block 114,688, historical minimum heap 189,756 bytes; 0 sent / 0 failed. This proves readable F0 status and unconnected memory only. It does not establish Windows pairing, HID behavior or connected-memory acceptance. Raw logs remain ignored under `private/device/`; no flashing tool changed installed partitions, NVS, bonds or assets this session.

The 300-second observation ended and released the port: 142 status samples, zero live connected samples. Without completed user actions, pairing remains unverified rather than a pass or a failure.

**Unverified**: Windows pairing/Ctrl+V/volume; iPhone and Android; connected memory on those platforms; at least three full boot-to-secured-and-both-subscribed measurements within 3 s; full display/physical-button acceptance. Windows user feedback is still pending, followed by iPhone tests. Previous Mac passes retain their historical scope. F0 is incomplete; F1, commit/push and publication were not started.

### Subsequent pairing failure observation

The user confirmed power/USB and reported **the target is visible in Windows but pairing errors**. Windows pairing: FAIL (user reported); HID and connected memory: NOT RUN. Independent BLE discovery PASS (discovery only): one `NABO 工具箱`, HID service 0x1812 present, RSSI −29 dBm. The existing F0 serial command opened one 60-second pairing window during a 150-second observation; no secured result or actionable handshake error code was captured. Serial is now released. Windows Settings exposed no targetable window, so the exact error text and whether a six-digit code appeared on the badge are still pending user input. Cause remains undetermined; older system warnings are not evidence of this failure's cause. No firmware changes, flashing, bond-store clearing or security downgrades occurred. Build/host results remain unchanged; F0 has not passed.

The user subsequently supplied the exact message, **“请尝试重新连接设备” (try connecting your device again), with no six-digit code on the badge**. During a new pairing window, the unique freshly advertised target matched exactly one Windows AEP endpoint: unpaired, can pair. Basic system `PairAsync` returned `FAILED / 19`; the badge never reached ready. [Microsoft defines result 19](https://learn.microsoft.com/en-us/uwp/api/windows.devices.enumeration.devicepairingresultstatus) as a generic failure, so this does not identify an authentication, driver or firmware cause. Private address comparison confirmed that the existing older NABO keyboard entry is another target; it was not removed. The main Settings window later became readable, but its Shell-owned add-device dialog could not be controlled through that window. No code-entry/authentication dialog was automated. iPhone pairing/volume/connected-memory testing is now requested; Windows remains unresolved and F0 stays gated.

### iPhone connected; F0 diag1 prepared only

The user first reported no iPhone discovery, then confirmed connection. Independent scanning captured connectable undirected advertising, general-discoverable flags 0x06, HID 0x1812 and keyboard appearance 0x03c1. The original F0 subsequently reported **ready=true / test=false**, meeting authentication and both-report subscription readiness. iPhone pairing/connection PASS (user confirmation plus serial); connected memory PASS: heap 196,244 and largest block 114,688 bytes. Physical volume-up confirmation remains pending; readiness alone does not establish it. `ready_ms=41128` includes this user pairing interval and is not automatic reconnect/full boot timing. A fresh six-digit ceremony was not independently observed; repeated reboot timing remains untested.

Read-only inspection reconfirmed ESP32-C3, 8 MiB and the legacy partition map. The 643,392-byte app readback exactly matches `ea6789e…5074c` and was saved privately for rollback. Only the table and app were read; no NVS reads, erases or flash writes. Partition-table SHA256: `7428911f9c364578c3d57ff0cc315b25442333cad48b1609577e7840124373c2`.

F0 diag1 is prepared for Windows diagnosis: numeric connection/security/subscription/advertising logs and a boot marker, excluding addresses, keys and passcodes. No security-policy, key-map or NVS logic changes. **Build PASS, host tests PASS (44 plus 1,559-step deterministic replay)**; build/merge/layout/no-Wi-Fi-symbol checks, independent archive verification and candidate inspect passed. App: 644,672 bytes, SHA256 `b0c39fb71ca8eb2de0ad0b1f26fd0b7e164f1d4c54cfee92c8738e47c69f7d30`; merged: 710,208 bytes, SHA256 `d021c36cb54504b91311b16350d5d00464bd85392f1041fb25bc97fcfed6f295`, archived under that hash in `build/firmware/`. **Not flashed; device tests NOT RUN.** Installation, if needed, requires separate authorization for this exact app-only candidate and live target revalidation: app `[0x10000,0xad640)`, erase end `0xae000`. Never use the merged image to upgrade this badge. Continue the original F0's iPhone acceptance first; Windows/Android and repeated timing remain pending, so F1 stays gated.

The user then explicitly confirmed **SECURED / ready and increased volume**: iPhone volume-up PASS. The 90-second capture contained 45 statuses, 36 live ready samples, minimum connected heap 196,244 and minimum largest block 114,688 bytes. The volume action occurred after that capture ended, so physical success relies on user confirmation; no send count was fabricated from the earlier zero. Disconnect only this iPhone device while preserving its bond before the next isolated Windows retry. Repeated full restart/automatic reconnect timing remains unverified.

### Latest: Windows passed; automatic reconnect 3/3, strict timing unverified

After disconnecting only the iPhone link while keeping its bond, the user confirmed **Windows pairing, paste and volume all work**. Serial also reached `ready=true / test=false`: 73 statuses over 150 seconds, 30 live ready samples, minimum connected heap 195,848 and largest block 114,688 bytes. Counts rose from 7 to 20 (13 completed sends), zero failures; final OS preference windows. Windows pairing/Ctrl+V/volume/connected memory PASS on the original, hash-verified installed F0. The initial failure's cause was not established.

Three USB hardware resets automatically reconnected to the same Windows host. A fresh boot banner and cleared send counter confirmed each actual reboot; no re-pairing was needed. Host monotonic measurements span from before the reset request to receipt of fresh ready status, including reset hold/USB/serial overhead:

| Round | Reset request to observed-ready upper bound | Advertising to ready | Heap / largest block | Upper bound ≤3 s |
|---|---:|---:|---:|---|
| 1 | 2,219.0 ms | 1,690 ms | 196,016 / 114,688 bytes | Yes |
| 2 | 3,125.0 ms | 2,608 ms | 196,016 / 114,688 bytes | No |
| 3 | 2,812.0 ms | 2,269 ms | 196,016 / 114,688 bytes | Yes |

**Automatic reconnect succeeded 3/3; the strict three-second gate remains unverified.** Round two's host upper bound does not prove exact device latency exceeded the limit, and cannot count as a pass. Cold power removal and sleep wake were not tested. The script used no ROM loader or flash writes; serial is released. Android availability was requested without waiving its gate. Diag1 remains uninstalled, build/host results unchanged; full F0 has not passed and F1 has not started.

An Android device is now available. Before pairing, source inspection confirmed that original F0 combines the three-bond limit with `ble_store_util_status_rr`, which evicts the oldest bond on overflow in the installed IDF 6.0.2 NimBLE code. The user was informed and asked whether to accept an older device potentially requiring re-pairing. No new pairing window was opened; Android remains NOT RUN. This step only read source/enumerated ports, with no NVS read/change, build or flash. F1 must follow its planned explicit full-slot deletion instead of inheriting silent eviction.

The user explicitly accepted proceeding with Android and potentially re-pairing an older device. Original-F0 observation is running and Android pairing/volume steps were provided; result IN PROGRESS, not yet a pass. This consent covers normal pairing's possible oldest-bond replacement only. No NVS erase or firmware flash occurred; diag1 remains uninstalled.

This Android attempt did not complete: the user confirms target visibility and a six-digit code on the badge. Android's PIN-entry/confirmation ceremony and error still need clarification. The 240-second capture ended with 136 statuses and zero live ready samples; Android HID/connected memory remain untested/unverified and serial is released. Bond data was not read, so actual eviction is unknown. Any retry must use the phone's correct ceremony in a fresh 60-second window, rather than a stale code. Build/host results are unchanged; F0 remains gated.

Latest clarification: **Android immediately reports pairing failure while the badge code flashes briefly and disappears**. Android pairing FAIL (user reported), cause undetermined; this is no longer classified as waiting for input. Original F0 lacks security/disconnect reason logs. The fixed diag1 archive was independently reverified (build/44 host checks remain PASS), and explicit app-only installation consent plus phone model/OS were requested. Consent remains pending: no flash, bond clear, NVS erase or security-policy changes. Similar older SDK issues are background only, not evidence of this device's root cause. F0 stays gated.

### Latest: diag1 installed; SMP confirm mismatch captured

The user explicitly authorized this fixed app-only image. The installer revalidated the device identity, C3/8 MiB/security/legacy layout on the same connection; only `[0x10000,0xad640)` was written and verified, followed by the F0 diag1 boot marker. Current app SHA256: `b0c39fb71ca8eb2de0ad0b1f26fd0b7e164f1d4c54cfee92c8738e47c69f7d30`. Bootloader/table/NVS/assets were not flashed. Earlier Mac/Windows/iPhone passes belong to original `ea6789e…5074c`, not a retest of this binary.

Phone identification is user-reported `荣耀9s pro / HarmonyOS 3.0.0`, not independently verified. Diag1 captured successful connection/security-request rc=0/passkey-display action=3, then **status=1028 / 0x404, local SMP confirm mismatch** with encryption/authentication/bonding unset. Disconnect 517 / 0x205 is the subsequent authentication failure. Failure arrived 251 ms after the passkey action and 2241 ms after the pairing window opened, excluding that attempt's 60-second timeout. New-bond persistence had not been reached; storage overflow is not an established cause. The underlying interoperability defect remains unknown.

[Espressif's similar issue](https://github.com/espressif/esp-idf/issues/14959) concerns older SDK/other phones and is background only. No SDK replacement, authentication bypass or bond clearing was performed. A phone-Bluetooth off/on isolation attempt was requested based on [Huawei's official troubleshooting](https://consumer.huawei.com/cn/support/content/zh-cn15960040/); result pending. Build/44 host checks remain PASS; diag1 flash/boot PASS, Harmony pairing FAIL; HID/connected memory, other-platform acceptance of this binary and strict timing remain unverified. F1 stays gated.

## Latest: diag2 numeric-comparison Harmony pairing, volume and memory PASS

Phone Bluetooth off/on did not fix diag1: action 3 again failed with 0x404 after about 300 ms. An explicit optional F0 command `>tk.pair.compare` selects DisplayYesNo/SC-only with MITM and bonding retained. Only numeric-comparison action 4 is accepted. Physical short OK accepts and long UP rejects; serial-injected keys cannot approve, and stale/cancelled/zero tokens are rejected. Normal long DOWN remains DisplayOnly; canonical JS, author defaults and assets are unchanged. This experiment is not the adopted default product policy.

**Build PASS / Host tests PASS (46: 18 Node + 28 Python; identical 1,559-step JS replay fixtures)**. Build/merge/layout, absence of Wi-Fi initialization and independent archive verification passed using IDF 6.0.2/C3/8 MiB/no PSRAM.

| Fixed diag2 artifact | Bytes | SHA256 |
|---|---:|---|
| app (currently installed) | 646,048 | `00517903fa87f3f3fd9bb820aa6b7882b3356cfc3a343e0694989b06fdc38982` |
| merged (not flashed) | 711,584 | `116944dcbb1ced392e1d16757fc010f7df2de7b3d22458d4f6ead517c9ed5298` |
| ELF | 8,553,072 | `916dbdece9b9772eccf0c30e2cbda9742608ef3ec2a413ddae66ce2fe1a622fd` |
| MAP | 5,812,944 | `9f535b7cde029acb8a48debbedb5e709dccfd078edbbee429619fa0280e82282` |

The user separately approved this exact app and experiment. Device identity/C3/8 MiB/legacy layout were rechecked on the same connection; only `[0x10000,0xadba0)` was written, with sector erase ending at `0xae000`. Write verification and F0 diag2 boot marker passed. Table/NVS/assets and private original-app rollback remain preserved. Original-image Mac/Windows/iPhone results have not been relabelled as diag2 acceptance.

Earlier incomplete experiments: an expired window followed by long DOWN selected normal action3/0x404; another displayed numeric comparison (action4), but only the phone was confirmed, and the 60-second window interrupted the late handshake (status7/disconnect534). Neither proves failure after both confirmations. The private observer now refreshes advertising before a connection is seen, then stops refreshing after the first link; it never confirms automatically.

The user confirmed matching codes, physical short OK plus phone confirmation, `SECURED / ready`, and physical UP increasing phone volume while staying ready. Device uptime: connect575912, action4 prompt576263, physical accept609692/rc0, encryption610021 (encrypted/authenticated/bonded all1), both report subscriptions612712, ready612713 ms. **Experimental Harmony pairing/volume/connected-memory PASS**: minimum observed live heap195232, largest block114688 bytes, test=false. Aggregate completed sends5/failures0 do not establish an exact physical-press count. The 39521ms manual pairing interval is not boot timing. Capture archival and three same-phone restart measurements follow.

**Unverified**: original display-passkey interoperability cause/default product policy, other-platform regression on current binary, strict full-restart three-second gate, cold power/sleep wake, complete display/buttons and full JS-C application replay. Full F0 remains gated and F1 has not started. No commit/push/publication; raw logs, bindings and device identity stay private.

## Latest: diag2 three-second reconnect FAIL; fixed diag3 candidate awaiting consent

The comparison capture completed: 300 seconds, 148 status samples, 116 live ready samples, with the memory minima and aggregate 5 completions/0 failures above. Three USB hardware resets of the same phone/bond then automatically reached secure/subscribed ready without re-pairing; fresh boot markers and zeroed send counts confirm actual resets:

| Round | Reset-request-to-ready host upper bound | app ready-event uptime | Heap / largest block |
|---|---:|---:|---:|
| 1 | 11640.0 ms | 11596 ms | 196116 / 114688 bytes |
| 2 | 11250.0 ms | 11205 ms | 196116 / 114688 bytes |
| 3 | 11547.0 ms | 11509 ms | 196116 / 114688 bytes |

**Three-second gate FAIL**: app ready uptime itself exceeds 11 seconds. Each trace has no connection during directed advertising, timeout reason13 after ~10 seconds, then filter2 last-peer whitelist advertising and ready ~0.7–1.1 seconds later. The delayed phase is established; the underlying reason this phone ignores directed advertising is not established. Automatic reconnect success is not timing acceptance. No power-removal or sleep test was performed.

Diag3 candidate changes the directed budget to 500ms before last-peer-only whitelist advertising. It retains the ten-second reconnect UI window and original timing origin; UI expiry no longer aborts a live security handshake. Encryption/authentication/subscription gates, normal DisplayOnly, optional comparison, keys, NVS and assets remain unchanged. Only transport scheduling changed; canonical prototype page rules and 1559-step fixtures remain unchanged, with FIRMWARE_PLAN updated. A production-policy boundary/uint32-wrap test brings **host tests to 47 (18 Node + 29 Python), PASS**. Build/merge/layout/no-Wi-Fi-init/independent immutable archive verify/fixed-candidate inspect all PASS.

| Fixed diag3 artifact (not installed) | Bytes | SHA256 |
|---|---:|---|
| app | 646272 | `cb5eeda654b3e22110dc0119ac17df0773c4c8a56a4ac12fbfaf999c7abf830d` |
| merged | 711808 | `2192d4137e1a12e1d44e798c2c11646e8fd501245004fd8b9b9549160224c532` |
| ELF | 8554448 | `913e31042009802f6ecf0bcb09fbb850e492e8bc83fd5b8157a5ca41ac26acbd` |
| MAP | 5813301 | `5de5fc7c4922cfe1a129a2d6904826b0eeaf213a40b313f3f88d5573c3295899` |

Archive: `build/firmware/2192d4137e1a12e1d44e798c2c11646e8fd501245004fd8b9b9549160224c532/`. COM12 was re-enumerated, and a new read-only check confirmed the same private identity/C3/actual8MiB/legacy2031616-byte factory, unchanged partition-table hash, and exact installed diag2 app hash. The candidate fits the actual smaller partition. No NVS read or Flash write; device reset and serial released afterward.

Only after explicit approval of this fixed app may `[0x10000,0xadc80)` be written, with erase ending at `0xae000`; revalidate identity/capacity/layout on the actual write connection and preserve table/NVS/assets. **Consent PENDING; diag3 device tests NOT RUN; installed app remains diag2.** Next: three same-phone reconnect tests retaining its bond. Default DisplayOnly interoperability, other-platform current-binary regression, cold power/sleep and full application replay remain incomplete. F0 remains gated, F1 not started; no commit/push/publication.

## Latest: diag3 installed, timing still FAIL; Tango2S awaits phone disconnection

The user explicitly approved fixed app `cb5eeda654b3e22110dc0119ac17df0773c4c8a56a4ac12fbfaf999c7abf830d`. Same-connection identity/capacity/legacy-layout checks and app-only write verification passed; table/NVS/assets preserved. All three fresh boot markers confirm F0 diag3, retaining the phone bond:

| Round | Reset-to-ready host upper bound | app ready uptime | filter2 advertising uptime | Heap / largest |
|---|---:|---:|---:|---:|
| 1 | 6922.0ms | 6885ms | 1024ms | 196108 / 114688 |
| 2 | 5344.0ms | 5316ms | 1003ms | 196116 / 114688 |
| 3 | 11234.0ms | 11214ms | 997ms | 196116 / 114688 |

Existing-bond automatic reconnects3/3, authentication/subscriptions/memory PASS; three-second gate **FAIL**. Whitelist advertising starts early, but links arrive at6334/5015/10813ms; remaining cause is unestablished. The phone is unavailable to the user, so screen state/distance are unknown and current-diag3 physical volume remains **NOT RUN**. Diag2 physical acceptance is not inherited. A subsequent90-second capture had42 live ready statuses, heap196116/largest114688, zero sends/failures; serial released.

The user supplied iReader Tango2S as a supplementary target (system/HID compatibility unverified) and a future office Xiaomi TV target. Opening the reader's experiment window caused the old phone to auto-reconnect with its existing bond, ready in639ms with no new comparison prompt. This is neither a reader pass nor a reader failure. The user can disconnect the phone and will report when done; no bond deletion is needed.

The user explicitly confirmed normal new-pairing FIFO replacement when all three records are occupied, without repeated eviction approval requests. These are pairing records, not six-digit passcodes; three is the current configuration. Prototype/DESIGN/FIRMWARE_PLAN now replace the oldest new-pairing record, preserve records on cancellation/timeout, and do not reorder on ordinary reconnect. **Latest48 host tests (19 Node+29 Python) and1582-step JS deterministic fixtures PASS**, covering cancellation, replacement, consecutive evictions and reconnect ordering. The author HID table is byte-identical; historic1559-step fixtures remain in Git baseline. Only prototype/docs/fixtures changed afterward; installed app remains unchanged and F1 C application work has not started.

**Build PASS (installed fixed diag3) / Host tests PASS48 / Device tests partial PASS for reconnect/memory, timing FAIL, Tango2S NOT RUN / Unverified current physical HID/default DisplayOnly/other platforms/cold power/sleep/reader/TV/full JS-C replay.** F0 stays gated. No commit/push/publication; raw logs/identities/bindings remain private.

## Latest: F1 development candidate passes host/build gates; device testing deferred

The user explicitly stopped device tests and authorized further development. F1 now includes the complete default C model/HID table, ten Chinese placeholder pages, QR/passkey dialogs, persistent three-slot FIFO/select/type/delete, CRC settings/slot records, startup, button/audio queues and sleep wiring. Production initialization is empty/disconnected. HID requires actual encryption/authentication and both report subscriptions; UI owns the model, NimBLE owns lifecycle commands. Simulated serial-test actions suppress HID/settings/bond writes; exit restores the prior model and real profiles. The real BLE lifecycle still maintains keys independently, so test mode is not an NVS read-only lock. Simulated counters are separate.

**Build PASS**: native Windows `./tools/validate.ps1 -Stage F1`, ESP-IDF6.0.2/C3/8MiB/noPSRAM, isolated defaults, build/merge/layout/MD5/offsets/no-Wi-Fi-init/archive checks. App **909,696 bytes**, SHA256 `2bd07a8b48ebde05ad97ed8d2e9cfcfb22377df94eb66a594e1ec536e17c7d79`; merged975,232 bytes SHA256 `93ddf1bad638082fa9881dc54cbb44f866064b9a410fcb659c097e6b2e139e7e`. It fits the measured legacy2,031,616-byte factory, but the generated table still differs from the physical table: merged image is verification-only for this device. F0 regression `-Stage F0 -FirmwareOnly` also passes; its647,232-byte new app is uninstalled, archive `d4d5b2d7c3856abae70696ac3424c8de1fbc6592a82ec1fb4acd7ba09eeea17b`.

**Host tests PASS:71 (20 Node +51 Python), zero skips**. All1,582 default reference steps compare complete projected C state, every effect and sleepDue; three deliberate C mutations are caught. Ten-page renderer tests cover >80 representative frames with dirty/full pixel equality, wide six-digit codes and same-size QR payload changes. Synthetic RAM providers test migration/CRC/transaction failure/FIFO preservation, not actual Flash power loss or RTOS concurrency. Custom F2 configuration is unimplemented and is not included in this replay claim.

Exact independently verified archive: `build/firmware/93ddf1bad638082fa9881dc54cbb44f866064b9a410fcb659c097e6b2e139e7e/`; app/merged/ELF/MAP hashes in `validation/f1.json`. Original364 assets/90,980,640 bytes reverify PASS; no new art, author HID hash unchanged. Placeholders convert existing atlas frame zero to RGB565 with original alpha; generated font subsets, OFL and provenance hashes are included. [Host C renderer preview](images/f1/overview.png) uses synthetic demo peers and is not a device photograph.

Product slots remain three. F1's fourth SDK key record is staging capacity: commit new slot before removing oldest key; failed commits remove only new staging, startup prunes unreferenced staging. F0 migration preserves SDK bonds and selected identity/OS; names are currently generic numbered labels. Reconnect/selection does not reorder FIFO. New-pair windows reject old automatic reconnects; explicit slot deletion is needed before repairing an existing identity. DisplayOnly remains default; optional numeric comparison still requires physical confirmation.

**Device tests: F1 NOT RUN**. No serial open/reset/flash after the user deferred testing. Installed image remains fixed diag3 `cb5eeda6…abf830d`; partition/NVS/assets untouched. Prior physical passes remain image-specific; diag3 Harmony three-second FAIL remains.

**Unverified**: all F1 physical pairing/HID, ten slot switches/timing/memory,3-second reconnect, PPT/meeting/camera, one-hour/50-key stability, power retention, LCD/buttons/audio and sleep/wake. Shared ADC GPIO can electrically wake on any key; exclusive UP-only wake is not claimed. Tango2S/XiaomiTV deferred. Still placeholders/short boot cue, no full sprite/voice/F2 integration. No commit/push/publication/new flash authorization.

## Latest: F2 host/build acceptance (2026-10-27)

User explicitly requested F2 while deferring flashing/device tests. Existing F1 now supports group/card editing, per-family chords, media/ASCII text, strict shared validation, chunked USB/CRC, NVS save/startup load and immediate model application after commit. Browser automatically reads back and compares before reporting success. Browser Save remains separate; author defaults/artwork stay unchanged.

**Host tests PASS:87 (27 Node +60 Python), zero skips**. Full1,710-step state/effects/sleepDue replay includes original1,582 plus128 configured steps/four OS, with three caught C mutations. Production JS client communicates with production C parser/protocol/RAM storage through stdio. Shared schema corpus, simulated reboot,64-character macros, disabled families, index clamping,4000-byte budget, corruption/timeout/interruption/test refusal/storage errors and corrupt-record preservation are covered. RAM providers do not prove real Flash power loss.

Local browser edit/save/reload/restore passed; unconnected USB read/write disabled; zero console errors/warnings; no port opened. [Config screenshot](images/f2/config-page.png), [C renderer preview](images/f2/overview.png). Custom CJK uses the existing font's21,281-glyph16px/1bpp Flash fallback; scale uses nominal pixel size instead of exceptional glyph bounding line height. Size assertion and dirty/full pixel equality pass; physical readability/memory remains untested.

**Build PASS**: final F2 version0.2.0-f2-dev1, ESP-IDF6.0.2/C3/8MiB/noPSRAM; full native PowerShell gate plus final incremental build/merge/layout/no-Wi-Fi-init/fixed archive checks. F0/F1 regression builds pass. cJSON1.7.19~2 added; cmake_utilities stays1.1.1; other versions unchanged. App **1,849,584 bytes**, SHA256 `55967cb3a9c89acc520bae2e295e7d92d52db8a0a0a1050cb71718da4428cb67`, leaving182,032 bytes in the measured legacy factory. Generated table still differs; no default/merged flashing.

Fixed archive `build/firmware/002ba9facfb572270d1d6c13672994c86e10c468e8cc5c48b7be3846d0f10c13/`; app/merged/ELF/MAP and source hashes in `validation/f2.json`. Independently verified with source inventory matching final worktree. F1/F0 regression bundles are also recorded there. Original364 assets/90,980,640 bytes reverify PASS. [Configuration/protocol guide](CONFIGURATION.md); native build `./tools/validate.ps1 -Stage F2`.

**Device tests: NOT RUN**. No COM enumeration/open/flash/Bluetooth action this increment. Installed fixed F0 diag3 remains `cb5eeda6…abf830d`, table/NVS/assets untouched. No commit/push/publication.

**Unverified**: actual USB permissions/reset/unplug/write/read, physical Flash power retention/error semantics, configured HID/text/QR/LCD and connected heap/largest block, all pending F0/F1 physical gates. Prior Harmony3s FAIL retained; Tango2S/TV deferred. Full animation/voice remains F3. Source/host/build completion is not physical/release acceptance.

## Latest: F2 installed; actual USB save/readback and warm-reset retention pass

The user resumed flashing/testing. Fixed dev1 was installed app-only after same-connection identity/C3/actual8MiB/legacy-factory checks. Menu, Chinese and UP/DOWN were user-confirmed. Real save/readback passed, but repeated reads lost chunks; the client correctly failed length checks. Failure evidence was retained and the original configuration restored.

Current **0.2.0-f2-dev2** uses the IDF interrupt USB driver with2048-byte TX/512-byte RX buffering and nonblocking input. Default polling VFS can drop bytes after a50ms host stall. Private capture also drains immediately and reopens after USB reset; a sole loss cause is not established. **Build PASS / Host tests PASS87 (27 Node+60 Python),1710 replay steps.** App1859696 bytes, SHA256 `49e596ca849119428f1d9cc95f6ff91b9c7016a99e6e9fca53e5285bb3185d57`; independently verified archive `build/firmware/35b077ef48a7ecbee1b671c28ed60b157deade1028b46bf76a399929bd1a45b4/`, source inventory matches. App-only `[0x10000,0x1d6070)`, erase ends0x1d7000. App verification and table/NVS/PHY/first-assets-sector before/after hashes passed before reboot. Entire assets excluded by bounds; no whole-assets hash. Runtime configuration/slot writes are normal NVS operations, not an erase. No merged/table flash or whole-chip erase; rollback apps remain private.

**Device tests PARTIAL PASS**: production JS client over actual USB, real NVS save/readback, bad CRC/non-ASCII rejection preserving current data, abort,10010ms receive timeout, test-mode write refusal/read access, two fresh F2 USB resets (boot markers748/746ms), and20 repeated full reads all passed. Temporary group/card metadata was restored; HID bindings stayed unchanged, crash markers0. This does not prove browser Web Serial permission handling or cold power retention.

The user confirmed Windows re-pairing, paste and volume: **dev2 Windows pairing/Ctrl+V/media volume PASS**. Initial imported-slot reconnect failure remains unexplained. Default configuration:220 ready samples/minimum heap113772; custom configuration:175 ready/minimum heap113664; largest98304 bytes in both, passing60KiB/30KiB gates. Send failures/crash markers0. One slot remained after user pairing/navigation; full migration and three-slot stress are unverified.

**Configured physical effects/cold power retention PASS**: user confirmed the one-group Chinese label, actual NABO-F2-TEST typing, custom card fields and exact QR URL https://example.org/nabo-f2. Initial webpage concern was clarified as the test URL having no NABO page, not an established QR encoding error. User unplugged USB, powered off, waited about5s, powered on and confirmed custom fields retained. USB readback then exactly matched the temporary configuration; original shortcuts/cards were restored with complete readback verification. This proves retention after successful commit, not power interruption during a write or actual storage-fault semantics.

**Unverified**: actual browser USB permission/UI/unplug flow, power interruption during commit/actual storage faults, other-platform regression/old-bond reconnect, remaining F0/F1 physical gates and three-second reconnect. Prior Harmony timing FAIL retained; Tango2S/TV deferred. No commit/push/publication; private identities/bonds/configuration/raw logs remain ignored.

The user reaffirmed startup visuals/sound and tool-specific animation requirements. Firmware still uses static first-frame placeholders; full F3 is incomplete. Reuse existing seven videos/405362-byte packs and5.5s welcome/any-key skip. Only171920 app bytes remain: plan protected resource loading without repartitioning/replacing retained FAT contents. Confirm the toolkit-specific startup audio source; the indexed audio folder currently only contains VOICE.md. Do not substitute another project's welcome or a short cue, regenerate art, or repeat paid generation.
