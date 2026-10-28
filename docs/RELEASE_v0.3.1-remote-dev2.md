# v0.3.1-remote-dev2 · 息屏遥控公开测试版

微信读书翻页、抖音切视频时，现在可以让屏幕熄灭并继续使用三键遥控。蓝牙保持连接，普通翻页不会点亮屏幕，也不会重新计算亮屏时间；需要查看界面时，长按最下方的OK键，只亮屏，不顺带执行快捷键。本版同时将抖音移入「媒体」，并按工牌实际从上到下的 **↑ / ↓ / OK** 顺序显示全部按键说明。

沿用全部已确认的NABO形象、七条动画、完整欢迎与开机语音，不重做素材。社区原封面与图片保持不变。此为公开测试版；本轮新增行为已通过实体验收，全部平台、功耗和长期稳定性仍有未测项。

## 这版怎么用

- **快捷键**默认五组：截图、Typeless、剪映、微信读书、编辑。截图上键保留截屏，下键Esc取消，OK保留粘贴；Typeless与剪映原绑定不变。编辑组为上键撤销、下键全选、OK复制。
- **媒体**先用↑/↓选择「音乐」或「抖音」，按OK进入。音乐保留上/下音量、OK播放暂停、亮屏长OK下一曲、长下上一曲；抖音上键发送↑、下键发送↓、OK发送→。实际切视频/快进由App与焦点决定。
- **微信读书**上键发送↑、下键发送↓、OK发送→，对应上一页、下一页、下一章的使用意图；具体阅读模式是否响应由App决定。
- **息屏遥控**默认开启：已连接的快捷键页，或已进入的媒体工具页，显示约30秒后息屏。连续短按不会延长这30秒；息屏后短键继续发HID。屏幕背光、动画解码与LCD传输停止，蓝牙、按键和USB仍工作。
- **暗屏长OK只亮屏**，这次长按及其松开不发快捷键、不换组、不切歌；亮屏后再次长OK恢复原工具动作。长上键亮屏并返回；媒体活动页先回音乐/抖音选择，再长上回主菜单。快捷键长下换组时亮屏，音乐长下上一曲仍可在暗屏使用。
- 在「设置 → 息屏遥控」可关闭自动息屏。断连、配对/设备类型弹窗、配置操作或错误提示会使屏幕保持可见。深度休眠设置独立于此功能。

## 配置与已有个人分组

