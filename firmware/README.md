<p align="right"><a href="README.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# NABO Toolkit F0

This is the Bluetooth feasibility probe, before the full tool firmware. It reuses the Adventure BSP, direct renderer and text reader, with an independent diagnostic screen. No game/map/menu shell is included. English ASCII labels use enabled Montserrat fonts; the Chinese Bluetooth name is not LCD text.

Use ESP-IDF **6.0.2**, ESP32-C3, 8 MiB flash, no PSRAM. The existing NVS/PHY/factory/assets/files partition boundaries and `ai-passport-nabo` board identity are preserved. Application code uses integers and no IRAM attributes. No Wi-Fi stack is initialized.

From the repository root after activating IDF:

```sh
./tools/validate.sh --static
./tools/validate.sh --firmware
./tools/validate.sh
```

The complete gate starts an isolated configuration from tracked defaults, removes macOS AppleDouble metadata from managed C sources, builds, merges, checks image offsets/partition MD5/overlaps, and freezes a hash-verified bundle under `build/firmware/<merged-sha256>/`. Dependencies are locked. BSP provenance/license is in `LICENSE.FoloToy`; renderer/text provenance is `nabo-adventure/firmware/main/adv_{gfx,shapes,text}`.

| Input | Effect |
|---|---|
| Menu OK | Open Bluetooth test |
| Test UP / OK | Volume up / Cmd+V (Mac) or Ctrl+V (Windows/phone) |
| Test DOWN | Switch Mac/Windows preference; save in `nabo_tk` |
| Hold UP 500 ms | Back; cancel current pairing if active |
| Hold DOWN 500 ms | Open pairing for 60 seconds |
| Hold OK 500 ms | Reconnect to the last peer |

With no saved peer, boot opens pairing for 60 seconds. Otherwise it starts 10 seconds of low-duty directed advertising, then only accepts the last peer through the whitelist. The screen shows all six passkey digits, including leading zeros. It never logs a passkey or peer address. Pairing uses DisplayOnly, bonding, MITM and secure connections; the HID sender requires authenticated encryption and both report subscriptions. A 64-entry queue sends down → 45 ms → up → 35 ms. Disconnect invalidates queued/in-flight work by generation. Failed key-up retries then disconnects to prevent stuck modifiers.

F0 persists one last peer and OS preference, while NimBLE retains up to three bonds. The full three-slot UI, tools, boot animation, configuration import, voice and sleep belong to later stages. UI alone owns the model; button/BLE/serial producers only enqueue events. The F0 model is intentionally separate from the future full JS–C port.

USB serial commands: `>tk.status`, `>tk.key=up|down|ok|long_up|long_down|long_ok`, `>tk.pair`, `>tk.reconnect`, `>tk.test=1|0`. Test mode suppresses HID; it is not hardware acceptance. `ready_ms` measures from the advertising attempt, so compare boot timestamps too when checking the three-second reconnect target.

No flashing is part of the build gate. `tools/flash_candidate.py` defaults to local image inspection. Its explicit `upgrade` mode requires the expected device MAC and app SHA256, checks ESP32-C3/security/8 MiB and either the planned map or the measured legacy Adventure map (factory 0x10000/0x1f0000, FAT assets 0x200000/0x600000) on the same connection, checks the app against the actual factory capacity, writes only the app at `0x10000`, verifies it, and keeps a private receipt. It never erases the whole chip or requires a full-flash backup. Device identification and user approval must precede its use. A merged image belongs at `0x0` and may reset stored data; do not substitute it for an app-only update.

See [validation](../docs/VALIDATION.md) for the exact artifact identity and pending F0 device checks. F1 is gated on successful pairing, reconnect and heap measurements.
