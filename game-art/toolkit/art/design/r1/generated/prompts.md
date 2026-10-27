# 本轮内置 imagegen 提示词

模式：内置 imagegen 参考图编辑。最终头部与背景规格由 `../assemble_r1.py` 合成保证，未使用 API/CLI 回退。

## S1 A

输入：`../S0_base.png` 的首次构图版本（原参考左帧放大，白大褂与绿背景；当时偏移为 `(8, 16)`）。最终合成统一使用脚本中 `(8, 24)` 的变换。

```text
Use case: identity-preserve clothing edit.
Edit the supplied NABO half-body portrait in place. Keep the entire head, face, thin round glasses, eyes, brown hairstyle, white cap with blue heartbeat NABO lettering, exact head scale, location and proportions unchanged. Do not regenerate the head. The head occupies about the top 70 percent of the frame and must stay that large.
Change ONLY the clothes below the neck to a dark navy-blue blazer (#243451) over an ivory shirt (#F6EBDD), open collar, no tie. Remove the doctor's stethoscope and badge. Add a simple slim black presentation clicker held in the character's RIGHT hand (viewer LEFT), at chest height within the lower third of the frame. Keep the other arm relaxed. A short half-body bust, not a full body, no legs or lower body extension.
Keep the framing EXACTLY as the input: square canvas, front view, cap near y60/1024, face centered, bottom cuts through torso at waist. Background perfectly uniform solid chroma key green #00B140, no gradients, shadows or scenery. Same 2D cartoon illustration as reference, simple dark outlines and cel shading. No green in clothes or clicker. No mirroring; NABO cap emblem must be unmirrored. One single image, no labels, no comparison panels.
```

## S1 B

输入：`S1_ppt_A_raw.png`。

```text
Use case: precise-object-edit, color variant only.
Edit this exact NABO half-body lecturer image. Change ONLY the blazer's color from navy to dark charcoal (#34313E) and the shirt from ivory to pale powder blue (#DCE8F2). Keep the exact same blazer shape, shirt shape, hand pose, slim black presentation clicker in character's right hand/viewer left, head, face, glasses, hair, white NABO cap and emblem, scale, framing and all positions unchanged. Do not redraw or redesign the face. Keep the same cartoon rendering.
Background solid flat #00B140. Square image, same half-body crop, no extra body or legs, no text, no mirroring, no green clothes. This is variant B of the same outfit, not a new character or pose.
```

## S0R（后续规格新增）

输入：已确认的 `art/start/S0_base.png`。

```text
Use case: identity-preserve reference image edit. Edit the supplied exact NABO half-body portrait in place. Keep the doctor's white coat, navy inner clothing, stethoscope and chest badge unchanged. Add only a simple large white rectangular remote control with rounded corners, held upright at chest height by the character's RIGHT hand (viewer LEFT). A few large round dark blue buttons; no words, logos, symbols or display on the remote. The remote and hand stay in the lower third, not covering the face, cap or cap mark. Other arm naturally down. Do not extend the body.
Keep the exact original face, eyes, thin round glasses, brown hair, white cap and blue unmirrored NABO heartbeat emblem. The head is large, the top 70 percent of the frame; do not change its size, pose or position. Keep the SAME half-body framing as input, no legs, no extra lower body; square 1024x1024, front view, hat top around y60, bottom cuts through waist. Flat #00B140 green background with no shadows or gradients. No green clothing or props. Same 2D cartoon rendering, simple dark outlines; no white sticker outline. One image only, no labels or montage. This is an edit, not a new character.
```