[在线配置页](https://liutupi.github.io/nabo-toolkit/)使用电脑Chrome/Edge与USB数据线。依次「连接工牌」→「从工牌读回」→编辑→「写入工牌并核对」；显示读回一致才算保存成功。也可完整解压 `nabo-toolkit-config-offline.zip`，打开其中的 `config.html`，无需开发环境。

新固件不会自动覆盖NVS里的个人配置，旧六组配置仍兼容。要采用新版五组，请先读回，再点击「使用新版默认快捷键（保留名片）」，检查后显式写入并核对；此按钮保留当前页面的名片，因此务必先读回。它会替换快捷键分组，个人定制绑定请先自行备份或逐项修改。作者当前设备仅迁移了匹配旧默认的抖音组，其余分组、名片和绑定已保留；公开下载不含这份个人配置。

「保存到浏览器」只保存本机编辑，不修改工牌。Wi-Fi二维码用于手机扫码加入网络，工牌自身不联网；二维码及导出文件包含密码，分享前删去私人内容。

## 下载内容与固定应用身份

- `nabo-toolkit-app.bin`：精确已安装验收的应用，**仅写0x10000**。
- `nabo-toolkit-v0.3.1-remote-dev2.zip`：同一应用、受保护的app-only升级脚本、所选验收记录、manifest、校验清单、离线配置页与许可证。
- `nabo-toolkit-config-offline.zip`：与本版固件ZIP内相同的独立离线配置页。
- `manifest.json`、`SHA256SUMS.txt`：应用、来源提交、配置与ZIP成员校验。
- `nabo-toolkit-community-full.bin`：另行提供的社区完整首装镜像，从**0x0**写入，会更换默认分区表并重置NVS、设置和蓝牙绑定。
- `community-manifest.json`、`COMMUNITY_SHA256SUMS.txt`：完整首装镜像的来源、布局与独立校验。

本版应用为 **2,011,616字节**，SHA256：

```text
b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe
```

固件内版本 `0.3.1-remote-dev2`。直接使用已验收归档中的相同应用，不重新编译后替换。匹配的完整构建为2,077,152字节，SHA256 `9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b`；社区文件需与此固定镜像逐字节核对。旧 `v0.3.0-f3-dev3` Release及其全部下载保持不变。

## 保留数据升级与社区首装

实机旧表为factory **0x10000/0x1f0000**、assets FAT **0x200000/0x600000**。新应用在该factory内余20,000字节，实际写入范围 `[0x10000,0x1fb1e0)`，擦除扇区截至 `0x1fc000`。保留数据升级仅更新app，保留旧分区表、NVS、PHY与素材。不要用默认 `idf.py flash`、完整镜像或整片擦除来做保留数据升级。

先解压固件ZIP，使用Python3.11与esptool5.5.0；日常配置不需要这些工具：

```text
python -m pip install esptool==5.5.0
python tools/flash_candidate.py --mode inspect --app nabo-toolkit-app.bin --sha256 b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe
python -m serial.tools.list_ports -v
python -m esptool --chip esp32c3 --port YOUR_PORT read-mac
```

关闭占用串口的监视器/配置页，确认你自己的端口与设备身份，替换以下两个占位符（设备地址用小写）：

```text
python tools/flash_candidate.py --mode upgrade --port YOUR_PORT --expected-mac YOUR_DEVICE_MAC --app nabo-toolkit-app.bin --sha256 b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe
```

脚本在同一连接复核芯片、8MiB容量、安全状态、实际分区、应用哈希与擦除范围，再写入和校验；未知布局应停止。操作收据与身份只保存在本机private目录，勿上传。

社区完整首装使用构建默认表：factory0x10000/0x3f0000、assets0x400000/0x300000、files0x700000/0x100000。从0x0安装会重置原设置/绑定；先备份重要数据，并准备重新配对。完整文件是构建产物，NVS/PHY为0xff填充，不含设备读取内容、凭据或个人配置。**本轮真机验证的是保留数据的app-only升级，完整首装路径仍未实机验收。**

## 验证范围

- **Build PASS**：ESP-IDF6.0.2、ESP32-C3、8MiB Flash、无PSRAM；固定归档与源码输入哈希独立校验通过，发布复用同一已验收应用。
- **Host tests PASS**：127项（37 Node+90 Python），2,206步完整JS–C对拍，3项故意变异被捕获，跳过0。包含媒体两模式、连续按键30秒息屏、暗屏长OK消费及松开不误发、旧配置兼容、持久化故障和增量/全刷新一致性。
- **Device tests 本轮新增行为PASS**：准确应用已app-only安装并写后校验；旧表/NVS/PHY/素材保护检查通过。配置迁移后自动读回及连续3次读回一致。用户确认实体顺序、媒体选择、持续短按后息屏、暗屏仍遥控、长OK只亮屏，以及当前耳机/键盘共存可用；串口真实发送/背光状态观察与之对应。此为本轮行为验收，不能当作全部F0/F1门槛通过。
- **Unverified**：实际电流与续航改善、冷启动保留、全部手机/电脑及App版本矩阵、完整首装、三槽切换/睡眠/长稳和严格三秒回连。历史Windows蓝牙共存/断联问题根因未定；当前条件下正常不代表已找到或修复根因。HID通知完成也不等于主机App已处理。详细记录见本包 `validation.json` 与仓库 `docs/validation/remote-control-v0.3.1.json`。

源码采用MIT；NABO形象、美术、动画和语音不随MIT授权，详见随包LICENSE、NOTICE.md和licenses目录。本项目与FoloToy官方无关联。

## English

This public **test** release adds display-off remote control and moves Douyin into the Media tool. The physical top-to-bottom order is **UP / DOWN / OK**. Shortcut defaults are Screenshot, Typeless, CapCut, WeRead and Editing. Existing personal configurations, including six groups, remain supported and are never automatically overwritten.

In Media, choose Music or Douyin with UP/DOWN, then press OK. Music retains its volume/playback controls. Douyin and WeRead send keyboard UP, DOWN and RIGHT for UP, DOWN and OK; actual page/chapter/video/seek behavior depends on the host app and focus.

Connected shortcut and selected media pages turn their display off after30 seconds; ordinary key presses do not extend that interval. Backlight, animation decoding and LCD transfers stop while BLE, buttons and USB remain active. Short keys still send HID. **Long OK while dark only wakes the display**, consuming that gesture and release without changing groups/tracks or sending HID. Long UP lights and returns; a media tool returns to its mode picker first. Turn this behavior off in Settings if preferred. Deep sleep is a separate setting.

The exact accepted app is2,011,616 bytes, SHA256 `b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe`. The app-only ZIP preserves the legacy partition table/NVS/assets through the guarded installer at0x10000; the separate community full image installs at0x0 and resets partitioning/settings/bonds. Full first installation is not device-tested. No device readback, personal configuration, credentials or raw logs are distributed; the prior Release is unchanged.

Use desktop Chrome/Edge and USB at [the configurator](https://liutupi.github.io/nabo-toolkit/), or extract the complete offline ZIP and open config.html. Read from the badge before changing defaults to retain actual cards; explicitly write and verify afterwards. Existing cfg_v1 is not silently migrated.

Build PASS;127 host tests and2,206 full JS–C replay steps PASS. The requested physical media/display behavior and current coexistence checks passed on the exact app. Power draw/runtime gain, cold retention, all host/app combinations, full installation and wider stability gates remain unverified. The historical intermittent Windows Bluetooth problem has no confirmed root cause or demonstrated fix. Source is MIT; NABO creative assets are excluded under NOTICE.md.
