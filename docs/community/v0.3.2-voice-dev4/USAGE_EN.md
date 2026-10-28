1. Choose the installation mode
For ESP32-C3/8 MiB AI Passport without PSRAM. To preserve an existing badge's partitions, cards, shortcuts, bonds and templates, use the guarded app-only upgrade after checking the actual device, capacity and partition table. Do not default-flash, install a merged image, or whole-chip erase.
https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.2-voice-dev4
Fixed app: 2,030,864 bytes; SHA256 d748e54395bff10eaa85530d4287198607fc3fcd17f2d1da8250b272b15d1829.
Community full installation starts at 0x0 and replaces the default table/NVS/configuration/bonds/personal templates. Configure and enroll again. That full-install path is not device-tested; it is distinct from accepted app-only installation.

2. Buttons and pairing
Facing the screen, the right-side buttons run top to bottom UP, DOWN, OK; OK is at the bottom. A long press is about 0.5 seconds; release adds no short press. Let the approximately 5.5-second welcome finish or skip with any key. UP/DOWN selects, OK enters, long UP returns.
Choose Pair new device in Connection. Select NABO 工具箱 on the host and follow the passkey or number-comparison prompts. Number comparison requires confirmation on both phone and badge. Choose the correct host type and wait for ready. Three bonds, one active connection; new pairing replaces the oldest bond, which may require that old host to pair again later.

3. Enroll personal commands, then search
Hold bottom OK in the main menu to open voice search. Targets are 读书, 抖音, 音乐, 名片, 拍照, 截图 and 语音输入.
• UP/DOWN selects what to enroll; long OK records one example. Remain quiet for about 300 ms, then say the displayed name once after 请说目标名称. Do not add “open” or “NABO”. Wait for 已保存 and an increased count before the next example. Enroll three per word.
• Existing six-word templates are retained. Add the seventh without re-enrolling the others. Further long OK attempts to replace that word's oldest example. Stop retrying if saving fails: templates share space with configuration/bonds, and maximum-length/widest templates cannot be overwritten indefinitely in every case.
• Short OK recognizes across all enrolled words; selection only chooses enrollment. A match only opens a tool. Typeless/voice input still needs its original button afterwards. Missing 微信读书, 截图 or Typeless/语音输入 groups are reported rather than created automatically.
• Unknown, ambiguous, too-long or capture-error results do not navigate. Long UP cancels and returns. Enrollment allows up to 0.96 seconds of voiced frames, queries up to 1.92 seconds, and each capture has a 3-second wall-clock limit. Say one short command, then pause. Music, speech and clothing noise can interfere; negation or audio replay rejection is not guaranteed.
Capture is on demand, without continuous wake listening or networking. Raw audio is not saved/uploaded; personal templates are not included in public firmware.

4. Six tools
• Shortcuts: UP/DOWN/OK sends the three current actions; lit-screen long OK/DOWN selects next/previous group. Defaults: Screenshot=capture/Esc/paste; Typeless=translate/ask/voice input; CapCut=split/undo/play; WeRead=UP/DOWN/RIGHT; Edit=undo/select-all/copy. Match application shortcuts, focus and reading behavior.
• PPT: previous/next/black-screen toggle; long OK start, long DOWN end. Counts are local.
• Meeting: camera/hand/mute; long OK changes template. Match desktop shortcuts.
• Media: choose Music/Douyin, then OK enters without HID. Music controls volume/playback; lit-screen long OK/DOWN selects next/previous track. Douyin sends UP/DOWN/RIGHT, with no long OK/DOWN tool action. Long UP returns to the picker, then the menu.
• Camera: open a volume-shutter-compatible app. UP chooses 0/3/10 seconds, DOWN five shots, OK shoots/cancels. Check the phone for saved photos.
• Cards: UP/DOWN switches, OK zooms/unzooms; long UP first leaves enlarged QR mode.

5. Screen-off control and configuration
Remote display-off defaults on. Connected shortcut/media tools darken about 30 seconds after entry/wake, without short keys extending the timer. Dark short keys still send. Dark long OK only wakes and consumes the gesture: no group/track action or short OK on release. Lit long OK keeps its tool action; long UP returns and lights the screen. Menu/media selection stays lit.
https://liutupi.github.io/nabo-toolkit/
Desktop Chrome/Edge + USB: close serial monitors, select the correct port, Read from badge, edit, explicitly Write, then verify readback. Opening serial can restart the badge. Configure 1–6 groups/three actions and 1–3 cards; text macros support 64 ASCII characters/newlines and QR payloads 160 UTF-8 bytes. Mac/iPhone and Windows/Android bindings are separate. Browser Save only saves locally.
To restore five defaults while keeping actual cards, read first, select Use new default shortcuts (keep cards), review, then explicitly write. Wi-Fi QR/configuration exports may contain plaintext passwords; do not publish private exports.

6. Legacy compaction and limits
Old templates are not bulk-migrated automatically at boot. If storage needs compaction, stop capture/configuration transactions and explicitly send >tk.voice.compact over USB while on menu/voice. It preserves samples, every coefficient, count and next slot. Only verified readback and a full comparison allow the same word's old record to retire. Stop on error; do not erase NVS or repeatedly retry. Already compact words are skipped.
This round verifies personal navigation, controlled-restart retention of 21 samples and lossless compaction. A real personal-card URL change, controlled-restart readback and phone scan passed; other configuration was retained. The earlier same-content test may be an SDK skip and is recorded separately. An independent SDK copy wrote/read/reinitialized a modified 1,629-byte configuration and a 4,016-byte opaque blob; the latter is not valid maximum-configuration-schema acceptance.
PC-USB headphone stutter occurred intermittently. Battery/external-power comparisons were normal, and PC USB was finally reported currently normal; investigation stopped at the user's request without a known cause or claimed firmware fix. More speakers/noise, full seven-word coverage, cold-power/interruption/Flash faults, extreme capacity/GC, power, long stability and historical platform gates remain unverified. Keep original images; historical UI/key illustrations defer to this text and the real interface.
