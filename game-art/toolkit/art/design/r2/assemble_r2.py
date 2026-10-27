#!/usr/bin/env python3
"""Reuse the approved reference head; assemble generated clothing/prop layers."""
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
R1 = ROOT.parent / "r1"
ART = ROOT.parent.parent
spec = importlib.util.spec_from_file_location("r1", R1 / "assemble_r1.py")
r1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r1)
NAMES = ("S2_meet", "S3_media", "S4_cam", "S5_macro")


def polygon_mask(size, polygons):
    mask = Image.new("L", size)
    draw = ImageDraw.Draw(mask)
    for polygon in polygons:
        draw.polygon(polygon, fill=255)
    return mask


def accessory(raw, kind):
    """Extract only actual generated ear gear, never the generated face."""
    raw = raw.convert("RGB")
    if kind == "meet":
        # Coordinates refer to the immutable 1254-square raw edit.
        polygons = [[(899,658),(916,662),(924,631),(940,635),(934,665),
                     (949,677),(962,704),(958,737),(946,761),(925,782),
                     (900,786),(883,777),(872,769),(872,751),(885,700)],
                    [(886,763),(902,774),(886,797),(862,817),(829,834),
                     (794,844),(790,853),(748,858),(734,850),(731,835),
                     (737,825),(748,820),(781,820),(791,828),(826,815),
                     (855,800),(875,779)]]
        color = lambda r,g,b: b > r*1.04 and b > g*1.04
    else:
        # Headband sits outside the cap, earcups over the ear positions.
        polygons = [[(440,160),(345,205),(275,280),(237,356),(219,430),
                     (218,485),(244,514),(250,550),(217,571),(192,600),
                     (177,654),(179,720),(198,771),(236,805),(282,811),
                     (325,799),(326,712),(315,648),(297,592),(280,564),
                     (266,533),(266,494),(254,477),(257,426),(274,357),
                     (305,294),(361,227),(448,165)],
                    [(814,160),(910,205),(979,280),(1017,356),(1036,430),
                     (1037,485),(1011,514),(1005,550),(1038,571),(1063,600),
                     (1078,654),(1076,720),(1057,771),(1019,805),(973,811),
                     (930,799),(929,712),(940,648),(958,592),(975,564),
                     (989,533),(989,494),(1001,477),(998,426),(981,357),
                     (950,294),(894,227),(807,165)]]
        color = lambda r,g,b: r > g*1.13 and b > g*1.13
    area = polygon_mask(raw.size, polygons)
    mask = Image.new("L", raw.size)
    mask.putdata([a if color(*rgb) else 0 for rgb,a
                  in zip(raw.get_flattened_data(),area.get_flattened_data())])
    mask = ImageChops.multiply(mask.filter(ImageFilter.MaxFilter(3)), area)
    gear = raw.convert("RGBA")
    gear.putalpha(mask)
    gear = gear.resize((1024,1024),Image.Resampling.LANCZOS)
    return gear


def locked_head(base):
    head = base.copy()
    head.paste((0,0,0,0),(0,r1.HEAD_END,1024,1024))
    alpha = head.getchannel("A")
    for y in range(r1.PROTECTED_END,r1.HEAD_END):
        factor = (r1.HEAD_END-y)/(r1.HEAD_END-r1.PROTECTED_END)
        row = alpha.crop((0,y,1024,y+1)).point(lambda a: round(a*factor))
        alpha.paste(row,(0,y))
    head.putalpha(alpha)
    return head


def save(layer, path):
    layer.save(path.with_name(path.stem+"_cutout.png"))
    final = r1.over_background(layer)
    final.save(path)
    return final


