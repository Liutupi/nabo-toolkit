<p align="right"><a href="README.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# NABO Toolkit

An offline Bluetooth HID remote for the FoloToy AI Passport (ESP32-C3): presentation controls, meeting shortcuts, media, camera shutter, configurable shortcuts/Typeless and QR contact cards.

Current checkpoint: browser layout/passkey simulation and the first Grok sprite batch are integrated. **F0 Bluetooth probe firmware builds and passes 40 host tests; physical acceptance is pending.** The full F1 application remains gated on pairing, reconnect and heap measurements. Welcome animation now plays completely, entering the menu at about 5.5 seconds, with any-key skip.

Read [handoff](docs/HANDOFF.md), [firmware plan](game-art/toolkit/FIRMWARE_PLAN.md), [UI design](game-art/toolkit/UI_DESIGN.md) and [validation](docs/VALIDATION.md). Maintenance rules: `AGENTS.md`.

```sh
python3 -m http.server 8770 --directory game-art/toolkit/prototype
./tools/validate.sh --static
# Activate ESP-IDF 6.0.2 before the complete build gate:
./tools/validate.sh
```

The browser prototype simulates Bluetooth/HID. F0 firmware usage and controls are in [firmware/README.md](firmware/README.md); host contracts in [tests/README.md](tests/README.md); video provenance and binary format in [sprites/README.md](game-art/toolkit/sprites/README.md). Original Grok sources remain unmodified, with manual review notes and automatic all-frame decoding records.

No flashing, Git commit/push or publishing occurs during validation. This project is not affiliated with FoloToy. NABO imagery and art assets are not licensed with the source code; reused BSP licensing is retained separately.

[Windows continuation](docs/WINDOWS_CONTINUE.md) · `python tools/verify_assets.py` checks all 364 source/intermediate/runtime asset files.
