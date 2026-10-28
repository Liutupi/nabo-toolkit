# v0.3.0-f3-dev3 · 公开测试版

本版本接通快捷键/名片USB配置保存与读回，使用原七条动画、完整欢迎和专用开机语音。最终dev3的完整欢迎、各工具服装/动作、开机音和无爆破按键音已由用户验收。作者默认键位保持原样。此为公开测试版，未测项见下文。

配置入口：https://liutupi.github.io/nabo-toolkit/ 。电脑Chrome/Edge+USB，连接→从工牌读回→编辑→写入工牌并核对。顶部「名片 / Wi-Fi 二维码」直达编辑区。离线包解压后打开config.html，无需开发环境。不要将自己的Wi-Fi密码或配置导出上传到GitHub。

## 下载内容

- `nabo-toolkit-app.bin`：精确已验收F3 dev3应用，**仅写0x10000**。
- `nabo-toolkit-v0.3.0-f3-dev3.zip`：同一app、受保护的升级脚本、manifest、验收说明、离线配置页及许可证。
- `nabo-toolkit-config-offline.zip`：独立离线配置页。
- `manifest.json`、`SHA256SUMS.txt`：产物身份/成员校验。
- `nabo-toolkit-community-full.bin`：经用户单独授权的社区完整首装镜像，2,065,136字节，从**0x0**写入；会改默认分区表、重置NVS/设置/绑定，完整首装路径尚未真机验收。
- `community-manifest.json`、`COMMUNITY_SHA256SUMS.txt`：社区首装镜像的来源、分区、嵌入app及独立校验。

app为1,999,600字节，SHA256 **d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711**，固件内版本0.3.0-f3-dev3。没有重新构建或改版本后替换已验收app。所有动画和PCM都在app内，不需要写assets。

## 升级已有兼容工牌

仅适用ESP32-C3/8MiB、无安全启动/Flash加密、受保护脚本能识别的两种分区表。实机验收的是旧表：factory0x10000/0x1f0000、assets FAT0x200000/0x600000；另可识别项目默认表。**保留数据升级不要用默认idf.py flash、社区完整镜像或整片擦除。** 未知分区应停止，不强刷。原固件ZIP仍是app-only升级包；完整首装文件单独命名，不可混用。

### 社区完整首装（与保留数据升级不同）

用户随后明确授权将已有固定构建的完整镜像提交AI Passport玩法社区。完整镜像SHA256 `9fa968de2a4837d130188bb9541ec55a67a3f1bd936b01eeeb4b81ea5047ad1c`，2,065,136字节，内含相同已验收app，未重新编译。从0x0安装会写默认表（factory0x10000/0x3f0000、assets0x400000/0x300000、files0x700000/0x100000），NVS/PHY区域为构建生成的0xff填充，因此原设置和蓝牙绑定会重置。镜像不含设备读回、凭据或个人配置。

此路径仅供接受重新分区/清除旧配置的首次安装，需先备份重要数据；构建/布局/内容校验通过，**完整首装尚未真机验收**。需要保留旧分区和数据时，继续使用上面的app-only脚本。社区发布过程中没有重刷作者当前工牌。

升级脚本需要Python3.11及esptool5.5.0；日常配置只需浏览器。先解压固件ZIP，在解压目录打开终端：

```text
python -m pip install esptool==5.5.0
python tools/flash_candidate.py --mode inspect --app nabo-toolkit-app.bin --sha256 d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711
python -m serial.tools.list_ports -v
python -m esptool --chip esp32c3 --port YOUR_PORT read-mac
```

自行确认目标工牌端口和本机读出的MAC；不要沿用别人的COM号或地址。关闭串口监视器/配置页连接，替换以下YOUR_PORT及YOUR_DEVICE_MAC（小写），再运行：

```text
python tools/flash_candidate.py --mode upgrade --port YOUR_PORT --expected-mac YOUR_DEVICE_MAC --app nabo-toolkit-app.bin --sha256 d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711
```

脚本在同一串口连接校验目标、芯片、实际容量、安全状态、分区表和app哈希/扇区边界；不符合则拒绝写入。仅更新app并校验，保留分区表、NVS、PHY和原assets。凭据/绑定/操作收据留在本机private目录，不要上传。断电/USB异常时先确认设备实际状态，不反复盲刷。

## 验证范围

- **Build PASS**：ESP-IDF6.0.2/C3/8MiB/无PSRAM，精确固定归档独立验证。旧factory余量32,016字节。
- **Host tests PASS**：100项、1,710步完整JS–C对拍；92帧解码、字库、PCM/包络和C渲染一致性通过。
- **Device tests 部分PASS**：dev3声音/完整欢迎/各工具动画用户验收；240次真实连接采样堆最低92,696、最大块77,824字节，音频错误0、崩溃0。安装仅app-only并检查保护区。
- **Unverified**：最终dev3重复USB配置/断电保留、浏览器权限实际流程、实体跳过、最终镜像全部宿主/三槽/睡眠/长稳等。F2 dev2曾通过Windows粘贴/音量、文字/名片/扫码和保存后断电保留，这些不是dev3重测。历史鸿蒙三秒回连FAIL保留；Tango2S/电视未测。详见[validation/f3.json](validation/f3.json)。

For English readers: this is a public **test** release. Use the exact app only at
0x10000 through the guarded installer after checking your own device/port/MAC.
The separate community full image is for first installation at0x0 and resets
the partition table/NVS/settings/bonds; its full-install path is not device-tested.
Use the app-only ZIP for preserving data. The app fits the legacy0x1f0000
factory partition; NVS/PHY/assets/partition table are preserved. Browser configuration
needs desktop Chrome/Edge and USB; read, edit, write and verify. Remaining validation
items are listed in validation/f3.json. Source is MIT; NABO creative assets are excluded.
