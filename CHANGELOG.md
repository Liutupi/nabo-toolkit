# Changelog

## v0.3.2-voice-dev4 — 2026-10-28 (experimental public test)

- Add on-demand, personally enrolled offline navigation for seven fixed Chinese commands; voice input opens Typeless without emitting its hotkey.
- Align/copy template counts bytewise, check heap/stack, and separate NVS reads from matcher allocation. No reset occurred in the bounded dev4 checks; the original cause is not claimed fully established.
- Losslessly pack per-word A/B records; check capacity before writes. Explicit USB maintenance preserves all21 recorded examples, coefficients and rotation, recovering available NVS entries47→251 on the device. Configuration writes now precheck space.
- 213 host checks,2,722 JS–C steps,3 mutations; exact accepted app2,030,864B, SHA256 `d748e54395bff10eaa85530d4287198607fc3fcd17f2d1da8250b272b15d1829`. Original art/font assets unchanged.
- Full first install, broad recognition/noise/long-stability gates and changed-payload physical configuration writes remain unverified. Intermittent PC-USB headphone stutter is unresolved; no BLE parameter or driver change. See `docs/RELEASE_v0.3.2-voice-dev4.md`.

## v0.3.0-f3-dev3 — 2026-10-28 (public test release)

- F1 tools and Chinese UI; F2 configurable shortcut groups/cards, CRC-checked USB save/readback and NVS persistence.
- Original seven Grok animations, distinct tool costumes, full welcome and dedicated Dreamina startup voice.
- F3 dev3 adds a5ms attack/release envelope; user accepted clean key tones and startup audio, full welcome and tool animations.
- Public configuration page and offline configurator; no configuration upload endpoint.
- Exact accepted app1,999,600 bytes, SHA256 `d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`; legacy factory spare32,016 bytes.
- Build PASS;100 host tests/1710 steps PASS; device acceptance PARTIAL. Prior timing FAIL and remaining compatibility/stability tests are retained in docs/validation/f3.json.
- App-only upgrade at0x10000; no repartitioning, merged installation image, device dumps, NVS backups or private logs in release downloads.
