<p align="right"><a href="README.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# Host contracts

Run `./tools/validate.sh --static` from the repository root. Requires Node.js, Python 3 and a C11 host compiler; the codec tests do not need Pillow/NumPy or ESP-IDF.

- 18 Node tests: pure JS rules, boot/voice/skip timing, passkeys, cancellation, right-side modifiers, camera cadence, PPT timer, wake and real inline DOM button wiring in a VM. Three deliberate rule mutations are caught.
- 7 C probe tests: 4,000 input events compared against the JS classifier, uint32 timer wrap, exhaustive secure/subscription readiness, exact keyboard/consumer bytes, disconnected actions, navigation and leading-zero/cancel behavior.
- 8 sprite codec tests: known RLE/delta rows, corrupt/truncated data, bad bounds/palette/timestamps/CRC and exact production frame decoding within budget.
- 7 flash-guard tests: exact app hash/chip/size, partition map/MD5/flags, device security, flash capacity, the measured legacy layout and its smaller app boundary; tests never open a port.
- `verify_golden.py` re-records all 1,559 reference steps in a temporary folder and compares three files byte-for-byte and by SHA256. Coverage includes ten pages, six key events, five connection events and all four OS types. `hid_tables.json` exports original and resolved defaults without modifying author bindings.

The full application C model is not implemented in F0. These JS fixtures and the C input differential test are not a claim of full JS–C state replay or hardware compatibility. Physical acceptance is tracked in `../docs/VALIDATION.md`.
