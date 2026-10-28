<p align="right"><a href="CONFIGURATION.zh_CN.md">简体中文</a> · <strong>English</strong></p>

Configuration entry: https://liutupi.github.io/nabo-toolkit/ . The new configuration page follows the current five-group source; the matching offline package belongs to [v0.3.1-remote-dev2](https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.1-remote-dev2). Publication/deployment verification is in progress. F3 retains the F2 configuration protocol; physical browser permission flow remains unverified.

**Delivery boundary:** v0.3.0 packages and the old `nabo-toolkit-config-shortcuts-20261028.zip` retain their original six-group snapshots (HANDOFF25). The new page follows the five-group source. Old dev3 needs this version's app to gain Media → Music/Douyin and display-off; reading personal configuration does not automatically delete groups. The fixed app is installed/partially accepted on the author's badge, while public deployment, release and community status are verified separately during publication.

Historical v0.3.0 asset verification: the original firmware ZIP and `nabo-toolkit-config-offline.zip` retain their publication-time page/defaults and do not automatically track the online page. The old20261028 configuration supplement has `config-shortcuts-manifest.json` and the separate `CONFIG_SHORTCUTS_SHA256SUMS.txt`. It contains no new firmware and does not replace the original eight release assets. All 11 release assets were anonymously downloaded and matched local bytes/SHA-256; the original eight hashes are unchanged, and all 13 members of the new ZIP matched its manifest. The historical f8b8ad8 Pages deployment passed anonymous HTTP 200 and byte/hash checks for its manifest and11 accessible files; this is not the new deployment's verification result.

# Shortcut and card configuration (F2/F3)

Use existing offline `game-art/toolkit/prototype/config.html`. Browser Save updates the prototype; USB writes require explicitly choosing a port and clicking Write and verify. **Historical F2 dev2 acceptance: installed app-only, actual USB save/readback/two warm resets/20 repeated reads passed. Configured text/card/QR and committed-save cold power retention also passed; browser permission/unplug-during-transfer remain unverified.**

The current badge runs the fixed `0.3.1-remote-dev2` app and retains the F2 configuration protocol. Open the HTTPS page, complete offline package or localhost page in desktop Chrome/Edge, connect by data cable and choose the freshly enumerated correct USB port. Read, edit and write. Release serial monitors first; opening/reset may restart the badge, and USB reset may require reconnecting the page. Ports never open automatically. Interrupted/timed-out writes need a readback check rather than automatic rewriting.

Edit1–6 groups and1–3 cards. The local candidate editor displays UP/DOWN/OK rows to match the physical top-to-bottom keys; the old packages retain their earlier layouts. JSON keeps its existing up/ok/down fields. Record or manually select left/right modifiers. Mac/iPhone and Windows/Android families are independent; clearing a family disables it. Unset bindings emit no HID. Meeting/PPT/camera and the candidate's Music/Douyin controls are fixed outside this editor. Defaults come from the current author-maintained tk_hid.js; personal saved configurations are never automatically overwritten.

## Unreleased candidate defaults and existing-device configuration

| Group | UP | DOWN | OK |
|---|---|---|---|
| Screenshot | Original screenshot chord | Esc cancel | Original paste chord |
| Typeless | Original translate binding | Original ask binding | Original voice-input binding |
| CapCut | Original split binding | Original undo binding | Original play/pause binding |
| WeRead | ↑ previous page | ↓ next page | → next chapter |
| Edit | Undo: Cmd/Ctrl+Z | Select all: Cmd/Ctrl+A | Copy: Cmd/Ctrl+C |

The candidate has five default groups. Window, PS and Browser remain removed; Douyin moves from the default groups to Media → Douyin. Music retains volume up/down, play/pause, long-OK next track and long-DOWN previous track. Douyin sends plain UP0x52/RIGHT0x4f/DOWN0x51 with UP/OK/DOWN; long OK/DOWN have no tool action, and long UP returns to the media picker. WeRead also uses plain arrows on all four host types. OK sends the keyboard right arrow. Page/chapter/seek behavior depends on the app, mode and focus; Douyin RIGHT is not guaranteed to select the next video. The earlier user confirmation of screenshots and WeRead/Douyin concerned the old dev3 six-group configuration on an unspecified host, not this candidate's new media UI.

The candidate adds Settings row4 Remote display-off (About moves to5). When eligible, display-off begins30 seconds after entering/waking the remote page; short keys still send and do not reset that interval. Dark-screen long OK only wakes and is consumed; lit-screen long-OK actions remain, and long UP still returns. The switch is saved independently in NVS `remote_v1`, without migrating/erasing old settings/configuration/bonds. Existing custom six-group configurations remain supported; nothing removes Douyin automatically. The authorized migration on the now-installed candidate separately removed only the matching old Douyin group and saved the retained five groups/cards through the normal configuration protocol. Candidate `0.3.1-remote-dev2` passed the127-test/2,206-step gate and ESP-IDF6.0.2/F3 build. It is installed; release/deployment verification is in progress. The user accepted media selection/physical order, display-off, dark-screen page turns and long-OK wake-only behavior on the current setup; cold-power/remote_v1 retention, measured power and the full app/platform matrix remain unverified.

