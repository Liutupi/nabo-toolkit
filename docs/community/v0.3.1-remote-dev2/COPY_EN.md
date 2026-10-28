NABO Toolkit · Pocket Bluetooth Remote
v0.3.1-remote-dev2 adds Music/Douyin selection and screen-off remote control, retaining the original seven NABO animations, full welcome and dedicated startup/key audio.

Six tools on AI Passport, using the physical top-to-bottom order UP, DOWN, OK:
1. Shortcuts: five defaults—Screenshot, Typeless, CapCut, WeRead and Edit. Screenshot uses UP capture, DOWN Esc, OK paste; WeRead sends UP/DOWN/RIGHT arrows, with chapter behavior depending on the app. Edit is undo/select-all/copy. Configure1–6 groups with three actions, left/right modifiers, media keys or up to64 ASCII characters/newlines. Mac/iPhone and Windows/Android bindings are separate. Typeless triggers existing desktop software; the badge does not record voice. Old personal six-group configurations are not automatically overwritten.
2. PPT: previous/next page, OK black-screen toggle, long OK start, long DOWN end, with local time/page counts—not the computer's real slide state.
3. Meetings: UP camera, DOWN hand, OK mute toggle; long OK selects Tencent Meeting, Feishu, Zoom or Teams templates. Desktop only; shortcuts must match the app.
4. Media: select Music or Douyin, then OK enters without sending HID. Music keeps volume, play/pause and lit-screen long OK/DOWN next/previous track. Douyin sends UP/DOWN/RIGHT; long OK/DOWN have no tool action. RIGHT may seek, not select the next video. Long UP returns to the picker, then the menu.
5. Camera: open a phone camera supporting volume-key shutter. UP selects0/3/10s, DOWN five shots, OK shoots/cancels countdown. Sending a key does not confirm a saved photo.
6. Cards:1–3 QR cards; UP/DOWN switches, OK zooms. URLs/text/Wi-Fi payloads up to160 UTF-8 bytes. Wi-Fi QR connects the phone, while the badge stays offline. Passwords remain in QR/configuration exports.

Screen-off remote control is enabled by default. Eligible connected shortcut/media tool pages darken30 seconds after entry/wake; short keys still send and do not extend that interval. Dark-screen long OK only wakes and is consumed: no group/track/short-OK action. Lit-screen long OK keeps its tool function. Long UP returns and lights the screen. Menu/media selection stays lit. Rendering/animation/LCD transfers stop while BLE/buttons/USB remain active; this is separate from deep sleep. No measured battery-saving percentage is claimed.

Configuration: https://liutupi.github.io/nabo-toolkit/
Desktop Chrome/Edge + USB: connect, read actual configuration, edit, then Write and verify. To replace defaults while keeping actual cards, read first, choose Use new default shortcuts (keep cards), then explicitly write. Browser Save is local only. A matching offline page is in this Release. Three Bluetooth bonds, one active host; successful new pairing replaces the oldest bond.

ESP-IDF6.0.2/ESP32-C3/8MiB/no PSRAM;127 host tests,2,206 JS–C steps and3 mutations pass. The fixed app passed authorized app-only flash/verification/reset. A separately authorized migration removed only the matching old Douyin group and retained other groups/cards with repeated USB readback. The user accepted media selection/key order, screen-off, dark page turns and long-OK wake-only; headphones/keyboard were normal in this round. Independent dark capture completed16 HID actions/32 notification transmissions with screen_off continuously true, animation frame9 frozen and zero related errors; the user repeated it successfully. TX completion is not host ACK; the older intermittent Bluetooth connection cause remains unresolved. Full app/platform coverage, cold-power persistence, power measurements, long stability,3s reconnect and reader/TV compatibility remain incomplete.

Community installation writes a complete image at0x0 and replaces partitions/NVS/settings/bonds. Full-image installation is still not device-tested. To preserve data/layout, use the guarded app-only upgrade instead:
https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.1-remote-dev2
Source: https://github.com/Liutupi/nabo-toolkit

The original five uploaded images remain unchanged. Older UI/key layouts in them are historical illustrations; this text and the actual UI take precedence. Guides are C host previews, not hardware photos. Independent project, not affiliated with FoloToy. Source MIT; NABO creative assets excluded.
