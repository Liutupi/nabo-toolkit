# v0.3.2-voice-dev4 · 本人离线语音查找（公开实验测试版）

在主菜单长按最下方 OK，可录入自己的固定口令，直接找到读书、抖音、音乐、名片、拍照、截图和语音输入。无需联网；不是通用语音转文字或身份验证。原七条动画、完整欢迎、开机语音、按键音、媒体和息屏遥控保持，社区原封面与五张图片不变。

## 录入和使用

1. 主菜单长按底部 OK 约 0.5 秒，进入「语音查找」。↑/↓选择录入目标。
2. 长按 OK，先保持安静，等「请说目标名称」再自然说一次名称；等「已保存」后重复，建议每词录三次。旧模板兼容，不需要全部重录。
3. 短按 OK，等「请说口令」后说任一已录词；当前高亮只决定录入目标，识别会比较全部已录词。长按上键取消并返回。
4. 识别只进入工具页，不自动发截图、拍照或播放指令。「语音输入」进入 Typeless/语音输入分组，之后按原键触发电脑上已安装的输入工具；工牌本身不做听写。

录入有效语音上限约 0.96 秒，查询约 1.92 秒；每次只说一个短词，说完停顿。准备阶段不要抢先说话。未识别、歧义或过长时不跳页。个人配置缺少微信读书、截图或 Typeless 对应组时，不会自动覆盖配置来创建它。详见[本人录入说明](VOICE.zh_CN.md)。

## 本次修改

- 模板计数对齐并逐字节同步，增加堆和栈检查；本轮连续录入/识别未再出现先前的卡死重启，原异常最终根因仍未完全锁定。
- 新模板无损打包，使用每词双副本，确认新副本后再退休同词旧记录；空间不足先拒绝，保留已确认样例。
- 模板读取与匹配器分配错开，避免临时内存同时占用。短查询和歧义门槛按已保留样本校核调整，同分和过近结果仍拒绝。
- 增加显式旧模板整理入口和配置写入空间预检。设备实测 21 份样本的系数、数量、轮转位置全部保持；NVS可用 entries 从47增至251。

## 配置页与个人数据

[在线配置页](https://liutupi.github.io/nabo-toolkit/)：电脑 Chrome/Edge + USB 数据线，先「连接工牌」→「从工牌读回」→编辑→「写入工牌并核对」。名片/Wi-Fi 二维码在快捷键分组下方，也可点顶部入口。`nabo-toolkit-config-offline.zip` 完整解压后打开 `config.html`，无需安装开发环境。「保存到浏览器」只保存本机编辑。

工牌不联网；Wi-Fi 二维码供手机扫码，导出的配置可能含密码。个人口令模板不会打进公开固件；新用户须自行录入。

## 下载与保留数据升级

- `nabo-toolkit-app.bin`、固件 ZIP、`manifest.json`、`SHA256SUMS.txt`：保护升级，**应用只写0x10000**。
- `nabo-toolkit-config-offline.zip`：与固件 ZIP 内相同的配置页。
- `nabo-toolkit-community-full.bin`、`community-manifest.json`、`COMMUNITY_SHA256SUMS.txt`：另供社区从 **0x0完整首装**。会写默认分区表，重置NVS、设置、蓝牙绑定和个人口令；完整首装未真机验收。

本次固定应用 **2,030,864 字节**，SHA256：

```text
d748e54395bff10eaa85530d4287198607fc3fcd17f2d1da8250b272b15d1829
```

SDK固定 ESP-IDF6.0.2，ESP32-C3/8MiB/无PSRAM。旧 factory 为0x10000/0x1f0000、assets FAT为0x200000/0x600000；本次应用剩752字节，写[0x10000,0x1ffd10)，擦除截止0x200000（不含）。不要用默认 `idf.py flash`、完整镜像或整片擦除做保留数据升级。

完整镜像直接复用固定归档，**2,096,400字节**，SHA256 `9f6ac2a640fd2c056d8367c4e62349c61472c9e6acc4e607463bb9bbe729dd78`，内嵌同一已验收应用；未为发布重编译。默认分区表与上一公开版相同；bootloader来自本次固定归档，字节并非上一版同一份产物。首装范围不能混称作者设备的app-only验收。

解压固件 ZIP，使用Python3.11/esptool5.5.0。日常配置无需安装这些工具：

```text
python -m pip install esptool==5.5.0
python tools/flash_candidate.py --mode inspect --app nabo-toolkit-app.bin --sha256 d748e54395bff10eaa85530d4287198607fc3fcd17f2d1da8250b272b15d1829
python -m serial.tools.list_ports -v
python -m esptool --chip esp32c3 --port YOUR_PORT read-mac
python tools/flash_candidate.py --mode upgrade --port YOUR_PORT --expected-mac YOUR_DEVICE_MAC --app nabo-toolkit-app.bin --sha256 d748e54395bff10eaa85530d4287198607fc3fcd17f2d1da8250b272b15d1829
```

先关闭占用串口的配置页/监视器，替换为自己的端口和小写设备地址。脚本会在同一连接核对设备、容量、安全状态、实际布局、哈希和写擦范围；未知布局应停止。

### 仅早期语音开发版：无损整理

从已公开v0.3.1首次升级的人没有旧语音库，可跳过。已有v1个人模板、空间不足时，可关闭配置页，用串口终端进入主菜单后发送 `>tk.voice.compact`。返回 `@voice compact_result=0` 才表示整理成功；七词数量和轮转位置保留。它不在启动时自动运行，不重录、不擦NVS分区、不改名片/快捷键/绑定。可用 `python -m serial.tools.miniterm YOUR_PORT 115200 --eol LF` 打开终端，结束按Ctrl+]；开串口可能重启设备，先等欢迎播完。

