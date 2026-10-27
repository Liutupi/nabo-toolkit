<p align="right"><strong>简体中文</strong> · <a href="README.md">English</a></p>

# NABO 工具箱

离线的蓝牙 HID 遥控工牌（FoloToy AI Passport，ESP32-C3）：PPT 翻页、会议快捷键、媒体、拍照快门、自定义快捷键/Typeless、名片二维码。

[打开配置页](https://liutupi.github.io/nabo-toolkit/) · [下载固件与离线配置包](https://github.com/Liutupi/nabo-toolkit/releases) · [升级说明](docs/RELEASE_v0.3.0-f3-dev3.md)

**v0.3.0-f3-dev3公开测试版**：原七条动画、完整欢迎、专用开机语音和无爆破按键音已接入并由用户验收。Build PASS（ESP-IDF6.0.2）；Host tests PASS（100项、1,710步完整JS–C对拍）；Device tests 部分PASS（声音/动画，240次连接采样堆最低92,696/最大块77,824字节，音频错误0、崩溃0）。最终镜像重复USB/断电保留、实体跳过、浏览器权限、全部宿主/三槽/睡眠/长稳仍Unverified；历史三秒FAIL保留。F2的Windows/配置实体验收作为历史证据保留，详见HANDOFF22–23和validation/f3.json。

用电脑Chrome/Edge打开配置页，USB数据线连接工牌，依次「连接工牌」→「从工牌读回」→编辑→「写入工牌并核对」。顶部「名片 / Wi-Fi 二维码」可直达编辑区。保存到浏览器只保存本机编辑内容。离线ZIP解压后打开config.html，无需开发环境。Wi-Fi二维码供手机扫码加入网络，工牌自身不联网；密码包含在二维码和导出文件中，页面没有配置上传或统计服务。

![实际C渲染器宿主预览，非LCD照片](docs/images/f3/overview.png)

**仅app升级到0x10000**：旧factory为0x10000/0x1f0000，assets FAT为0x200000/0x600000，与默认构建表不同。不要默认idf.py flash、刷合并镜像或整片擦除。本次不提供首次整机安装镜像。固定已验收app1,999,600字节，SHA256 `d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`。

先读[交接本](docs/HANDOFF.md)、[固件框架](game-art/toolkit/FIRMWARE_PLAN.md)、[界面设计](game-art/toolkit/UI_DESIGN.md)、[验证记录](docs/VALIDATION.zh_CN.md)。维护约定见 `AGENTS.md`。

```sh
python3 -m http.server 8770 --directory game-art/toolkit/prototype
./tools/validate.sh --static
# 激活 ESP-IDF 6.0.2 后运行完整构建门禁：
./tools/validate.sh --f3
# Windows 原生 PowerShell：./tools/validate.ps1 -Stage F3
python tools/build_config_site.py
```

浏览器模拟蓝牙/HID；F2配置规则/USB协议见[配置说明](docs/CONFIGURATION.zh_CN.md)，F0按键见[固件说明](firmware/README.zh_CN.md)，宿主契约见[测试说明](tests/README.zh_CN.md)，视频格式见[精灵说明](game-art/toolkit/sprites/README.zh_CN.md)。原始素材不变。

门禁不刷机或发布。源码采用[MIT](LICENSE)；NABO形象、美术、动画及语音不随MIT授权，详见[许可和第三方声明](NOTICE.md)。本项目与FoloToy官方无关联。

[Windows 接班](docs/WINDOWS_CONTINUE.zh_CN.md) · `python tools/verify_assets.py` 检查全部367份素材，原364份保持不变。
