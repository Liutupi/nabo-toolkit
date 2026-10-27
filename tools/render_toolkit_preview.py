"""Render the production C page builders on the host; requires Pillow and host cc."""
import ctypes as C
from pathlib import Path
import struct
import sys
import argparse
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from tk_native import State,PAGES,configure
from test_tk_renderer import RendererTests

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--f2',action='store_true');parser.add_argument('--f3',action='store_true');args=parser.parse_args()
    renderer=RendererTests
    if args.f3:
        from test_tk_f3_renderer import AnimatedRendererTests
        renderer=AnimatedRendererTests
    renderer.setUpClass();lib=renderer.lib;folder=ROOT/('build/f3-preview' if args.f3 else 'build/f2-preview' if args.f2 else 'build/f1-preview');folder.mkdir(parents=True,exist_ok=True)
    h=lib.tk_render_new(C.byref(renderer.assets));images=[]
    try:
        for page in range(12):
            s=State();lib.tk_host_demo(C.byref(s),0);s.page=min(page,9)
            if args.f2:
                from test_tk_config import example
                cfg=example();cfg['groups'][0]['name']='办公室';cfg['groups'][0]['up']['label']='右侧修饰';cfg['groups'][0]['ok']['label']='常用回复';cfg['groups'][0]['down']['label']='音量增加';cfg['cards'][0]['title']='名片';cfg['cards'][0]['name']='NABO';cfg['cards'][0]['line']='我的办公室';configure(lib,s,cfg)
            now=2000
            if page==2 and not args.f2:s.macro_group=1
            if page==3:s.ppt_running=True;s.ppt_start=0;now=605000
            if page==4:s.meet_app=2
            name=PAGES[page] if page<10 else 'pair-code' if page==10 else 'card-zoom'
            if page==10:s.page=8;s.pairing=True;s.pair_until=60000;s.passkey_valid=True;s.passkey=123
            if page==11:s.page=7;s.card_zoom=True
            if not lib.tk_render_frame(h,C.byref(s),now,True,0):raise RuntimeError('Page overflow: '+name)
            data=C.string_at(lib.tk_render_pixels(h),240*320*2);pixels=struct.unpack('<76800H',data)
            rgb=bytes(v for c in pixels for v in (((c>>11)*255//31),((c>>5&63)*255//63),((c&31)*255//31)))
            image=Image.frombytes('RGB',(240,320),rgb);image.save(folder/(name+'.png'));images.append(image)
        grid=Image.new('RGB',(4*248,3*328),(12,15,24))
        for i,image in enumerate(images):grid.paste(image,((i%4)*248+4,(i//4)*328+4))
        grid.save(folder/'overview.png');print(str(folder/'overview.png'))
    finally:lib.tk_render_free(h);renderer.tearDownClass()
if __name__=='__main__':main()
