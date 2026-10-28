NABO Toolkit turns AI Passport into a pocket Bluetooth HID remote with six tools: configurable shortcuts, presentation controls and local timer, meeting shortcut templates, media controls, delayed camera shutter/five-shot burst, and up to three QR cards. Original NABO animations, a complete welcome and dedicated startup/key audio are included.

Configure shortcuts and cards at https://liutupi.github.io/nabo-toolkit/ using desktop Chrome/Edge and USB: connect, read the current configuration, edit, then write and verify. Supports1–6 groups with three actions each, platform-specific key combinations, media keys and printable ASCII text macros up to64 characters. Browser Save only saves local edits. Wi-Fi QR codes let a phone join that network; the badge itself stays offline. Passwords are included in QR/configuration exports.

Store up to3 Bluetooth bonds, with one active connection. A successful new pairing replaces the oldest bond. Typeless actions only trigger the shortcuts configured in your existing desktop software; the badge does not record voice. Meeting templates and camera volume-key behavior must match the host application. HID sends commands but cannot read application status.

Public test version v0.3.0-f3-dev3. Build,100 host tests and1710 JS-C replay steps pass. User acceptance covers the final app's animations and audio; not every host/app, reconnection target or full-install path has been physically tested. Reader/TV support remains unverified.

Important: community installation writes a complete image at0x0 and resets the partition table/NVS/settings/Bluetooth bonds. The complete image contains the same accepted app and passes build/layout/content checks, but full-image installation is not device-tested. To preserve existing data/layout, use the guarded app-only upgrade from the GitHub Release instead:
https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.0-f3-dev3

Cover is a gameplay illustration; UI guide images are C host-renderer previews, not hardware photographs. Independent community project, not affiliated with FoloToy. Source MIT; NABO creative assets excluded.
