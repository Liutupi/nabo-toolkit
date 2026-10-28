1. Choose installation mode first
ESP32-C3/8MiB AI Passport, no PSRAM. Community install writes a complete image at0x0, replacing partitions/NVS/settings/bonds; that full-install path remains untested on hardware. For existing data/layout/assets, use the guarded app-only upgrade, inspect the actual target/capacity/partitions and back up first; do not whole-chip erase or use default flash.
https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.1-remote-dev2
Fixed app:2,011,616 bytes, SHA-256 b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe. App-only flash/verification/reset passed; this does not validate full installation.

2. Physical keys and pairing
Facing the screen, right-side keys run from top to bottom UP, DOWN, OK; OK is the bottom key. Screen/editor rows follow that order. Let the5.5s welcome finish or press any key. UP/DOWN selects and OK enters.
In Connection, choose Pair new device and OK. Select NABO 工具箱 in host Bluetooth settings, follow passkey/comparison prompts and confirm matching numbers on both sides when required. Choose Mac, Windows, iPhone/iPad or Android; wait for ready. Disconnect competing hosts. Three bonds, one active connection; successful new pairing replaces the oldest bond without clearing NVS.

3. Tool keys
Long press is about0.5s; release does not add a short action. Long UP returns; media tools first return to their picker, then the menu. Enlarged QR first exits zoom.
• Shortcuts: UP/DOWN/OK sends current actions; lit-screen long OK/DOWN changes next/previous group. Defaults in physical order: Screenshot=capture/Esc/paste; Typeless=translate/ask/voice input; CapCut=split/undo/play; WeRead=UP/DOWN/RIGHT; Edit=undo/select-all/copy. Typeless needs matching desktop software. WeRead chapter behavior depends on app/mode/focus. Old saved six-group configurations remain compatible.
• PPT: previous/next/black-screen toggle; long OK start, long DOWN end. Counts are local.
• Meeting: camera/hand/mute; long OK changes template. Desktop only; match app bindings.
• Media: select Music/Douyin, then OK enters without HID. Music=volume up/down/play-pause; lit-screen long OK/DOWN next/previous track. Douyin=UP/DOWN/RIGHT; long OK/DOWN have no tool action. RIGHT may seek, not change video.
• Camera: open a volume-key-compatible camera; UP delay0/3/10s, DOWN five shots, OK shoot/cancel. Check saved photos on the phone.
• Cards: UP/DOWN switches, OK zooms/unzooms.

4. Screen-off control
Settings → Remote display-off defaults on. Connected shortcut/media tool pages darken30s after entry/wake without short keys extending the timer; pairing/OS dialogs and menu/media selection stay lit.
Dark UP/DOWN/OK still send. Dark long OK only wakes and is consumed, without group/track/HID action or a short OK on release. Lit-screen long OK retains its action. Long UP returns and lights the screen. Disable the switch to keep remote pages lit. It uses independent remote_v1, leaving settings_v1/cfg_v1/bonds intact; real cold-power retention and measured savings remain unverified.

5. Configure shortcuts/cards
https://liutupi.github.io/nabo-toolkit/
Use the matching Release offline page if needed; extract it completely and open config.html. Older published packages retain their old content.
Desktop Chrome/Edge + USB: close serial monitors, connect/select the correct port, Read from badge, edit, Write and verify. Opening serial may restart it.1–6 groups/3 actions,1–3 cards; Mac/iPhone and Windows/Android bindings are separate. Use manual entry for intercepted chords; text macros allow64 ASCII/newline characters. QR limit160 UTF-8 bytes.
For five defaults while keeping actual cards: read first, click Use new default shortcuts (keep cards), review, explicitly write. No automatic device write or deletion of old saved Douyin groups occurs. Only matching readback confirms save; Browser Save is local. After interruption, reconnect/read before rewriting. Wi-Fi QR joins the phone to a network; the badge stays offline and exports contain plaintext passwords—do not share private files.

6. Acceptance limits
127 host tests/2,206 steps pass. User acceptance covers current media/key order, screen-off, dark page turns, long-OK wake-only and normal headphones/keyboard coexistence in this round. Independent dark capture completed16 HID actions/32 transmissions with screen_off continuously true, animation frame9 frozen and zero related errors; the user repeated it successfully. TX completion is not host ACK; the older intermittent connection cause remains unresolved.
Full app/platform coverage, remote_v1 cold-power retention, power/runtime measurements,3-slot stress, long stability, full installation, reader/TV and the3s reconnect target remain incomplete. Test bindings in a blank area before work. Original five images remain; historical key/UI illustrations defer to this text and the actual UI.