## 验收范围和已知限制

- **Build PASS；Host tests PASS**：213项（44 Node+144 Python+25声学探针），2,722步JS–C对拍、3变异、0跳过。
- **Device checks PASS（本轮范围）**：固定app-only安装/保护区核验；21份模板逐值无损整理，受控重启后七词仍3/3；用户确认语音输入/读书正确跳转。dev3还通过新词三录、重启识别及“你好”拒识；不把旧镜像结果称作dev4重新跑过全部项目。
- 真实USB原配置同内容保存/读回通过，同值可能由SDK跳过写入；随后实际将个人名片二维码改为[作者全部作品](https://ai-passport.folotoy.cn/creators/?id=14101)，真实改动的1648B配置记录保存、受控重启读回和手机扫码确认均通过，其余配置保持。个人配置不包含在下载中。最大4016B只是在实际SDK后端副本上的不透明存储测试，不是合法最大配置schema验收。
- **Unverified**：长稳、多用户/背景噪声/完整七词准确率与拒识矩阵、冷断电和真实Flash故障、极端容量/大配置、功耗及原平台/回连/深睡门槛。分数不是准确率。
- Windows耳机曾在PC USB连线时断续，电池/外部充电对照正常；用户最后反馈插着也恢复正常并停止调查。原因未定，本版没有更改BLE参数或驱动，也不宣称已修复共存问题。

本版为公开实验测试版。社区保存/提交审核/公开状态分别记录，GitHub发版不等于社区已更新或已上架。源码MIT；NABO形象与素材依NOTICE.md，不随MIT授权。本项目与FoloToy官方无关联。

English: This experimental release adds speaker-enrolled offline navigation for seven Chinese commands, including voice input that only opens Typeless. Enroll three examples on the badge; recognition never starts a tool action automatically. The exact hardware-accepted app is reused. Old templates can be compacted explicitly without changing coefficients/counts/rotation. App-only at0x10000 preserves the existing layout/data; the separate0x0 image resets default partitioning/NVS/bonds/templates and has not had a hardware first-install test.213 host checks passed. A real personal-card URL change, controlled-restart readback and phone scan passed. Long stability, broad recognition/noise coverage and intermittent PC-USB headphone coexistence remain unverified or unresolved.
