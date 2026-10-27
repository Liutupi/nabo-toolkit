<p align="right"><a href="README.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# Host contracts

Run `./tools/validate.sh --static`, or native Windows `./tools/validate.ps1 -Static`, from the repository root. Requires Node.js, Python 3 and a C11 host compiler; the codec tests do not need Pillow/NumPy or ESP-IDF.

- 20 Node tests: pure JS rules, boot/voice/skip timing, passkeys, cancellation, right-side modifiers, camera cadence, PPT timer, wake, FIFO replacement/ignoring old reconnects during pairing, and real inline DOM button wiring in a VM. Three deliberate rule mutations are caught.
- 7 C probe tests: 4,000 input events compared against the JS classifier, uint32 timer wrap, exhaustive secure/subscription readiness, exact keyboard/consumer bytes, disconnected actions, navigation and leading-zero/cancel behavior.
- 8 sprite codec tests: known RLE/delta rows, corrupt/truncated data, bad bounds/palette/timestamps/CRC and exact production frame decoding within budget.
- 7 flash-guard tests: exact app hash/chip/size, partition map/MD5/flags, device security, flash capacity, the measured legacy layout and its smaller app boundary; tests never open a port.
- 4 F0 observer tests: embedded status parsing, privacy field allowlist, exclusion of simulated/disconnected memory samples, and keeping advertising time separate from full boot timing. Two optional comparison checks require physical short OK/long UP and reject stale/cancelled/zero prompt tokens. One reconnect-policy check covers 500/10000ms boundaries and uint32 wrap. The C library is explicitly unloaded before temporary-directory cleanup on Windows. Host policy checks do not prove real reconnect timing.
- `verify_golden.py` re-records1,710 steps byte-for-byte/by SHA256: original1,582 plus128 configured steps, ten pages/six keys/five connection events/four OS types. Default HID table is unchanged.

Current total: **87 (27 Node +60 Python)**. F1's71 remain; F2 adds7 Node schema/client,8 C configuration/protocol/storage,1 custom Chinese-renderer checks. Production JS client communicates with production C parser/protocol/storage through stdio, never a real serial port.

`test_tk_model.py` compares complete production C state/effects/sleepDue for1,710 steps, including variable group/card counts, disabled families,64-character text, consumer keys and shrinking-index clamps. Three deliberate C mutations are caught. The adapter only converts the configuration ABI; JSON parsing/persistence/client behavior is independently tested end to end. Demo bonds exist only in host fixtures; production starts empty/disconnected.

Renderer tests use real fonts/LVGL, covering ten pages/dialogs, wide six-digit passkeys, QR changes, custom CJK fallback and dirty/full pixel equality. Native `validate.ps1 -Stage F2` or POSIX `validate.sh --f2` reconfigures first to fetch pinned LVGL/cJSON. Missing LVGL causes explicit static-only SKIP, not pass; missing cJSON fails. IDF6 does not support MSYS builds. C preview additionally needs Pillow: `python tools/render_toolkit_preview.py --f2`.

RAM NVS/NimBLE providers inject storage failures and synthetic peers to check commit-before-eviction, preservation on failure, F0 migration and staging cleanup. They do not prove RTOS concurrency or physical power-loss behavior. No test opens a serial port. Physical acceptance is tracked in `../docs/VALIDATION.md`; host/build passes do not imply F1 device acceptance.