For an existing badge: **Connect → Read from badge → Use new default shortcuts (keep cards) → Write and verify**. The new-default-groups button only replaces groups in the current editor and retains that editor's cards. Read first to retain the actual cards stored on the badge. Clicking the button does not automatically read/write the device or save browser storage. Restore defaults resets both draft groups and cards, so it is not a substitute for the card-preserving workflow.

For the published separate offline supplement, extract the complete package and open its `config.html` in desktop Chrome/Edge. Its historical six-group update works on old dev3 without flashing; it does not add the candidate media/display features. Neither page/package automatically migrates NVS `cfg_v1`, and the package contains no personal configuration export. Only explicit Write and verify saves groups; retained cards come from the actual configuration read first.

Historical dev3 configuration evidence: stored NVS configuration takes precedence over defaults, so firmware upgrades do not automatically replace personal groups. The production JS client previously wrote six groups over real USB to dev3 and read them back three times, retaining screenshot/paste, Typeless, CapCut and cards without flashing/changing bonds/partitions/erasing NVS. User confirmation of screenshots and WeRead/Douyin was on an unspecified host and belongs to that old six-group configuration, not all-platform or current-candidate physical acceptance.

Current installed-candidate migration PASS: after the exact app-only flash/verification/reset, actual USB read/edit/write removed only the old Douyin group with matching arrow bindings. The result is Screenshot, Typeless, CapCut, WeRead and Edit; every other group field and card matched the pre-migration configuration. Save/automatic readback and three successive reads agreed. This proves warm-running save/readback. Cold-power and independent `remote_v1` retention remain unverified; current physical user acceptance is recorded separately below.

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

Current media/display gate PASS:37 Node+90 Python=127 checks, zero skips,2,206 replay steps and3 deliberate mutations caught; ESP-IDF6.0.2/F3 build PASS. Candidate `0.3.1-remote-dev2` app is2,011,616 bytes, SHA-256 `b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe`, leaving20,000 bytes in the legacy factory partition. Independent archive verification, source-input SHA comparison and binary version checks passed. The exact app passed authorized app-only flash, application verification and reset. Before reset, partition-table/NVS/PHY/first-assets-sector hashes matched their pre-write values; the entire assets area was outside write/erase ranges and was not read back in full. The installed app and new configuration source are ready for this publication; deployment/release/community outcomes are verified separately. Old v0.3.0/20261028 packages keep their six-group snapshots.

Two bounded observers totaled505/505 real ready samples over about504 seconds: minimum connected heap92,624/largest77,824 bytes,31 successful HID actions/62 notification TX completions, zero reported errors or crashes. BLE CI was7,500µs, latency0 and supervision2,000ms. Notification completion remains distinct from host acknowledgment; this is not a one-hour stability test.

User physical acceptance PASS on the current setup: media selection/physical key order, screen-off, dark-screen page turns, long OK only waking, and headphones/keyboard normal in this round. Independent dark capture completed16 HID actions/32 notification transmissions while screen_off stayed true and animation frame9 remained frozen, with zero related errors; the user repeated the test successfully. Two earlier dark captures also froze animation frames and wake did not increase sent. The old intermittent Bluetooth connection cause remains unresolved. Power measurements, remote_v1 cold-power retention, the full app/platform matrix and original reconnect/three-slot/deep-sleep/one-hour gates remain unverified.

Dev2 adds read-only diagnostics for connection interval (CI), latency, supervision timeout and HID transmission errors. It does not change BLE policy or the configuration protocol. A completed TX is not a host acknowledgment and does not prove that an app executed the action; the Windows Bluetooth fault cause remains unresolved.

Historical shortcut-only gate PASSED:29 Node+73 Python=102 checks,1710 full replay steps and3 deliberate mutations caught; ESP-IDF6.0.2/F3 build PASS. That `0.3.1-shortcuts-dev1` app is1,999,728 bytes and was not flashed/published. Earlier app-response feedback came from the old dev3 configuration update; it does not establish this installed candidate's physical acceptance.

Historical F2 acceptance, not this default-group revision:87 host tests/1710 steps covered shared JS/C validation, production JS-to-C stdio/RAM persistence/fault injection, model and rendering. The production JS client subsequently passed actual USB save/readback/rejections/two resets/20 reads, restoring original configuration. Dev1 dropped-read chunks were detected by length checks; dev2 buffered USB completed the tests. Configured text/card/QR and cold power retention after commit are user/readback verified. Actual browser permission/unplug during transfer/power interruption during commit/hardware fault semantics still need separate acceptance; see [validation](VALIDATION.md) and validation/f2.json.
