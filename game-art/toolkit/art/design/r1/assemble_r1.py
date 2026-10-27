#!/usr/bin/env python3
"""Assemble reference-locked R1 portraits and the explicitly requested QA sheets.

Imagegen supplies the suit/clicker edits. This script reuses the actual reference
head pixels, removes backgrounds, applies one shared transform, and resizes QA.
It never draws or regenerates facial features.
"""
from collections import deque
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT.parent.parent / "reference/nabo-idle.png"
GREEN = (0, 177, 64)
BACKGROUNDS = ((20, 32, 58), (34, 50, 79))
OFFSET = (8, 24)
SCALED_SIZE = (1008, 1008)  # shared 4.5x transform of the 224-square reference
HEAD_END = 744  # neck join; head and facial features stay above the feather band
PROTECTED_END = 728
BODY_START = 720
HEAD_BOX = (128, 48, 896, 736)
NAMES = ("S0_base", "S1_ppt_A", "S1_ppt_B")


def flood(points, start, width, height):
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0 <= nx < width and 0 <= ny < height:
                i = ny * width + nx
                if points[i] and (nx, ny) not in seen:
                    seen.add((nx,ny))
                    queue.append((nx,ny))
    return seen


def reference_cutout():
    im = Image.open(REFERENCE).convert("RGB").crop((0, 0, 224, 224))
    pixels = list(im.get_flattened_data())
    # Remove only black exterior and detached compression specks. All interior
    # RGB values, including dark glasses/hair, remain the original source values.
    fg = [max(c) > 24 for c in pixels]
    comp = flood(fg, (112, 80), 224, 224)
    outside = flood([(x,y) not in comp for y in range(224) for x in range(224)],
                    (0,0),224,224)
    alpha = Image.new("L",im.size)
    alpha.putdata([0 if (x,y) in outside else 255
                   for y in range(224) for x in range(224)])
    im.putalpha(alpha)
    im.save(ROOT / "reference_left_cutout.png")
    return im


def key_green(im):
    im = im.convert("RGB")
    bg = im.getpixel((0,0))
    out = []
    for r,g,b in im.get_flattened_data():
        dominance = min(g-r,g-b)
        alpha = max(0.0,min(1.0,(60-dominance)/40)) if g > 70 else 1.0
        if alpha < 0.01:
            out.append((0,0,0,0))
        else:
            rgb = tuple(round(max(0,min(255,(c-bc*(1-alpha))/alpha)))
                        for c,bc in zip((r,g,b),bg))
            out.append(rgb+(round(alpha*255),))
    result = Image.new("RGBA",im.size)
    result.putdata(out)
    return result


def over_background(layer, color=GREEN):
    im = Image.new("RGBA",layer.size,color+(255,))
    im.alpha_composite(layer)
    return im.convert("RGB")


def font(size=20):
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf",size)


