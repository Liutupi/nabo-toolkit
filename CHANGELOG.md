# Changelog

## v0.3.0-f3-dev3 — 2026-10-28 (public test release)

- F1 tools and Chinese UI; F2 configurable shortcut groups/cards, CRC-checked USB save/readback and NVS persistence.
- Original seven Grok animations, distinct tool costumes, full welcome and dedicated Dreamina startup voice.
- F3 dev3 adds a5ms attack/release envelope; user accepted clean key tones and startup audio, full welcome and tool animations.
- Public configuration page and offline configurator; no configuration upload endpoint.
- Exact accepted app1,999,600 bytes, SHA256 `d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`; legacy factory spare32,016 bytes.
- Build PASS;100 host tests/1710 steps PASS; device acceptance PARTIAL. Prior timing FAIL and remaining compatibility/stability tests are retained in docs/validation/f3.json.
- App-only upgrade at0x10000; no repartitioning, merged installation image, device dumps, NVS backups or private logs in release downloads.
