<p align="right"><strong>简体中文</strong> · <a href="CONFIGURATION.md">English</a></p>

# 快捷键和名片配置（F2/F3）

公开入口：[NABO工具箱配置](https://liutupi.github.io/nabo-toolkit/)；离线包见[Release](https://github.com/Liutupi/nabo-toolkit/releases)。顶部“名片 / Wi-Fi 二维码”可直达编辑区。

开发入口是现有 `game-art/toolkit/prototype/config.html`，无需联网。页面分开提供浏览器保存和USB工牌读写：只有点击“写入工牌并核对”才向所选串口写入。**F2 dev2已授权app-only安装，真实USB保存/读回/两轮重启保留和20次连续读回通过；自定义文字/名片/扫码及成功保存后断电保留也通过；浏览器真实权限弹窗和传输中拔线仍待验收。**

当前工牌已安装F3 dev3；F2协议沿用。在Chrome/Edge打开本地页面或localhost服务，用数据线接工牌，点“连接工牌”选择重新枚举的正确USB串口。可以先“从工牌读回”，再编辑并“写入工牌并核对”。先释放串口监视器；打开端口可能重启，USB复位后可能需要重新连接页面。页面不自动选择/打开串口；中断/超时后先读回核对，不自动重写。

可编辑 1–6 组快捷键、每组上/OK/下，以及 1–3 张名片。录键或手动勾选修饰键支持左右 Ctrl/Shift/Alt/Win；Mac/iPhone 与 Windows/安卓两套分别保存。可清空某一平台绑定；完全未设置的键不发 HID。会议、PPT、媒体、拍照的固定键位保持原样。默认配置始终来自作者原 `tk_hid.js`，恢复默认只修改编辑内容，需另外保存。

| 字段 | 限制 |
|---|---|
| 根结构 | `v:1`，必须同时有 `groups`、`cards`；拒绝未知字段、重复键 |
| 组名 / 键名 | 最多各 8 个 Unicode 字符；组名非空 |
| 组合键 | `{mod,key}`；mod 0–255，key 为0或4–115，修饰键单独组合使用 key0；平台项可为null |
| 多媒体键 | 播放暂停、下一曲、上一曲、音量加、音量减 |
| 文字宏 | 最多64个可打印 ASCII 字符或换行；不跳过非法字，而是拒绝保存 |
| 名片 | 标题非空且最多6字；名字最多24字；说明最多32字；二维码非空且最多160个UTF-8字节 |
| 总配置 | 规范化紧凑 JSON ≤4000 UTF-8字节；数值只接受非负整数 |

键名从旧页面6字限制扩为8字，以容纳原默认“播放 / 暂停”；名片名字从旧页面16字扩为24字，保留默认 `github.com/Liutupi`。这是输入限制修正，默认键位未改。配置导入、浏览器保存、USB写入使用同一验证规则；导出为紧凑JSON，确保可原样导入。Wi-Fi二维码内容由页面转义生成，**密码会明文存入工牌/备份**，分享文件前删除私人内容。

固件的紧凑中文备用字库来自同一现有思源黑体，中日韩统一表意文字及常用标点共21,281字形，16px/1bpp，直接从Flash读取，按显示字号缩放。它不占整幅字形位图RAM；非字库字符用方框代替。F3已接入原七条动画和专用语音，用户验收见HANDOFF22。

## USB 协议

每行ASCII，以LF结束；CRLF亦可。数据按UTF-8 JSON计算长度和CRC32（IEEE，初值/末异或均0xffffffff），每段原始数据≤48字节，标准规范base64≤64字符。每段收到确认后再发下一段。

| 请求 | 成功回复 |
|---|---|
| `>tk.cfg.abort` | `tk.cfg.aborted`，取消未提交的传输 |
| `>tk.cfg.begin <字节数>` | `tk.cfg.ready <字节数>` |
| `>tk.cfg.data <base64>` | `tk.cfg.more <累计字节数>` |
| `>tk.cfg.end <8位十六进制CRC>` | `tk.cfg.ok <规范JSON字节数> <CRC>` |
| `>tk.cfg.read` | `tk.cfg.begin <字节数>`，多行 `tk.cfg.data <base64>`，最后 `tk.cfg.end <CRC>` |

写入必须收齐长度、CRC正确、结构/范围/UTF-8都通过，才保存NVS `nabo_tk/cfg_v1`；这是带 `TKCF`/版本/长度/CRC 的二进制封装，载荷为规范JSON。成功提交后才切换UI模型，组数/名片数缩小时收敛当前索引。读回每轮输出一段，传输期间不自动休眠。网页在提交后自动读回，校验CRC并比较完整配置，核对一致才显示成功。

失败回复 `tk.cfg.err <固定代码>`，不回显拒绝的配置。常见代码：`size/json/utf8/depth/keys/number/version/groups/cards/name/label/key/media/text/card/crc/data/state/busy/line/timeout/test/memory/storage`。接收10秒无数据或总计60秒到期会取消；超长行、坏base64、错序/超量数据、重复begin、test模式写入都拒绝，当前生效配置不切换。读取损坏NVS记录时使用默认并报错，保留原记录，不擦库。

`>tk.test=1` 时拒绝配置写入，可读真实已保存配置；模拟动作不持久化。test不是整个NimBLE/NVS生命周期的只读锁。设置、蓝牙槽和配对密钥继续使用独立键，此功能不删除它们。

## 宿主验证与构建

激活项目ESP-IDF6.0.2并准备Node、Python、宿主C11编译器后，Windows用 `./tools/validate.ps1 -Stage F2`；Linux/WSL对应IDF环境用 `./tools/validate.sh --f2`。配置层同时使用F1和F2 defaults，产物在 `build/f2/`。IDF6的JSON组件采用锁定的 `espressif/cjson 1.7.19~2`，原cmake_utilities固定为1.1.1，其余依赖版本保留。

宿主87项/1,710步对拍包含网页/C同一语料、生产JS至C端、RAM持久化/故障及模型/渲染。随后生产JS客户端已通过真实USB验证配置保存、自动读回、异常拒绝、两轮硬件复位保留和20次读回；原配置恢复。dev1连续读回丢段被长度检查捕获，dev2启用带缓冲USB驱动后完成上述检查。自定义文字/名片/扫码和保存后断电重开已由用户及USB读回验收；真实浏览器权限/传输中拔线、写入中断电/硬件故障语义仍须独立验证；见[记录](VALIDATION.zh_CN.md)和validation/f2.json。
