<p align="right"><strong>简体中文</strong> · <a href="VALIDATION.md">English</a></p>

# 验证记录 — 2026-10-27

Build: PASS  
Host tests: PASS（40 项）  
Device tests: PASS（刷写/启动、Mac 配对/粘贴/音量、Mac 连接中内存）；完整 F0 验收未完成  
Unverified: Windows/iPhone/安卓配对、重复开机到就绪三秒计时、其他系统 HID、完整屏幕/按键验收、休眠及 F1。

已使用项目 FIRMWARE_PLAN 指定的 **ESP-IDF 6.0.2**，从受版本管理默认配置生成隔离配置，运行完整 `./tools/validate.sh` 通过。含 18 项 Node、7 项 C 探路/按键、8 项精灵、7 项刷写保护测试、JS 重录一致性、差异空白检查、构建/合并/分区验证及精确归档校验。未套用通用 skill 的 5.5.3 默认版本。

| 产物 | 字节 | SHA256 |
|---|---:|---|
| F0 app | 643,392 | `ea6789e39fddc8a7063a94d45c6687cf71d61a11eb56c55cb9aa4bcce305074c` |
| 合并镜像 | 708,928 | `42b610327eb726941ef93bc4cf9a6caeecdf937b4a91bcebe1d656b8d7f0263b` |
| ELF | 8,540,112 | `70768e4ab69942875fc8d4e83dfec7b1e3fc99fcd99dd295355a3bafd854311f` |
| MAP | 5,738,838 | `2ecc8694beba91a46394ac10d7adbdff0d6c640446aed963a88319bbe8e9c289` |

精确归档：`build/firmware/42b610327eb726941ef93bc4cf9a6caeecdf937b4a91bcebe1d656b8d7f0263b/`，含匹配的 app/合并镜像/ELF/MAP、引导程序、分区表、刷写参数、SDK/构建元数据。用 `python3 tools/archive_firmware.py verify <归档目录>` 再校验。app 小于计划 factory 的 4,128,768 字节。二进制/调试文件已由 Git 忽略。同一镜像再次验证保留首份已验证归档；当前默认配置文件的注释与首份源码快照不同，生成的 SDK 配置和镜像哈希相同。

NimBLE 仅 peripheral/broadcaster，1 连接、3 绑定、NVS 持久化、运行时内存池，DisplayOnly + MITM + 安全连接。NVS 初始化失败不擦库。IDF 6.0.2 隐藏的 `ESP_WIFI_ENABLED` 是芯片能力标记，蓝牙组件会依赖 Wi-Fi 组件，默认配置强制关闭不会生效；门禁已检查 ELF 不含 `esp_wifi_init/start/connect`，固件不初始化 Wi-Fi。

F0 是独立诊断菜单/测试页，只保存一个上次设备和 Mac/Windows 偏好，不含完整模型、三槽 UI、开机动画、语音和休眠。`ready_ms` 从广播开始，验收三秒回连要结合开机时间戳；松开报告失败会先重试再断连。

| F0 真机门槛 | 要求 | 结果 |
|---|---|---|
| 配对 | Mac、Windows、iPhone、安卓；需要时能输入六位码 | Mac PASS；其余待测 |
| 重启回连 | 上次设备三秒内自动认证/订阅就绪 | 一次真实 USB 重启自动回连，广播起算 701 ms；多轮全程计时待做 |
| 连接中内存 | 空闲堆 ≥60 KiB，最大块 ≥30 KiB | Mac PASS：至少 195,604 / 114,688 字节 |
| HID | Mac Cmd+V / Windows Ctrl+V、音量加、不粘修饰键 | 用户确认 Mac 粘贴/音量正常，5 次成功/0 失败；其余待测 |

用户已确认正确设备开机并连接。对 `/dev/cu.usbmodem212401` 只读识别，确认 ESP32-C3、8 MiB，无安全启动/Flash 加密限制；现有 `nabo-adventure 0.1.0` / IDF 6.0.2。首次严格布局检查拒绝写入；随后实测旧表为 NVS `0x9000/0x6000`、PHY `0xf000/0x1000`、factory `0x10000/0x1f0000`、FAT assets `0x200000/0x600000`，MD5 正确，与构建计划表不同。F0 不访问 assets/files，643,392 字节 app 可放入较小的旧 factory。安装器仅显式接受计划表或这一实测旧表，再按实际 factory 大小检查候选和擦除扇区边界；新增旧布局/超长候选两项测试。不能将构建分区表刷到这台设备。MAC、原始检查输出仅存忽略的 `private/device/`，未要求或读取全 Flash 备份。

用户已在当前聊天明确授权“允许，刷入 F0 并开始测试”。已先重验固定归档，核对同一串口和私有设备 MAC，保留实测旧表完成 app-only 刷写：镜像 `[0x10000, 0xad140)`，擦除扇区 `[0x10000, 0xae000)`，写后 app 校验 PASS。没有写合并镜像、分区表、NVS 或素材区，没有整片擦除。随后 20 秒串口观察收到 F0 菜单状态，无崩溃标记。未连接时空闲堆 196,668 字节、最大块 114,688 字节、最低堆 189,908 字节；**不是连接中堆验收**。用户已确认 Mac 配对、OK 粘贴与上键音量正常；串口收到 5 次成功、0 次失败。Mac 连接中堆最低观察值 195,604 字节，最大块 114,688 字节，超过门槛。串口打开会触发 USB_UART_CHIP_RESET；已观察一次实际重启自动回连，广播起算 701 ms，重复开机全程计时尚未完成。原引导程序为 IDF 5.5.3，未覆盖。用户有 iPhone，因下班交接，本轮未继续测；Windows/iPhone/安卓留待接续。屏幕完整效果尚待用户验收。F0 全部门槛未过前不开始 F1。

原型：通过实际浏览器控件操作十个页面，检查配对码、Typeless 右修饰键、PPT 计时、相机倒数及菜单/连接/设置/名片；最后刷新之后控制台错误/警告为零。截图位于 `docs/images/prototype/`；`overview.png` 是实际浏览器截图裁切拼接，不是真机证据；浏览器不向设备真实发 HID。

JS 基准共 1,559 步，覆盖 10 页、4 OS、6 键、5 连接事件；三项故意修改的时间/修饰键/连拍节奏会被测试抓到。C 按键与 JS 对比 4,000 次事件，另测 uint32 回绕；完整 C 应用状态对拍待 F1。

视频：7 条 720×720/24 fps 原片，535 帧全自动解码。人工检查每 0.25 秒接触表、首尾和头部对比，说明与源哈希在 `art/qa/batch1/review.json`。欢迎 4,042 ms，从 1.4 秒播到约 5.44 秒；用户已选 5.5 秒进菜单、任意键跳过。8 个精灵包共 405,362 字节；解码与索引目标逐像素一致，RGBA 量化损失另记；LCD 可读性/帧率、C 解码器待 F3。语音、界面美术和 Grok 第 2 批动作仍待后续。

用户已要求将当前源码和全部素材提交推送至私有仓库 main；交接见 `WINDOWS_CONTINUE.zh_CN.md`，具体提交以 git log 为准。未创建发布版本。
