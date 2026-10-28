# Personal offline commands (v0.3.2-voice-dev4 experimental release)

Enroll your own recordings for seven fixed Chinese commands: **读书** (reading), **抖音** (Douyin), **音乐** (music), **名片** (cards), **拍照** (camera), **截图** (screenshot), and **语音输入** (voice input). This is personal acoustic template matching, not general speech transcription or identity verification. It records only when started with a button, without continuous wake-word listening, networking, or uploading audio. Dev4 passed the requested bounded voice, lossless compaction and controlled-restart retention checks. The initial reset cause, broader speaker/noise coverage and long stability remain open. Check [HANDOFF](HANDOFF.md) and [VALIDATION](VALIDATION.md) for the actual scope; one user's acceptance is not a general accuracy result.

The physical buttons on the right are **UP, DOWN, OK**, from top to bottom. Hold the bottom OK button in the main menu to open voice search. Existing tool actions and the dark-screen long-OK wake behavior remain unchanged.

## Enroll first

1. In a quiet place, wear the badge as you normally would. Use UP/DOWN to select a target.
2. Hold OK once. Stay quiet during “准备采音” (preparing), then say the selected command naturally when “请说目标名称” appears, such as “读书” or “语音输入”. Do not add “open” or “NABO”.
3. Wait for “已保存” (saved) and the increased count. Repeat until that target shows `3/3`, then enroll the other targets. Existing recordings for the first six commands are retained; enroll the new voice-input target separately without re-enrolling the others.
4. Once a word has three templates, another long OK attempts to replace its oldest template. The word is read back after every save, including error returns. Only matching readback confirms success and installs templates in RAM; an unconfirmed record is reported as damaged or unknown, without blindly rewriting old data or erasing NVS. An error return does not guarantee that old Flash contents are unchanged. Real Flash faults and power loss require another readback check.

Background preparation takes about 300 ms. Each capture has a 3-second wall-clock limit. Enrollment accepts at most 0.96 seconds of voiced frames; a recognition query accepts at most 1.92 seconds. Long phrases, slow speech, or several commands in one capture can be rejected as too long; a truncated prefix is not accepted. Say one short command, then pause. The four-character voice-input command also has the enrollment limit, and usability at a natural speaking pace still needs a device check.

## Recognize and open a page

Press OK briefly on the voice page, wait for “请说口令” (say a command), and say an enrolled command. Recognition compares all enrolled targets; the highlighted card selects only what to enroll. A match opens the corresponding page and **does not send a screenshot, shutter, playback, or other HID action**. Use the existing tool buttons afterwards.

Reading and screenshot require the personal shortcut groups named “微信读书” and “截图”. **Voice input only opens the “Typeless” or “语音输入” shortcut group. Press its existing tool button afterwards to act; recognition does not start computer recording or send a voice-input shortcut.** If a group is missing, the badge reports it without creating or modifying configuration. Douyin and music open their respective media modes; cards and camera open the existing pages.

Unknown, ambiguous, too-long, capture-error, and operation-error results do not navigate. Press OK to retry. Selection and repeated starts are blocked during capture; hold UP to cancel and return to the menu. Remain quiet during preparation. Music, television, conversation, clothing noise, and local speaker sounds can affect capture. Template matching does not understand negation and cannot guarantee rejection of a recording being played back.

## Storage and validation limits

The dev3 candidate losslessly packs templates and journals each word in two independent slots. It verifies a new slot before retiring the previous copy of that same word, and still reads the six-word legacy format. A failed space precheck rejects the new enrollment while retaining confirmed examples. Storage is shared with personal configuration and bonds, so the longest possible commands are not guaranteed unlimited re-enrollment; stop retrying if saving fails.

The badge stores acoustic templates, without saving or exporting raw audio. Their new records are separate from personal cards/shortcuts, settings, and Bluetooth bonds; enrollment requires no NVS erase or partition change. Public firmware contains no personal templates, so another user must enroll their own.

Host simulation and builds check algorithms, state, boundaries, and fit. Personal recognition, environmental rejection, cancellation, cold-power persistence, BLE coexistence, peak memory, and power use require separate device tests. A matching score is not a calibrated accuracy percentage, and acceptance by one person does not establish support for every speaker or environment.