def comparison(reference, portraits):
    result = Image.new("RGB",(1600,880),(239,235,229))
    draw = ImageDraw.Draw(result)
    images = [reference]+portraits
    labels = ("REFERENCE - ORIGINAL", "S0 - DOCTOR", "S1 A - NAVY / IVORY", "S1 B - CHARCOAL / BLUE")
    for i,(im,label) in enumerate(zip(images,labels)):
        x=i*400
        draw.text((x+16,12),label,font=font(19),fill=(25,35,50))
        draw.text((x+16,42),"Same source head; no mirroring",font=font(15),fill=(65,70,80))
        thumb=im.resize((384,384),Image.Resampling.LANCZOS)
        result.paste(thumb,(x+8,72))
        draw.text((x+16,480),"HEAD DETAIL",font=font(18),fill=(25,35,50))
        detail=im.crop(HEAD_BOX)
        detail.thumbnail((384,344),Image.Resampling.LANCZOS)
        result.paste(detail,(x+(400-detail.width)//2,520))
    result.save(ROOT/"compare.png")


def small_check(layers):
    # Draw at actual display size, then use nearest-neighbor 4x enlargement.
    sheet=Image.new("RGB",(384,432),(239,235,229))
    draw=ImageDraw.Draw(sheet)
    tiny=font(10)
    for row,bg in enumerate(BACKGROUNDS):
        top=row*216
        draw.rectangle((0,top,383,top+215),fill=bg)
        draw.text((6,top+4),f"#{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}   110px bust / 64px head",font=tiny,fill="white")
        for col,(name,layer) in enumerate(zip(("S0","S1 A","S1 B"),layers)):
            x=col*128
            bust=layer.crop(layer.getbbox())
            width=round(bust.width*110/bust.height)
            bust=bust.resize((width,110),Image.Resampling.LANCZOS)
            sheet.paste(over_background(bust,bg),(x+(128-width)//2,top+32))
            head=layer.crop(HEAD_BOX)
            # Avatar is a 64-square direct crop from the same image, not redrawn.
            side=max(head.size)
            square=Image.new("RGBA",(side,side))
            square.alpha_composite(head,((side-head.width)//2,(side-head.height)//2))
            square=square.resize((64,64),Image.Resampling.LANCZOS)
            sheet.paste(over_background(square,bg),(x+32,top+147))
            draw.text((x+49,top+18),name,font=tiny,fill="white")
    sheet.save(ROOT/"small_check_1x.png")
    sheet.resize((1536,1728),Image.Resampling.NEAREST).save(ROOT/"small_check.png")


def main():
    cutout=reference_cutout().resize(SCALED_SIZE,Image.Resampling.LANCZOS)
    base=Image.new("RGBA",(1024,1024))
    base.alpha_composite(cutout,OFFSET)
    head=base.copy()
    head.paste((0,0,0,0),(0,HEAD_END,1024,1024))
    alpha=head.getchannel("A")
    for y in range(PROTECTED_END,HEAD_END):
        factor=(HEAD_END-y)/(HEAD_END-PROTECTED_END)
        row=alpha.crop((0,y,1024,y+1)).point(lambda a: round(a*factor))
        alpha.paste(row,(0,y))
    head.putalpha(alpha)
    layers=[base]
    for variant in ("A","B"):
        raw=Image.open(ROOT/f"generated/S1_ppt_{variant}_raw.png")
        body=key_green(raw).resize((1024,1024),Image.Resampling.LANCZOS)
        body.paste((0,0,0,0),(0,0,1024,BODY_START))
        body.alpha_composite(head)
        layers.append(body)
    portraits=[]
    for name,layer in zip(NAMES,layers):
        layer.save(ROOT/f"{name}_cutout.png")
        final=over_background(layer)
        final.save(ROOT/f"{name}.png")
        portraits.append(final)
    original=Image.new("RGB",(1024,1024))
    original.paste(Image.open(REFERENCE).crop((0,0,224,224)).resize(SCALED_SIZE,Image.Resampling.LANCZOS),OFFSET)
    comparison(original,portraits)
    small_check(layers)
    checks={
        "reference_sha256":hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
        "reference_frame":[0,0,224,224],
        "transform":{"scale":4.5,"offset":list(OFFSET)},
        "protected_rows":[0,BODY_START-1],
        "neck_join_rows":[PROTECTED_END,HEAD_END-1],
        "canvas":[1024,1024],
        "background":"#00B140",
        "head_pixel_differences_vs_S0":{},
        "outputs":{},
        "status":"R1 candidates, awaiting user identity/outfit approval",
    }
    for name,im in zip(NAMES,portraits):
        diff=ImageChops.difference(im.crop((0,0,1024,BODY_START)),portraits[0].crop((0,0,1024,BODY_START)))
        checks["head_pixel_differences_vs_S0"][name]=sum(any(c) for c in diff.get_flattened_data())
        checks["outputs"][name]={"size":list(im.size),"sha256":hashlib.sha256((ROOT/f"{name}.png").read_bytes()).hexdigest(),"corners":[im.getpixel(p) for p in ((0,0),(1023,0),(0,1023),(1023,1023))]}
        assert diff.getbbox() is None
        assert im.size==(1024,1024)
        assert all(im.getpixel(p)==GREEN for p in ((0,0),(1023,0),(0,1023),(1023,1023)))
    (ROOT/"qa.json").write_text(json.dumps(checks,indent=2)+"\n")
    print(json.dumps(checks,indent=2))


if __name__=="__main__":
    main()
