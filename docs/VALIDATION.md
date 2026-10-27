<p align="right"><a href="VALIDATION.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# Validation checkpoint — 2026-10-27

Build: PASS  
Host tests: PASS (40)  
Device tests: PASS (flash/startup, Mac pairing/paste/volume, Mac connected memory); full F0 acceptance remains incomplete  
Unverified: Windows/iPhone/Android pairing, repeated full boot-to-ready timing, other-system HID, full display/button acceptance, sleep and F1.

The complete gate `./tools/validate.sh` passed using **ESP-IDF 6.0.2** and an isolated configuration generated from tracked defaults. It includes 18 Node tests, 7 C probe/input tests, 8 sprite-codec tests, 7 flash-guard tests, JS golden determinism, diff whitespace checks, firmware build/merge/layout verification and immutable archive hash verification. SDK version follows this project's FIRMWARE_PLAN rather than the reusable skill's generic 5.5.3 default.

| Artifact | Bytes | SHA256 |
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
| Pairing | Mac, Windows, iPhone, Android; six-digit passkey when requested | Mac PASS; others pending |
| Restart reconnect | Last peer automatically secured/subscribed within 3 s | One actual USB reset reconnected; 701 ms from advertising. Repeated full timing pending |
| Connected memory | Idle heap ≥60 KiB; largest block ≥30 KiB | Mac PASS: at least 195,604 / 114,688 bytes |
| HID controls | Mac Cmd+V / Windows Ctrl+V, volume up, no stuck modifiers | User confirms Mac paste/volume; 5 successful reports, 0 failures. Others pending |

The user connected and powered on the intended device. Read-only inspection at `/dev/cu.usbmodem212401` confirms ESP32-C3, 8 MiB, no secure-boot/flash-encryption restriction, and installed `nabo-adventure 0.1.0` / IDF 6.0.2. Initial strict-layout checking refused to write. The measured legacy layout has NVS `0x9000/0x6000`, PHY `0xf000/0x1000`, factory `0x10000/0x1f0000`, and FAT assets `0x200000/0x600000`, with a valid partition MD5. It differs from the build's planned table. F0 uses neither assets nor files, and its 643,392-byte app safely fits this smaller factory partition. The installer now explicitly accepts only the planned map or this measured legacy map, then checks the candidate against the actual factory size and sector boundary. Two added host tests cover the legacy layout and oversized candidates. Do not install the build's partition table on this device. Device MAC and raw inspection output remain under ignored `private/device/`; no full-flash backup was required or taken.

The user explicitly authorized flashing this F0 and starting tests in the current chat. The fixed archive was reverified, and the same port/private MAC were checked before an app-only write: image `[0x10000, 0xad140)`, erased app sectors `[0x10000, 0xae000)`. App verification passed. The legacy partition table, NVS and asset regions were not written; no merged image or full-chip erase was used. A subsequent 20-second serial observation received F0 menu status with no crash markers. Unconnected idle heap: 196,668 bytes; largest block: 114,688; minimum heap: 189,908. **These are not connected-memory acceptance results.** The user confirmed Mac pairing, OK/paste and UP/volume work; serial reports show 5 sends and 0 failures. Mac connected heap was at least 195,604 bytes, largest block 114,688, above thresholds. Opening serial causes USB_UART_CHIP_RESET on this setup: one actual restart auto-reconnected, 701 ms from advertising; repeated full boot-to-ready timing is pending. The preserved bootloader reports IDF 5.5.3. The user has an iPhone, but deferred its test when leaving work; Windows/iPhone/Android continue in the next session. Full physical screen acceptance remains pending. F1 waits for the complete agreed F0 gate.

Prototype: all ten pages were exercised through actual browser controls; passkey modal, Typeless right modifiers, PPT timer, camera countdown and menu/connection/settings/contact screens were inspected. Browser warnings/errors after the final reload: none. Screenshots are under `docs/images/prototype/`; `overview.png` is a crop montage of actual browser screenshots, not device evidence. The browser performs no real HID transmissions.

The JS reference contains 1,559 deterministic steps over ten pages, four OS values, six key events and five connection events. Three deliberate timing/modifier/cadence mutations are caught. C input classification matches JS for 4,000 events including 500 ms boundaries; uint32 wrap is separately tested. Full JS–C application-state replay remains pending F1.

Video: seven 720×720/24 fps originals, 535 frames automatically decoded. Manual checks used 0.25-second samples and endpoints/head comparisons; notes bind source hashes in `art/qa/batch1/review.json`. Welcome is 4,042 ms and plays from 1.4 s to about 5.44 s; the user selected menu entry at 5.5 s with any-key skip. Eight binary sprite variants total 405,362 bytes. Lossless decode equals every indexed target pixel; RGBA-to-indexed quantization error is recorded separately. Physical LCD readability/frame rate and the C sprite decoder remain pending F3. Boot voice, UI art and the second Grok action batch remain pending.

The user requested committing/pushing the current source and all assets to the private main branch. See WINDOWS_CONTINUE.md; git log identifies the checkpoint. No release has been published.
