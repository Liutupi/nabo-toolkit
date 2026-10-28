<p align="right"><a href="CONFIGURATION.zh_CN.md">简体中文</a> · <strong>English</strong></p>

Public entry: https://liutupi.github.io/nabo-toolkit/ ; offline package: https://github.com/Liutupi/nabo-toolkit/releases . F3 retains the F2 protocol. Physical browser permission flow remains unverified.

# Shortcut and card configuration (F2/F3)

Use existing offline `game-art/toolkit/prototype/config.html`. Browser Save updates the prototype; USB writes require explicitly choosing a port and clicking Write and verify. **Historical F2 dev2 acceptance: installed app-only, actual USB save/readback/two warm resets/20 repeated reads passed. Configured text/card/QR and committed-save cold power retention also passed; browser permission/unplug-during-transfer remain unverified.**

The current badge still runs F3 dev3 and retains the F2 protocol. Open the HTTPS page, complete offline package or localhost page in desktop Chrome/Edge, connect by data cable and choose the freshly enumerated correct USB port. Read, edit and write. Release serial monitors first; opening/reset may restart the badge, and USB reset may require reconnecting the page. Ports never open automatically. Interrupted/timed-out writes need a readback check rather than automatic rewriting.

Edit1–6 groups with UP/OK/DOWN bindings and1–3 cards. Record or manually select left/right modifiers. Mac/iPhone and Windows/Android families are independent; clearing a family disables it. Unset bindings emit no HID. Fixed meeting/PPT/media/camera tables stay unchanged. Defaults come from the current author-maintained tk_hid.js; the user explicitly requested the group changes below. Personal saved configurations are never automatically overwritten.

## New defaults and existing-device configuration

| Group | UP | OK | DOWN |
|---|---|---|---|
| Screenshot | Original screenshot chord | Original paste chord | Esc cancel |
| Typeless | Original translate binding | Original voice-input binding | Original ask binding |
| CapCut | Original split binding | Original play/pause binding | Original undo binding |
| WeRead | ↑ previous page | → next chapter | ↓ next page |
| Douyin | ↑ previous video | → right/seek | ↓ next video |
| Edit | Undo: Cmd/Ctrl+Z | Copy: Cmd/Ctrl+C | Select all: Cmd/Ctrl+A |

Window, PS and Browser are removed from the new default set. The screenshot/paste, Typeless and CapCut actions are retained; Screenshot DOWN now sends Esc. WeRead/Douyin send plain UP0x52, RIGHT0x4f and DOWN0x51 on all four host types, including phones. OK sends the keyboard right arrow, not a mouse right click. Page/chapter/seek behavior depends on the actual app, reading mode and focus; Douyin RIGHT is not guaranteed to select the next video. The user confirmed screenshot invocation/cancellation and said WeRead/Douyin work on the current test host. The host type was not specified; separate phone/desktop platforms and individual chapter/seek behaviors remain unverified.

For an existing badge: **Connect → Read from badge → Use new default shortcuts (keep cards) → Write and verify**. The new-default-groups button only replaces groups in the current editor and retains that editor's cards. Read first to retain the actual cards stored on the badge. Clicking the button does not automatically read/write the device or save browser storage. Restore defaults resets both draft groups and cards, so it is not a substitute for the card-preserving workflow.

Existing dev3 loads its stored NVS configuration before using defaults; a firmware upgrade does not automatically replace personal groups. The production JS client has written the six new groups over real USB to the current old dev3 and read them back three times; original screenshot/paste, Typeless, CapCut and cards are retained as intended. No firmware flash, bond change, partition change or NVS erase was performed. This proves configuration save/readback on the old dev3. The user subsequently confirmed screenshot invocation/cancellation and WeRead/Douyin operation on the current host, without identifying phone versus desktop. It is not all-platform acceptance or on-device acceptance of the new candidate.

| Field | Limit |
|---|---|
| Root | v:1, groups and cards required; unknown/duplicate keys rejected |
| Group/key label | Up to8 Unicode characters; group name nonempty |
| Chord | mod0–255, key0 or4–115; key0 for modifier-only chords; family may be null |
| Consumer | Play/pause, next, previous, volume up/down |
| Text macro | Up to64 printable ASCII characters or LF; invalid characters rejected |
| Card | Nonempty title≤6 characters; name≤24; line≤32; nonempty QR≤160 UTF-8 bytes |
| Whole configuration | Canonical compact JSON≤4000 UTF-8 bytes; unsigned integral numeric spelling |

Old6-character labels could not contain the author's existing “播放 / 暂停”; old16-character names could not contain github.com/Liutupi. These limits expanded to8/24 during F2. The subsequently requested default-group changes are listed above; protocol and field limits remain unchanged. Import, browser save and USB write share validation. Compact JSON export fits its own import limit. Wi-Fi QR generation escapes fields; Wi-Fi passwords remain plaintext in the badge/export, so remove private values before sharing.

A Flash-backed21,281-glyph CJK/punctuation fallback uses the existing Source Han font at16px/1bpp, scaled for requested display size. Unsupported glyphs become squares. No full glyph bitmap buffer is allocated. F3 already integrates the original seven animations and dedicated voice; user acceptance is recorded in HANDOFF22.

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

Use project ESP-IDF6.0.2 plus Node/Python/native C11 compiler. Current F3: native Windows ./tools/validate.ps1 -Stage F3; Linux/WSL ./tools/validate.sh --f3; output build/f3. F3 inherits F1/F2 defaults; use -Stage F2 / --f2 to regress F2 separately. JSON uses pinned espressif/cjson1.7.19~2; preexisting cmake_utilities stays1.1.1 and other dependency versions remain.

The complete gate has PASSED:29 Node+73 Python=102 checks,1710 full replay steps and3 deliberate mutations caught; ESP-IDF6.0.2/F3 build PASS. Candidate `0.3.1-shortcuts-dev1` app is1,999,728 bytes and has not been flashed or published. Current user feedback comes from the old dev3 configuration update, not device acceptance of this candidate.

Historical F2 acceptance, not this default-group revision:87 host tests/1710 steps covered shared JS/C validation, production JS-to-C stdio/RAM persistence/fault injection, model and rendering. The production JS client subsequently passed actual USB save/readback/rejections/two resets/20 reads, restoring original configuration. Dev1 dropped-read chunks were detected by length checks; dev2 buffered USB completed the tests. Configured text/card/QR and cold power retention after commit are user/readback verified. Actual browser permission/unplug during transfer/power interruption during commit/hardware fault semantics still need separate acceptance; see [validation](VALIDATION.md) and validation/f2.json.
