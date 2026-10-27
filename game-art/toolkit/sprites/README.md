<p align="right"><a href="README.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# First-batch sprites

Seven original Grok MP4 files remain in `../art/video/batch1/`. Automatic decode covers all 535 frames; contact sheets every 0.25 seconds, approved/first/last heads and source-bound manual notes are in `../art/qa/batch1/`. The manual result is PASS_WITH_NOTES: the welcome remote briefly approaches the lower face and the meeting nod is deeper than requested. Both retain the cap/face/props in reviewed samples.

`tools/review_toolkit_video.py` and `tools/build_toolkit_sprites.py` run from the repository root (Python 3, ffmpeg/ffprobe, Pillow 12.1.0, NumPy 2.4.1). The builder rejects changed source hashes or a missing manual review. Original files are never overwritten. It keys green without face-smoothing filters, applies one fixed full-canvas transform to 256×256 RGBA, then fixed bust/head crops. No per-frame bounding-box scaling is used. The final anchor is bottom center.

Welcome: eight timed frames, 4,042 ms, 115×150. Each of six idle loops: twelve frames, 3,000 ms, 84×110. Base also supplies a 64×64 circular avatar. The duplicate 3-second closing frame is omitted. Index zero is transparent; each action shares one palette of 63 opaque RGB565 entries plus transparency. Edge RGB is composited toward `#14203A` before indexing. Quantization thresholds are mean absolute channel error ≤12 and max ≤96. The lossless codec comparison is against the indexed target frames, not the original RGBA master; quantization is separately measured in `manifest.json`.

The eight `.tks` files total **405,362 bytes**, within the 1 MiB first-batch budget. Every decoded pixel equals its indexed target (zero differences), and frame CRCs verify decoded content. Browser atlases in `../prototype/assets/sprites/` use the same frames/palettes and are wired into the prototype. The C decoder/integration, physical LCD colors/frame rate and voice remain pending F3; F0 does not include these assets.

Binary format (little endian), version `TKSPR1\0\0`:

- Header `<8s4H2I>`: magic, width, height, frame count, palette count (=64), duration ms, loop flag.
- 64 RGB565 `uint16` palette entries; index 0 transparent.
- Per-frame `<5I>` index: time ms, absolute payload offset, payload bytes, decoded CRC32, key flag.
- Payload: `height+1` uint32 row offsets relative to payload start, followed by rows.
- Tokens: count = `(token & 127)+1`. Key frame high bit: repeat one following palette index; low bit: literal indices. Delta frame high bit: skip unchanged pixels from previous frame; low bit: changed literals.

Decoder bounds-checks headers, timestamps, row tables, indices, palette range, first key frame and CRC. Eight codec tests include corrupt/truncated data. Never mirror the frames; cap branding is directional.
