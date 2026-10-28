NABO Toolkit · Say a command, find your tool
v0.3.2-voice-dev4 | Public experimental test version

Turn an AI Passport into a remote for reading, video, music, slides, meetings, photos and QR cards. This version adds personal offline voice search. Enroll three examples each for seven fixed Chinese commands: 读书 (reading), 抖音 (Douyin), 音乐 (music), 名片 (cards), 拍照 (camera), 截图 (screenshot), and 语音输入 (voice input). Then press OK on the voice page and say an enrolled command to open its tool. Recognition only navigates: use the existing buttons afterwards to act. It does not automatically take a screenshot or photo, start playback, or send a shortcut.

Hold the bottom OK button in the main menu to open voice search. Capture starts only on request, without continuous wake-word listening, networking or uploading raw audio. Personal acoustic templates stay on the badge; public firmware includes no author's templates, so each user enrolls their own. This is personal short-command matching, not general transcription, free conversation or identity verification. Voice input opens the Typeless/voice-input group; the desktop application and matching shortcuts are still required.

The original six tools remain:
1. Shortcuts: five defaults—Screenshot, Typeless, CapCut, WeRead and Edit. Screenshot uses UP capture, DOWN Esc, OK paste; WeRead sends UP/DOWN/RIGHT arrows, with page/chapter behavior determined by the application. Configure 1–6 groups with three actions, chords, media keys or up to 64 ASCII characters/newlines. Mac/iPhone and Windows/Android bindings are separate. Existing personal configurations are not automatically overwritten.
2. PPT: previous/next page, black-screen toggle, long OK start and long DOWN end. Time/page counts are local, not the computer's real slide state.
3. Meetings: camera, hand and mute templates for Tencent Meeting, Feishu, Zoom and Teams. Match the desktop application's shortcuts.
4. Media: choose Music or Douyin. Music controls volume, play/pause and tracks. Douyin sends UP/DOWN/RIGHT; RIGHT can seek rather than change videos, depending on the application and focus.
5. Camera: use a phone camera supporting volume-key shutter, with 0/3/10-second delay and five shots. Check the phone to confirm saved photos.
6. Cards: 1–3 QR cards with URLs, text or Wi-Fi payloads. UP/DOWN switches, OK zooms. A Wi-Fi QR joins the phone to a network; the badge stays offline. Passwords remain in the QR and exported configuration.

The complete welcome, startup voice, key sounds and tool animations retain the original assets. Physical right-side keys run top to bottom UP, DOWN, OK. Connected shortcut/media tools can darken after 30 seconds while short keys keep working. Dark-screen long OK only wakes; long UP returns and lights the screen. Settings can disable this feature. No unmeasured battery-saving percentage is claimed.

Configuration: https://liutupi.github.io/nabo-toolkit/
Use desktop Chrome/Edge and USB: read the badge first, edit shortcuts/cards, explicitly write, then verify readback. Browser Save is local only. Three Bluetooth bonds, one active host; successful new pairing replaces the oldest bond.

Lossless compact templates, independent A/B slots and space checks protect confirmed examples when storage is insufficient. Legacy compaction requires an explicit USB command; it does not run automatically at startup or rotate samples. 213 host tests, 2,722 JS–C steps and three mutation checks pass. This round includes personal navigation, controlled-restart retention of 21 samples and exact feature preservation during compaction. These results are not a multi-user or all-environment accuracy guarantee.

To preserve data, use the guarded app-only upgrade:
https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.2-voice-dev4
Community full installation writes at 0x0, replaces the default partition table and resets NVS, configuration, bonds and personal templates. Reconfigure and enroll afterwards. Full installation remains untested on hardware.

Known limits: intermittent headphone stutter occurred with the badge on PC USB. Battery/external-power comparisons were normal, and the user finally reported PC USB currently normal too. Investigation stopped at the user's request; no BLE parameters or driver were changed, and the cause is unresolved. Longer stability, more speakers/noise, the full seven-command matrix, cold power-off/Flash faults, extreme capacity/GC, power and historical platform gates remain unverified.

Reuse the original five images without replacement or re-upload. Older UI/version illustrations defer to this text and the actual interface. Independent project, not affiliated with FoloToy. Source MIT; NABO creative assets have a separate scope.
