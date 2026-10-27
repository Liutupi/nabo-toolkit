# r1b 内置 imagegen 编辑提示词

模式：内置参考图编辑，未用 API/CLI 回退。最终图使用原参考头部合成，原始生成图片不直接作为首帧。

## S0_base

输入：`../S0_edit_input.png`。

```text
Use case: identity-preserve outpainting of body ONLY. This is a 1024x1024 production character keyframe. The supplied image already has NABO's exact head at its final size and location. Keep the head completely unchanged: do not enlarge, shift or redraw face, thin round glasses, hair, white cap, blue heartbeat NABO emblem. The cap top is y60 and the chin is about y500. Keep that exact size; the face must NOT become larger.
Complete ONLY the clothing/body BELOW THE NECK: continue the existing white doctor's coat and navy scrubs down to the WAIST at the bottom of the square frame. Keep the exact stethoscope and small NABO chest badge. Do not alter the outfit identity. Both arms and hands must be visible: relaxed bent elbows, hands lightly resting together at upper waist around y820, fingers simple, no held object. The whole character body including elbows should fit within x230 to x794 (about 55% frame width); leave plenty of clear green on both sides for later waving. Head width and head-to-body width follow the provided image. No legs, hips or lower-body extension: bottom crop at waist.
Same 2D cartoon/cel shaded illustration as the reference, dark colored outlines, no white sticker outline. No green in clothes. Background perfectly flat solid #00B140, no gradient, shadow, floor, scenery or extra text. Front view, centered, one character. Do not mirror the cap mark. Fill the blank lower part with the completed torso and hands, not with a larger head.
```

## S0R_remote

输入：本轮完成的 `../S0_base.png`。

```text
Use case: identity-preserve clothing and prop edit. Edit the supplied NABO waist-up portrait in place. Add ONLY a large white handheld remote in the character's RIGHT hand (viewer LEFT), held upright at chest height below the face. A few large dark blue circular buttons, no text, logos, display or symbols. The right arm bends naturally at elbow to hold it; the other hand rests low at waist. Keep the white doctor's coat, navy scrubs, stethoscope and NABO badge the same as input. Keep both hands and elbows fully within the frame.
Keep the EXACT original head shape, facial features, eyes, thin round glasses, hair, white cap and unmirrored blue heartbeat NABO emblem. Do not alter, enlarge or shift the head. Cap top stays near y60/1024, chin near y500. Keep the wider WAIST-UP framing: bottom cuts at waist at the BOTTOM EDGE, no legs or hips; character and elbows occupy roughly the central 55% of frame, leaving green margins for waving. No floating cutout above bottom, torso must continue to bottom edge.
Square 1024x1024. Solid perfectly uniform #00B140 green background, no gradient, shadow or ground. Same 2D cartoon/cel shading, dark colored outlines, no white sticker border. No green clothing or props. No extra accessories, no mirroring, no new text, no montage.
```

## S1_ppt

输入：本轮完成的 `../S0_base.png`。

```text
Use case: identity-preserve clothing and prop edit. Edit the supplied NABO waist-up portrait in place. Change ONLY the outfit to the previously selected B palette: dark CHARCOAL blazer (#34313E), pale powder BLUE shirt (#DCE8F2), no tie. Remove the doctor's stethoscope and chest badge. Put a simple slim BLACK presentation clicker in the character's RIGHT hand (viewer LEFT), upright at mid-chest height below the face. Other hand relaxed at waist. Keep both hands and elbows fully inside the frame.
Keep the EXACT original head shape, facial features, eyes, thin round glasses, hair, white cap and unmirrored blue heartbeat NABO emblem. Do not alter, enlarge or shift the head. Cap top stays near y60/1024, chin near y500. Keep the wider WAIST-UP framing: bottom cuts at waist at the BOTTOM EDGE, no legs or hips; character and elbows occupy roughly the central 55% of frame, leaving green margins for waving. No floating cutout above bottom, torso must continue to bottom edge.
Square 1024x1024. Solid perfectly uniform #00B140 green background, no gradient, shadow or ground. Same 2D cartoon/cel shading, dark colored outlines, no white sticker border. No green clothing or props. No extra accessories, no mirroring, no new text, no montage.
```
