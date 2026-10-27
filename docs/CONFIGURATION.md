<p align="right"><a href="CONFIGURATION.zh_CN.md">简体中文</a> · <strong>English</strong></p>

Public entry: https://liutupi.github.io/nabo-toolkit/ ; offline package: https://github.com/Liutupi/nabo-toolkit/releases . F3 retains the F2 protocol. Physical browser permission flow remains unverified.

# Shortcut and card configuration (F2/F3)

Use existing offline `game-art/toolkit/prototype/config.html`. Browser Save updates the prototype; USB writes require explicitly choosing a port and clicking Write and verify. **F2 dev2 is installed app-only: actual USB save/readback/two warm resets/20 repeated reads pass. Configured text/card/QR and committed-save cold power retention also pass; browser permission/unplug-during-transfer remain unverified.**

The current badge runs F2. Open the local page/localhost in Chrome/Edge, connect by data cable and choose the freshly enumerated correct USB port. Read, edit and write. Release serial monitors first; opening/reset may restart the badge, and USB reset may require reconnecting the page. Ports never open automatically. Interrupted/timed-out writes need a readback check rather than automatic rewriting.

Edit1–6 groups with UP/OK/DOWN bindings and1–3 cards. Record or manually select left/right modifiers. Mac/iPhone and Windows/Android families are independent; clearing a family disables it. Unset bindings emit no HID. Fixed meeting/PPT/media/camera tables stay unchanged. Author defaults still come from tk_hid.js; Restore defaults edits the draft and needs a separate save.

| Field | Limit |
|---|---|
| Root | v:1, groups and cards required; unknown/duplicate keys rejected |
| Group/key label | Up to8 Unicode characters; group name nonempty |
| Chord | mod0–255, key0 or4–115; key0 for modifier-only chords; family may be null |
| Consumer | Play/pause, next, previous, volume up/down |
| Text macro | Up to64 printable ASCII characters or LF; invalid characters rejected |
| Card | Nonempty title≤6 characters; name≤24; line≤32; nonempty QR≤160 UTF-8 bytes |
| Whole configuration | Canonical compact JSON≤4000 UTF-8 bytes; unsigned integral numeric spelling |

Old6-character labels could not contain the author's existing “播放 / 暂停”; old16-character names could not contain github.com/Liutupi. Limits now8/24 respectively, preserving author defaults. Import, browser save and USB write share validation. Compact JSON export fits its own import limit. Wi-Fi QR generation escapes fields; Wi-Fi passwords remain plaintext in the badge/export, so remove private values before sharing.

A Flash-backed21,281-glyph CJK/punctuation fallback uses the existing Source Han font at16px/1bpp, scaled for requested display size. Unsupported glyphs become squares. No full glyph bitmap buffer is allocated. Complete animation/voice remains F3.

## USB protocol

ASCII lines terminated by LF; CRLF accepted. Length/CRC operate on UTF-8 JSON. CRC32 IEEE uses initial/final XOR0xffffffff. Each standard canonical-base64 segment carries≤48 raw bytes/64 encoded characters. Await each acknowledgment before the next segment.

| Request | Success response |
|---|---|
| >tk.cfg.abort | tk.cfg.aborted, cancels uncommitted transfer |
| >tk.cfg.begin byte_count | tk.cfg.ready byte_count |
| >tk.cfg.data base64 | tk.cfg.more accumulated_count |
| >tk.cfg.end eight_hex_crc | tk.cfg.ok canonical_byte_count crc |
| >tk.cfg.read | tk.cfg.begin count, multiple tk.cfg.data segments, tk.cfg.end crc |

Only complete length/CRC/schema/range/UTF-8 validation reaches NVS nabo_tk/cfg_v1, a binary TKCF/version/length/CRC envelope containing canonical JSON. Apply to the UI model only after successful storage commit; clamp indices when groups/cards shrink. Reads stream one segment per loop and prevent automatic sleep during transfer. The browser automatically reads back after writing and checks CRC and complete configuration equality before reporting success.

Errors are tk.cfg.err plus a fixed code, never echoed personal configuration: size/json/utf8/depth/keys/number/version/groups/cards/name/label/key/media/text/card/crc/data/state/busy/line/timeout/test/memory/storage. Receive timeout is10s inactivity/60s overall. Overlong lines, invalid base64, wrong order/excess data, overlapping begin and test-mode writes are rejected without switching active configuration. Corrupt persisted records fall back with an error and remain intact; no erase.

During >tk.test=1, configuration writes are refused; reads return actual committed configuration. Simulations do not persist. Test mode is not a global NVS/NimBLE read-only lock. Settings, slots and pairing keys remain independent and are not deleted.

## Host gate

Use project ESP-IDF6.0.2 plus Node/Python/native C11 compiler. Native Windows: ./tools/validate.ps1 -Stage F2. Linux/WSL: ./tools/validate.sh --f2. F1+F2 defaults generate build/f2. JSON uses pinned espressif/cjson1.7.19~2; preexisting cmake_utilities stays1.1.1 and other dependency versions remain.

87 host tests/1710 steps cover shared JS/C validation, production JS-to-C stdio/RAM persistence/fault injection, model and rendering. The production JS client subsequently passed actual USB save/readback/rejections/two resets/20 reads, restoring original configuration. Dev1 dropped-read chunks were detected by length checks; dev2 buffered USB completed the tests. Configured text/card/QR and cold power retention after commit are user/readback verified. Actual browser permission/unplug during transfer/power interruption during commit/hardware fault semantics still need separate acceptance; see [validation](VALIDATION.md) and validation/f2.json.
