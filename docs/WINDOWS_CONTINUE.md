<p align="right"><a href="WINDOWS_CONTINUE.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# Continue on Windows

The private repository is `Liutupi/nabo-toolkit`, branch **main**. All approved start images, original Grok videos, design attempts/prompts/assembly scripts, reviews, RGBA masters, indexed frames, binary sprites, browser atlases, prototype, golden traces, F0 firmware source and pinned dependency metadata are in Git. No image/video needs to be generated again. `docs/validation/assets.json` lists every art/audio/asset file with byte length and SHA256; `python tools/verify_assets.py` checks completeness. `.gitattributes` keeps source/fixtures in LF on Windows and preserves binary media.

Clone into a short path, or pull the existing checkout after preserving its changes:

```powershell
git -c core.longpaths=true clone https://github.com/Liutupi/nabo-toolkit.git C:\nabo-toolkit
cd C:\nabo-toolkit
git status --short --branch
python tools/verify_assets.py
python -m http.server 8770 --directory game-art/toolkit/prototype
```

Open `http://localhost:8770/`. The browser simulates Bluetooth/HID. It already uses the first Grok sprite batch. Up/Down/Enter work; hold 0.5 s for long press. Welcome lasts about 5.5 s and any key skips. Google Fonts and the QR helper currently use external CDNs; allow those for the prototype or use font fallback. The device firmware stays offline.

Read `AGENTS.md`, `docs/HANDOFF.md`, `docs/VALIDATION.md`, `game-art/toolkit/FIRMWARE_PLAN.md` and `UI_DESIGN.md`. The required game skill is from private `Liutupi/nabo-skills` (`nabo-passport-game/SKILL.md`); check/install it in the Windows agent environment. Also check the five Passport skills required by the environment. Their Mac installation paths are not portable. Use only the relevant skill; do not substitute its generic SDK version for the project requirement.

Firmware uses **ESP-IDF 6.0.2**, target **ESP32-C3**, 8 MiB, no PSRAM. Activate that version's environment before building. `firmware/dependencies.lock` and BSP component requirements pin dependencies; `managed_components`, SDK installations, local venvs and build/debug artifacts are regenerated, not copied from Mac. A host C11 compiler plus Node.js and Python is required for the full host gate. Run `./tools/validate.sh` in Git Bash with these tools available, or a Linux/WSL environment; ESP-IDF's RISC-V cross compiler cannot replace the host `cc` used by ctypes tests. WSL USB access needs separate setup—do not assume it sees the Windows device. The Windows native IDF prompt can build using an absolute build path:

```powershell
idf.py -C firmware -B C:\nabo-toolkit\build\f0 -D SDKCONFIG=C:\nabo-toolkit\build\f0\sdkconfig build
```

For host checks separately: `node --test tests/tk_golden/model.test.js tests/tk_golden/prototype.test.js`, `python -m unittest discover -s tests -p "test_*.py" -v`, `python tools/verify_golden.py`. Native Windows needs `cc` (a host compiler producing a loadable Windows library); use the Bash/WSL route if absent. The Python art pipeline additionally uses ffmpeg/ffprobe and `pip install -r tools/requirements-art.txt` in a separate Python 3.11+ venv. Existing assets can be used without these image-processing dependencies.

The exact Mac-built F0 app SHA256 is `ea6789e39fddc8a7063a94d45c6687cf71d61a11eb56c55cb9aa4bcce305074c`. The app is already on the badge. The 40 host tests and complete Mac gate passed. The user confirmed **Mac pairing, paste and volume work**; connected heap was at least 195,604 bytes, largest block 114,688. One actual USB-induced restart auto-reconnected, 701 ms measured from advertising. Repeated boot-to-ready timing remains pending. The serial monitor opens caused `USB_UART_CHIP_RESET` on this setup; account for resets when testing. The user has an iPhone, but its test was deferred when leaving work; **iPhone, Windows and Android pairing remain unverified**. F1 must wait for F0's physical gate unless the user explicitly changes the acceptance scope.

The device's measured legacy partition table differs from the build plan: NVS `0x9000/0x6000`, PHY `0xf000/0x1000`, factory `0x10000/0x1f0000`, FAT assets `0x200000/0x600000`. Existing bootloader reports IDF 5.5.3; the previous Adventure app and current F0 app use IDF 6.0.2. **Preserve this installed table**. F0 does not use assets/files, fits the smaller app partition, and was installed app-only. Do not run unreviewed `idf.py flash`/merged-image flashing: that would replace the table. The guarded installer supports this measured map and checks actual app capacity. Enumerate the Windows COM port and device identity afresh; `/dev/cu.usbmodem212401` and private Mac receipts are not Windows configuration. New device/write scopes require their own consent. Never erase the chip to bypass an NVS error.

For the first Windows pairing at home, hold DOWN for 0.5 s to advertise for 60 s. After pairing, press OK to open the test, then DOWN to switch the saved Mac preference to Win / phone before testing OK/Ctrl+V and UP/volume. Leaving Mac mode would send the Windows modifier instead of Ctrl. If the Mac is nearby, disconnect just this NABO device there to avoid it reclaiming the link; do not delete its bond. Re-enter the test with OK after a serial-induced reset.

Next: test Windows pairing/clipboard/volume and iPhone pairing/volume, measure connected heap and repeated restart reconnect under 3 s, obtain Android coverage, then enter F1 after the agreed gate. Voice B2, UI styleboard B6, the second Grok action batch and F3 art integration remain pending. Do not regenerate first-batch art or claim JS–C application replay is already complete.

Private MAC/bonding data, raw device logs, credentials and build/ELF/MAP bundles are intentionally excluded from Git; sanitized results and hashes are in `docs/validation/f0.json` and `VALIDATION.md`. The historic Grok delivery ZIP may mention a Mac destination path: use repository-relative `game-art/toolkit/art/video/batch1/` on Windows.

Suggested continuation prompt:

> Continue NABO Toolkit on Windows from this checkout. First read AGENTS.md, docs/HANDOFF.md, docs/WINDOWS_CONTINUE.md and docs/VALIDATION.md. Run the asset inventory check; preserve user changes. All first-batch artwork/videos/sprites and the F0 source are already present. The badge runs verified F0; Mac pairing/paste/volume passed. Start with Windows and iPhone F0 tests, then remaining reconnect/memory/Android acceptance. Preserve the badge's measured legacy partition table, enumerate the COM port again and obtain any required flashing consent. Do not start F1 before its F0 gate, redraw NABO, change author default bindings, or commit private device data.
