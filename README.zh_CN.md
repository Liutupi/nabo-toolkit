<p align="right"><strong>简体中文</strong> · <a href="README.md">English</a></p>

# NABO 工具箱

**v0.3.2-voice-dev4 · 公开实验测试版**：新增本人录入的离线语音查找，覆盖读书、抖音、音乐、名片、拍照、截图、语音输入。主菜单长按底部OK，每词建议录三次，再短OK识别；语音输入仅进入Typeless，之后按原键操作。213项宿主与本轮真机语音/21份模板保留检查通过。显式无损整理恢复了存储余量，不改变个人样本、配置或绑定；原NABO形象、动画和声音保留。[发布及保护升级说明](docs/RELEASE_v0.3.2-voice-dev4.md) · [录入用法](docs/VOICE.zh_CN.md) · [配置页](https://liutupi.github.io/nabo-toolkit/)。

它不是通用听写或普适识别。个人名片链接真实改写、重启保留和手机扫码已通过；长稳、多用户/噪声和完整首装仍有未测项，PCUSB耳机间歇问题未定因。本轮社区更新文案已备齐，但页面自动化被中止，尚未保存/提交，原社区图片保留。[作者全部已发布作品](https://ai-passport.folotoy.cn/creators/?id=14101)。

[v0.3.2-voice-dev4 固件已发布](https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.2-voice-dev4)：8个资产匿名重新下载通过，ZIP内37个文件及公开配置页11个文件字节/SHA一致；[发布核验记录](docs/validation/publication-v0.3.2-voice-dev4.json)。社区原条目已公开的是上一版v0.3.1，本次dev4尚未更新或提交。以下v0.3.1段落为历史发布/设备证据，不代表当前社区状态或v0.3.2重新完成全项验收。

**v0.3.1-remote-dev2已在GitHub发布，社区审核中（2026-10-28）**：源码默认五组为截图（含Esc取消）、Typeless、剪映、微信读书、编辑，抖音移入媒体的“音乐/抖音”选择。音乐原音量/播放/切歌键保留；屏幕与本地网页按实体从上到下“上、下、OK”显示。可选30秒息屏遥控，普通短键不续亮屏计时且继续发送，暗屏长OK只亮屏，亮屏长OK保留原工具动作，长上仍返回。候选 `0.3.1-remote-dev2` 完整门禁PASS：127项（37 Node+90 Python）、跳过0、2,206步、3项故意变异及ESP-IDF6.0.2/F3构建；固定app已获授权app-only安装、校验和复位通过。另经真实USB仅移除匹配的旧抖音组，其余组/名片逐项保留，自动读回及连续3次读回一致。实体媒体选择/键位顺序、息屏、暗屏翻页及长OK只亮屏已由用户确认通过；冷启动保留、真实功耗和全部App/平台矩阵仍待测，GitHub固件与公开配置页已核验，原社区条目已更新并重新提交审核，尚未公开上架。

本轮实体验收PASS：用户确认媒体/键位顺序、息屏、暗屏翻页、长OK只亮屏，耳机/键盘本轮均正常。独立补采也在screen_off=true全程捕获16条HID成功/32次notification TX，动画帧9冻结、相关错误0，唤亮前后sent不增加。此前间歇连接根因仍未确定，不称已修复或全平台共存通过；TX完成非宿主ACK。

**配置页已公开并核验**：[新版配置页](https://liutupi.github.io/nabo-toolkit/)与当前五组源码同步；v0.3.0包及旧 `nabo-toolkit-config-shortcuts-20261028.zip` 保留各自原六组快照，HANDOFF25仍作历史记录。旧dev3要获得媒体选择/息屏，需升级本版app；读回个人配置不会自动删组，替换默认组和写入设备仍须显式操作。此前102项属于快捷键候选，与本版127项分开记录；本版Release的8个资产及配置站点11个文件已匿名下载并核对字节/SHA，社区公开上架仍待审核。

离线的蓝牙 HID 遥控工牌（FoloToy AI Passport，ESP32-C3）：PPT 翻页、会议快捷键、媒体、拍照快门、自定义快捷键/Typeless、名片二维码。

[打开配置页](https://liutupi.github.io/nabo-toolkit/) · [下载固件与离线配置包](https://github.com/Liutupi/nabo-toolkit/releases) · [升级说明](docs/RELEASE_v0.3.1-remote-dev2.md)

**社区更新**：原项目1701/可变修订3928已更新为v0.3.1-remote-dev2并重新提交，当前**审核中，尚未公开**。原五图/封面/顺序保留，逐张重下字节/SHA与更新前一致；保存页固件重下2,077,152字节、SHA256 `9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b`，与已发布GitHub full逐字节相等。见[本轮社区核验](docs/community/v0.3.1-remote-dev2/README.md)。匿名社区端点本轮未重查。

[历史首次投稿记录](docs/community/v0.3.0-f3-dev3/README.md)保留v0.3.0快照；3928是可变修订，当前固件href已替换为新二进制，旧字节/SHA和HTTP401不能称当前下载结果。

**v0.3.0-f3-dev3公开测试版**：原七条动画、完整欢迎、专用开机语音和无爆破按键音已接入并由用户验收。Build PASS（ESP-IDF6.0.2）；Host tests PASS（100项、1,710步完整JS–C对拍）；Device tests 部分PASS（声音/动画，240次连接采样堆最低92,696/最大块77,824字节，音频错误0、崩溃0）。最终镜像重复USB/断电保留、实体跳过、浏览器权限、全部宿主/三槽/睡眠/长稳仍Unverified；历史三秒FAIL保留。F2的Windows/配置实体验收作为历史证据保留，详见HANDOFF22–23和validation/f3.json。

用电脑Chrome/Edge打开配置页，USB数据线连接工牌，依次「连接工牌」→「从工牌读回」→编辑→「写入工牌并核对」。顶部「名片 / Wi-Fi 二维码」可直达编辑区。保存到浏览器只保存本机编辑内容。离线ZIP解压后打开config.html，无需开发环境。Wi-Fi二维码供手机扫码加入网络，工牌自身不联网；密码包含在二维码和导出文件中，页面没有配置上传或统计服务。

候选息屏开关独立使用NVS `remote_v1`，不迁移或擦除既有设置与绑定；本次授权配置迁移另将保留的五组保存到 `cfg_v1`。一般换默认组仍须先读回实际名片，再显式写入核对；仅更新配置不能让旧dev3增加媒体选择或息屏功能。当前连接就绪与诊断采样不等于Windows蓝牙故障根因已确认或全部共存通过。

![实际C渲染器宿主预览，非LCD照片](docs/images/f3/overview.png)

**保留数据升级仅写app到0x10000**：旧factory为0x10000/0x1f0000，assets FAT为0x200000/0x600000，与默认构建表不同。不要默认idf.py flash、刷社区完整镜像或整片擦除。经单独授权另提供 `nabo-toolkit-community-full.bin` 社区首装包（0x0写入、重置分区/NVS/绑定，完整首装尚未真机验收），详见[安装说明](docs/RELEASE_v0.3.1-remote-dev2.md)。两种包不能混用。本版固定app2,011,616字节，SHA256 `b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe`；旧v0.3.0产物仍按上文历史验收记录保留。

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

[Windows 接班](docs/WINDOWS_CONTINUE.zh_CN.md) · `python tools/verify_assets.py` 检查全部368份素材（93,040,985字节，含社区封面），原364份保持不变。
