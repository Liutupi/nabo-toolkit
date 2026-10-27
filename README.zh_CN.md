<p align="right"><strong>简体中文</strong> · <a href="README.md">English</a></p>

# NABO 工具箱

离线的蓝牙 HID 遥控工牌（FoloToy AI Passport，ESP32-C3）：PPT 翻页、会议快捷键、媒体、拍照快门、自定义快捷键/Typeless、名片二维码。

当前进度：浏览器版式/配对码模拟和第一批 Grok 精灵已接入；**F0 蓝牙探路固件构建及 40 项宿主测试通过，待真机验收**。配对、回连、堆实测通过后才进入完整 F1。欢迎动画按用户选择完整播完，约 5.5 秒进入菜单，任意键可跳过。

先读[交接本](docs/HANDOFF.md)、[固件框架](game-art/toolkit/FIRMWARE_PLAN.md)、[界面设计](game-art/toolkit/UI_DESIGN.md)、[验证记录](docs/VALIDATION.zh_CN.md)。维护约定见 `AGENTS.md`。

```sh
python3 -m http.server 8770 --directory game-art/toolkit/prototype
./tools/validate.sh --static
# 激活 ESP-IDF 6.0.2 后运行完整构建门禁：
./tools/validate.sh
```

浏览器模拟蓝牙/HID；F0 用法与按键见[固件说明](firmware/README.zh_CN.md)，宿主契约见[测试说明](tests/README.zh_CN.md)，视频来源与二进制格式见[精灵说明](game-art/toolkit/sprites/README.zh_CN.md)。原始 Grok 视频原样保留，已有人工审查说明和全帧自动解码记录。

验证过程不刷机、不 commit/push、不发布。本项目与 FoloToy 官方无关联；NABO 形象、美术不随源码许可授权，复用 BSP 的许可单独保留。

[Windows 接班](docs/WINDOWS_CONTINUE.zh_CN.md) · `python tools/verify_assets.py` 检查全部 364 份源素材、中间帧和运行素材。
