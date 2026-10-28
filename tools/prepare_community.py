#!/usr/bin/env python3
"""Compose exact-text community guide cards from existing C renderer previews."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/community/v0.3.0-f3-dev3'
W,H = 900,1200
BG='#101b30'; PANEL='#1c2b43'; LINE='#34445e'; WHITE='#f6eee3'; DIM='#b7c6d9'; PEACH='#ffb38c'; CYAN='#8be1ea'
FONT=Path('C:/Windows/Fonts/msyh.ttc')
BOLD=Path('C:/Windows/Fonts/msyhbd.ttc')

def font(n,bold=False): return ImageFont.truetype(str(BOLD if bold else FONT),n)
def text(draw,xy,s,n=26,color=WHITE,bold=False): draw.text(xy,s,font=font(n,bold),fill=color)
def lines(draw,xy,items,n=25,gap=44,color=DIM):
 for i,s in enumerate(items): text(draw,(xy[0],xy[1]+i*gap),s,n,color)
def panel(draw,box):draw.rounded_rectangle(box,22,fill=PANEL,outline=LINE,width=2)
def base(num,title,subtitle):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 text(d,(52,35),'NABO TOOLKIT',20,CYAN,True);text(d,(W-145,35),num+' / 05',20,DIM)
 text(d,(52,90),title,46,WHITE,True);text(d,(54,161),subtitle,23,DIM)
 d.line((52,218,848,218),fill=LINE,width=2)
 text(d,(52,1150),'公开测试版 · v0.3.0-f3-dev3',20,DIM)
 return im,d
def screen(im,name,xy,size=(220,293)):
 p=ROOT/'build/f3-preview'/name
 src=Image.open(p).convert('RGB');src.thumbnail(size,Image.Resampling.LANCZOS)
 im.paste(src,xy)
def save(im,name):
 im.save(OUT/name,optimize=True)

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 im,d=base('02','六大工具，都在手边','从工作到生活，用一枚工牌发出常用操作')
 tools=[('快捷键','截图 / 复制 / 粘贴','macro.png'),('PPT','翻页 / 黑屏 / 演讲计时','ppt.png'),('会议','静音 / 摄像头 / 举手','meet.png'),('媒体','音量 / 播放 / 切歌','media.png'),('拍照','延时快门 / 五连拍','cam.png'),('名片','网址 / 文字 / Wi-Fi码','card.png')]
 for i,(title,desc,shot) in enumerate(tools):
  x=52+(i%3)*270;y=249+(i//3)*420
  panel(d,(x,y,x+252,y+392));screen(im,shot,(x+16,y+14))
  text(d,(x+16,y+313),title,28,PEACH,True);text(d,(x+16,y+353),desc,17,DIM)
 text(d,(52,1100),'实际 C 渲染器宿主预览；设备和连接为演示，非实拍。',20,DIM)
 save(im,'02-six-tools.png')

 im,d=base('03','三颗按键，上手就会','短按执行，按住约半秒为长按；不需要双击')
 panel(d,(52,250,848,421))
 for i,(key,desc) in enumerate([('↑','菜单向上'),('OK','确认 / 进入'),('↓','菜单向下')]):
  x=95+i*250;d.rounded_rectangle((x,274,x+208,348),18,fill=PEACH)
  text(d,(x+72,284),key,34,BG,True);text(d,(x+45,365),desc,25,WHITE)
 rows=[('通用返回','工具页长按上键返回菜单；二维码放大时先退出放大。'),('快捷键','上 / OK / 下执行本组动作；长OK下一组，长下上一组。'),('PPT','上 / 下翻页，OK黑屏；长OK开始，长下结束。'),('媒体','上 / 下调音量，OK播放暂停；长OK下一曲，长下上一曲。'),('会议','OK静音，上摄像头，下举手；长OK切换会议软件。'),('拍照','上切延时，OK拍摄或取消倒计时，下触发五连拍。')]
 y=465
 for title,desc in rows:
  text(d,(58,y),title,27,CYAN,True)
  # Keep exact copy short enough for a single guide card line.
  wrapped=[desc[j:j+25] for j in range(0,len(desc),25)]
  lines(d,(195,y+2),wrapped,23,32);y+=105
 text(d,(58,1105),'会议快捷键只用于电脑，需与应用设置一致；HID不读回软件状态。',19,DIM)
 save(im,'03-controls.png')

 im,d=base('04','自己的快捷键，自己配','不安装开发环境：电脑浏览器 + USB 数据线')
 for i,(title,desc) in enumerate([('打开配置页','liutupi.github.io/nabo-toolkit/'),('连接并读回','选正确USB串口，再点“从工牌读回”'),('编辑快捷键与名片','1–6组快捷键、1–3张名片；两类系统分别设置'),('写入工牌并核对','页面自动读回比对；成功后断电保留')]):
  y=265+i*160;panel(d,(52,y,848,y+136))
  d.ellipse((76,y+30,138,y+92),fill=PEACH);text(d,(96,y+37),str(i+1),29,BG,True)
  text(d,(165,y+22),title,31,WHITE,True);text(d,(165,y+75),desc,22,DIM)
 panel(d,(52,935,848,1092))
 lines(d,(76,958),['“保存到浏览器”只保存本机编辑，不会改工牌。','名片区可生成Wi-Fi二维码，手机扫码加入网络。','密码包含在二维码和导出配置中；工牌自身不联网。'],22,39)
 save(im,'04-configuration.png')

 im,d=base('05','先配对，再开始遥控','三份绑定记录 · 一次连接一台 · 本地保存')
 screen(im,'conn.png',(550,270),(240,320))
 lines(d,(58,266),['① 菜单进入“连接”','② 选空槽 / 配对新设备','③ 电脑或手机里选择','    “NABO 工具箱”','④ 按两端提示核对 / 输入码','⑤ 选择实际设备类型','⑥ 就绪后打开目标应用'],25,58,WHITE)
 panel(d,(52,720,848,900))
 text(d,(76,741),'配对与使用提醒',28,PEACH,True)
 lines(d,(76,790),['最多保存3台，新配对成功后替换最早绑定。','Typeless只触发你电脑已有的快捷键；不是工牌录音。','拍照前先打开手机相机，快门通过“音量+”触发。'],22,37)
 panel(d,(52,925,848,1095))
 text(d,(76,945),'当前为公开测试版',27,CYAN,True)
 lines(d,(76,990),['应用和系统快捷键需实机核对；并非全平台全部验证。','电视 / 阅读器暂未验收；安装方式与保留数据边界见正文。'],22,38)
 text(d,(550,610),'C渲染器演示画面，非实拍',18,DIM)
 save(im,'05-pairing-and-scope.png')
 files={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size)} for p in sorted(OUT.glob('0*.png'))}
 (OUT/'images.json').write_text(json.dumps({'version':'v0.3.0-f3-dev3','aspect':'3:4','image_entries':files,'guide_screenshots':'C host renderer; synthetic peers; not physical LCD photos'},indent=2)+'\n',encoding='utf-8',newline='\n')
 print('Prepared community cards:',list(files))

if __name__=='__main__':main()