def comparison(images, labels, path):
    width = 320
    out = Image.new("RGB",(len(images)*width,724),(239,235,229))
    draw = ImageDraw.Draw(out)
    for i,(image,label) in enumerate(zip(images,labels)):
        x=i*width
        draw.text((x+12,12),label,font=r1.font(17),fill=(25,35,50))
        out.paste(image.resize((304,304),Image.Resampling.LANCZOS),(x+8,48))
        draw.text((x+12,377),"HEAD DETAIL",font=r1.font(16),fill=(25,35,50))
        crop=image.crop(r1.HEAD_BOX)
        crop.thumbnail((304,290),Image.Resampling.LANCZOS)
        out.paste(crop,(x+(width-crop.width)//2,414))
    out.save(path)


def small_check(layers, labels, path):
    out = Image.new("RGB",(len(layers)*128,432))
    draw = ImageDraw.Draw(out)
    for row,bg in enumerate(r1.BACKGROUNDS):
        y=row*216
        draw.rectangle((0,y,out.width-1,y+215),fill=bg)
        draw.text((6,y+4),"#%02X%02X%02X  110px bust / 64px avatar"%bg,
                  font=r1.font(10),fill="white")
        for col,(layer,label) in enumerate(zip(layers,labels)):
            x=col*128
            bust=layer.crop(layer.getbbox())
            bust=bust.resize((round(bust.width*110/bust.height),110),Image.Resampling.LANCZOS)
            out.paste(r1.over_background(bust,bg),(x+(128-bust.width)//2,y+32))
            head=layer.crop(r1.HEAD_BOX)
            square=Image.new("RGBA",(768,768))
            square.alpha_composite(head,(0,(768-head.height)//2))
            avatar=square.resize((64,64),Image.Resampling.LANCZOS)
            out.paste(r1.over_background(avatar,bg),(x+32,y+147))
            draw.text((x+43,y+18),label,font=r1.font(10),fill="white")
    out.save(path.with_name(path.stem+"_1x.png"))
    out.resize((out.width*4,out.height*4),Image.Resampling.NEAREST).save(path)


def main():
    base=Image.open(R1/"S0_base_cutout.png").convert("RGBA")
    base_rgb=Image.open(ART/"start/S0_base.png").convert("RGB")
    head=locked_head(base)
    layers, finals, overlays = [], [], []
    for name in NAMES:
        raw=Image.open(ROOT/f"generated/{name}_raw.png")
        body=r1.key_green(raw).resize((1024,1024),Image.Resampling.LANCZOS)
        body.paste((0,0,0,0),(0,0,1024,r1.BODY_START))
        body.alpha_composite(head)
        gear=accessory(raw,"meet" if name=="S2_meet" else "media") if name in NAMES[:2] else Image.new("RGBA",(1024,1024))
        body.alpha_composite(gear)
        gear.save(ROOT/f"{name}_accessory.png")
        final=save(body,ROOT/f"{name}.png")
        layers.append(body); finals.append(final); overlays.append(gear)

    raw=Image.open(R1/"generated/S0R_remote_raw.png")
    remote=r1.key_green(raw)
    mask=polygon_mask(raw.size,[[(246,843),(354,831),(366,855),(384,950),
        (405,947),(423,970),(423,1015),(436,1080),(450,1150),
        (455,1254),(225,1254),(224,1200),(232,1140),(240,1103),
        (228,1066),(229,1018),(240,970),(253,953),(267,955),(249,884)]])
    remote.putalpha(ImageChops.multiply(remote.getchannel("A"),mask))
    remote=remote.resize((1024,1024),Image.Resampling.LANCZOS)
    remote.save(R1/"S0R_remote_prop.png")
    boot=base.copy(); boot.alpha_composite(remote)
    boot_rgb=save(boot,R1/"S0R_remote.png")

    original=Image.new("RGB",(1024,1024))
    original.paste(Image.open(r1.REFERENCE).crop((0,0,224,224)).resize(r1.SCALED_SIZE,Image.Resampling.LANCZOS),r1.OFFSET)
    comparison([original,base_rgb]+finals,["REFERENCE","S0 APPROVED","S2 MEETING","S3 MEDIA","S4 CAMERA","S5 SHORTCUTS"],ROOT/"compare.png")
    small_check(layers,["S2","S3","S4","S5"],ROOT/"small_check.png")
    comparison([original,base_rgb,boot_rgb,Image.open(R1/"S1_ppt_A.png"),Image.open(R1/"S1_ppt_B.png")],
               ["REFERENCE","S0 APPROVED","S0R REMOTE","S1 A","S1 B SELECTED"],R1/"compare_v2.png")
    small_check([base,boot,Image.open(R1/"S1_ppt_A_cutout.png"),Image.open(R1/"S1_ppt_B_cutout.png")],
                ["S0","S0R","S1 A","S1 B"],R1/"small_check_v2.png")

    qa={"status":"S0/S1 B approved; S0R and S2-S5 candidates awaiting user review",
        "reference_sha256":hashlib.sha256(r1.REFERENCE.read_bytes()).hexdigest(),
        "head_source":"../r1/S0_base_cutout.png","canvas":[1024,1024],
        "background":"#00B140","outputs":{}}
    for name,final,layer,overlay,path in zip(list(NAMES)+["S0R_remote"],finals+[boot_rgb],layers+[boot],overlays+[remote],
                                            [ROOT/f"{n}.png" for n in NAMES]+[R1/"S0R_remote.png"]):
        diff=ImageChops.difference(final,base_rgb)
        d=list(diff.get_flattened_data()); a=list(overlay.getchannel("A").get_flattened_data())
        outside=sum(any(pixel) and alpha==0 for pixel,alpha in zip(d[:1024*720],a[:1024*720]))
        cap=ImageChops.difference(final.crop((365,85,665,260)),base_rgb.crop((365,85,665,260))).getbbox()
        mouth=ImageChops.difference(final.crop((480,640,590,695)),base_rgb.crop((480,640,590,695))).getbbox()
        alpha=layer.getchannel("A")
        bad_bg=sum(pixel!=r1.GREEN and a==0 for pixel,a in zip(final.get_flattened_data(),alpha.get_flattened_data()))
        assert outside==0 and cap is None and mouth is None and bad_bg==0 and final.size==(1024,1024)
        bounds=alpha.point(lambda a:255 if a>127 else 0).getbbox()
        qa["outputs"][name]={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "size":list(final.size),"subject_bounds":bounds,
            "head_difference_outside_authorized_accessories":outside,
            "cap_emblem_unchanged":cap is None,"mouth_unchanged":mouth is None,
            "nonuniform_exterior_background_pixels":bad_bg}
    (ROOT/"qa.json").write_text(json.dumps(qa,indent=2)+"\n")
    print(json.dumps(qa,indent=2))


if __name__=="__main__":
    main()
