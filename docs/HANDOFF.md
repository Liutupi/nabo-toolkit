# 交接本

更新：2026-10-27 · 设计、运行逻辑、界面风格已定稿；**接下来主要由 Codex 实现** · 提交见 `git log`

## 1. 现在是什么状态

《NABO 工具箱》是一个**离线的蓝牙遥控工牌**：工牌模拟蓝牙键盘，用上 / 下 / OK 控制电脑、手机、平板，不联网。

| 部分 | 状态 |
|---|---|
| 玩法规则 | ✅ 定稿（DESIGN.md），浏览器原型能完整操作（`prototype/`） |
| 运行逻辑 / 固件框架 | ✅ 定稿（FIRMWARE_PLAN.md）：模块、任务、连接状态机、发送、配置写入、休眠、测试、“能用”的验收标准 |
| 界面风格 | ✅ 定稿“工牌挂绳”（UI_DESIGN.md）：配色、字体、每个画面的坐标 |
| 美术 | ✅ 七张起始图全部获用户确认，**S1 选 B（炭灰西装 + 浅蓝衬衫）**。`art/start/` 已齐全（r1b 的 S0/S0R/S1 + r2b 的 S2–S5），头部、背景、尺寸、帽标与嘴部检查通过。Grok 第 1 批七条原片已收到，535 帧完整解码；审片、固定锚点抽帧、64 色 RGB565 RLE/差分包与原型接入完成，总计 405,362 字节，解码像素差异 0。旧 `r1/`、`r2/` 不作为 Grok 输入 |
| 开机语音 | ⬜ 等用户在即梦生成“那波，陪你遥控万物！”（`audio/VOICE.md`） |
| 固件 | 🟡 F0 探路版已构建并通过完整门禁；app 643,392 字节。已获授权完成 app-only 刷写；Mac 配对/粘贴/音量/连接中内存通过，其他平台和多轮计时待测，**尚未进入 F1**。精确 SHA 与产物见 `docs/VALIDATION.md` |

**优先级：先能用，再好看。** 功能（下面的 A 线）是关键路径；美术（B 线）同时做，不挡功能发布。

## 2. 先读这些

| 文件 | 内容 |
|---|---|
| `AGENTS.md` | 维护约定（必须遵守） |
| `game-art/toolkit/DESIGN.md` | 规则：按键、连接、每个工具、开机画面和语音、配置页、设置 |
| `game-art/toolkit/FIRMWARE_PLAN.md` | **固件怎么搭、怎么运行、怎么算能用** |
| `game-art/toolkit/UI_DESIGN.md` | 界面风格和每个画面的版式 |
| `game-art/toolkit/ART_BRIEF.md` | 美术规格：身份锁定、分工、行头、14 条镜头 |
| `game-art/toolkit/CODEX_PROMPTS.md` / `GROK_PROMPTS.md` | 美术提示词 |
| nabo-passport-game skill | NABO 项目的通用流程 |

## 3. 文件职责

| 文件 | 职责 |
|---|---|
| `game-art/toolkit/prototype/tk_core.js` | **规则的标准答案**：开机、菜单、各工具、连接、设置的状态机（纯函数，时间作参数） |
| `game-art/toolkit/prototype/tk_hid.js` | 键位表：HID 键码、会议快捷键、6 组默认快捷键（作者自己的配置）、录键映射 |
| `game-art/toolkit/prototype/tk_draw*.js` | 按固件版式画 240×320（`tk_draw_boot.js` 是开机画面） |
| `game-art/toolkit/prototype/index.html` | 工牌原型（↑ ↓ Enter，按住 0.5 秒为长按；`TOOLKIT.press/state/advance`） |
| `game-art/toolkit/prototype/config.html`、`config.js` | 配置页原型（现在存浏览器，F2 改 Web Serial） |
| `game-art/toolkit/audio/VOICE.md` | 开机语音的生成和处理 |
| `game-art/toolkit/art/reference/nabo-idle.png` | NABO 身份参考图，不要改 |
| `game-art/toolkit/art/start/` | 定稿起始图（`selection.json` 记录用户的选择） |

## 4. 怎么跑

```sh
python3 -m http.server 8770 --directory game-art/toolkit/prototype
# http://localhost:8770/            工牌原型
# http://localhost:8770/config.html 配置页
```

## 5. 待办

### A 线：功能（关键路径，按顺序）

| # | 任务 | 谁 | 完成标准 |
|---|---|---|---|
| A1 ✅ | 原型跟上 UI_DESIGN 第 6 节（版式、配对码弹窗、`sim('passkey')`） | Codex | 版式、配对码和真实精灵已接入；实际浏览器操作通过，刷新后控制台无错误/警告；截图 `docs/images/prototype/` |
| A2 ✅ | 对拍轨迹：`tests/tk_golden/record_golden.js`（node 直接跑 `tk_core.js`）+ 键位表导出 JSON | Codex | 1,559 步覆盖 10 页、4 OS、6 键、5 连接事件；临时重录逐字节一致。**完整 C 模型对拍待 F1** |
| A3 | **F0 蓝牙探路**（FIRMWARE_PLAN 第 6 节） | Codex 写，用户的工牌实测 | F0 代码、固件与 40 项宿主测试已过；Mac 配对、粘贴、音量及连接中内存已通过；一次重启自动回连广播起算 701 ms。Windows/iPhone/安卓及多轮开机计时待测，完整门槛过后才开始 F1 |
| A4 | **F1 能用版**：模型、键位表、全部页面（占位画面）、3 槽连接、开机画面、休眠 | Codex 写，用户实测 | FIRMWARE_PLAN 第 1 节 10 项全过 → 可以先发布“能用版” |
| A5 | F2 配置页 Web Serial 写入和读回 | Codex | 写入立即生效、断电保留、坏数据不破坏旧配置 |
| A6 | 会议快捷键逐条实测，改 `tk_hid.js` 和 DESIGN 5.2 | 用户 + Codex | 表里每条标“已实测” |

### B 线：美术（并行，不挡 A 线）

| # | 任务 | 谁 | 完成标准 |
|---|---|---|---|
| B1 | **Codex 第 1 轮返工**（CODEX_PROMPTS） | Codex，用户验收 | ✅ 用户已回复“可以”；`art/design/r1b/acceptance.json` 绑定三张哈希，`art/start/` 已更新 |
| B2 | 开机语音 | 用户生成，Codex 按 VOICE.md 处理 | `audio/boot-welcome.wav` + `generation.json` |
| B3 | Codex 第 2 轮 S2–S5（**用 B1 的新构图**） | Codex，用户验收 | ✅ 用户回复“确认”；`r2b/acceptance.json` 绑定四张哈希，`art/start/` 已齐 7 张 |
| B4 ✅ | Grok 第 1 批（开机欢迎 + 6 条待机） | 用户跑 Grok | ✅ 七条原片已保存在 `art/video/batch1/`，原样保留 |
| B5 ✅ | 审片、抽帧、打包（ART_BRIEF 第 6 节） | Codex | `art/qa/batch1/review.json`（带说明通过）；8 个精灵包共 405,362 字节，逐帧无损解码对比 0 差异；原型已使用真 NABO。LCD/固件接入待 F3 |
| B6 | Codex 第 3 轮风格板 → 第 4 轮全套界面素材 | Codex，用户确认 | `art/ui/` 齐全 |
| B7 | Grok 第 2 批 7 条动作 + 处理 | 用户 / Codex | 同 B5 |
| B8 | **F3**：素材接进固件 | Codex | 渲染测试更新截图；帧率、内存复测 |

最后 F4 发布：按 skill 第 5 节，社区封面用开机画面。

## 6. 注意事项

- 会议快捷键表是凭记忆写的，**全部没实测**（A6）。
- 用户的键盘没有 F13 以上的键，不要设计依赖 F 键的默认键位。
- 截屏默认“截到剪贴板”（Mac Ctrl+Cmd+Shift+4，Windows Win+Shift+S），截完直接粘贴。
- 出厂默认键位是作者自己电脑上的配置，别人用配置页改。
- 原型已使用 Grok 原片处理的真实 NABO 精灵，未重画身份；菜单图标仍为程序占位，B6 未开始。
- 参考图只有 224×224，起始图里的头部是原像素等比放大；构图放宽后头部缩放变小，反而更清楚。
- GitHub 私有仓库：https://github.com/Liutupi/nabo-toolkit（main）。
- 构建和宿主测试通过不等于能用，**FIRMWARE_PLAN 第 1 节必须在真机上过**。

## 7. 给 Codex 的开场白（可直接复制）

**功能（A 线）：**

> 这是《NABO 工具箱》（ESP32-C3 AI Passport 工牌的离线蓝牙遥控工具）。先读 `AGENTS.md`、`docs/HANDOFF.md`、`game-art/toolkit/DESIGN.md`、`game-art/toolkit/FIRMWARE_PLAN.md`、`game-art/toolkit/UI_DESIGN.md`，按 nabo-passport-game skill 的流程工作。原则是先能用再好看。今天做 HANDOFF 第 5 节 A 线的第 __ 项。改规则先改 `game-art/toolkit/prototype/tk_core.js`；固件的运行逻辑严格按 FIRMWARE_PLAN 第 4 节。做完把结果（测试数、app 大小、SHA256、真机实测数据、没验证的项）写回 HANDOFF。

**美术（B 线）：**

> 这是《NABO 工具箱》。先读 `AGENTS.md`、`docs/HANDOFF.md`、`game-art/toolkit/ART_BRIEF.md`、`game-art/toolkit/UI_DESIGN.md`。今天做 HANDOFF 第 5 节 B 线的第 __ 项，提示词在 `game-art/toolkit/CODEX_PROMPTS.md`。NABO 的身份不能改，必须拿 `game-art/toolkit/art/reference/nabo-idle.png` 左帧做图像编辑，只换衣服。只在 `game-art/toolkit/art/`（语音在 `audio/`）下工作。

## 8. Codex 接续记录（2026-10-27）

- 已读取本次 `9004d56` 交接及 `FIRMWARE_PLAN.md`、`UI_DESIGN.md`，界面方向按已定“工牌挂绳”；固件 A 线仍未开始，未将美术检查描述为功能或真机验收。
- 用户在当前聊天选定 B；B1 返工文件与完整方法在 `game-art/toolkit/art/design/r1b/README.md`，对比图 `compare.png`、边缘对比 `edge_check.png`、小尺寸图 `small_check.png`、检查记录 `qa.json`。
- 头部统一 3.0 倍、偏移 `(176, 30)`，帽顶 y=60；三张人物宽度 541/549/552 px，左右留白约 230 px。背景与尺寸检查通过；不透明头部保护区域像素差异为 0；原尺寸头部内部 RGB 保持不变。动作实际出框、循环和手指稳定性待视频审查。
- 已按返工提示词将 r1b 三张复制到 `art/start/`，用户随后回复“可以”确认；`selection.json` 和 `r1b/acceptance.json` 已记录确认及哈希。原 `r1/`、旧 `r2/` 和所有原片均保留。
- 旧 r2 已生成 S2–S5 和小尺寸检查，但仍是旧胸口构图，当前不可交付 Grok。`art/design/r2/GROK_BATCH1.md` 只是预备提示词，其首帧在新构图验收并调整完 S2–S5 前不可使用。
- 新构图第 2 轮已完成于 `art/design/r2b/`：以已确认 S0 为输入编辑身体和服装，统一复用 r1b 的头部；S2/S3 的耳部配件按同一相似变换复用。四张 1024×1024、帽顶 y=60，受保护头部差异与背景错误均为 0，帽标和嘴部像素不变。结果见 `qa.json`、`compare.png`、`small_check.png`、`all_seven.png`。
- 用户已回复“确认”接受 r2b 四套行头，已复制到 `art/start/`，七张均为最终确认版本；记录在 `r2b/acceptance.json` 和 `art/start/selection.json`。
- Grok 第 1 批可以开工：准备包 `art/delivery/NABO_Toolkit_Grok_Batch1.zip`，内含 7 张 PNG、7 条完整逐镜提示词、对应表和帧哈希清单。已验证 ZIP CRC、七张帧的 SHA256 与定稿一致。包大小 4,219,958 字节，SHA256 `35ce47007426412f60cdfa07340040b3080dfa223f871aa5f9d0e7e6791e214b`。
- 下一美术节点：用户生成 00 开机欢迎 + 01–06 六条待机，原片原样放 `art/video/batch1/` 后由 Codex 审片。完整提示词和文件表在 `art/design/r2b/GROK_BATCH1.md`，S0R 已按三按钮白色遥控器修订，S5 为深蓝领口/袖口。尚未生成、提交或发布任何视频，也未 commit/push。

## 9. Codex 功能与视频接续（2026-10-27）

- 按用户最新选择，欢迎动作完整播完：1.4 s 开始，约 5.5 s 进菜单；任意键仍可跳过且不会发送 HID。规则、DESIGN 和 FIRMWARE_PLAN 已同步。
- A1：按 UI_DESIGN 调整菜单/按键卡/字体/计时/提示，补六位配对码（含前导零）、取消配对、取消类型选择及晚到事件防护，修复唤醒空闲计时。新增单 ADC 按键分类器，500 ms 长按只触发一次，延迟松开也不误触短按。
- A2：Node 直接录制基准和默认键位表，不依赖浏览器时钟。18 项 Node、7 项 C 探路逻辑、8 项精灵解码、7 项刷写保护纯逻辑测试共 40 项通过。C 按键与 JS 对比 4,000 个事件；**没有把这当成完整 C 应用模型对拍**。
- B4/B5：7 条 720×720/24 fps 视频共 535 帧全解码；人工看每 0.25 s 接触表及首尾/头部对比。欢迎遥控器短暂靠近下半脸、会议点头偏深，记录为带说明通过；未声称人工逐帧看完所有 535 帧。原片无覆盖。固定空间变换输出 256 母版、110/150 高半身和 64 头像，透明 + 63 RGB565 色，行 RLE/差分。解码与索引目标帧差异为 0；量化误差另记，不宣称与原 RGBA 无损相同。
- F0：`firmware/` 从 Adventure 提取 BSP/直绘文字渲染器，诊断 UI 独立实现；NimBLE 唯一宿主，DisplayOnly/MITM/绑定/安全连接，64 深发送队列和 45/35 ms 节奏。只保存一个上次设备与 OS 偏好，不冒充完整三槽功能。串口不打印配对码或地址；NVS 初始化错误不擦库掩盖；未初始化/链接 Wi-Fi 启动函数。
- ESP-IDF 6.0.2 完整门禁 `./tools/validate.sh` PASS；合并镜像、app、ELF、MAP、分区表、flash_args、SDK 配置已校验归档。IDF 的隐藏 `ESP_WIFI_ENABLED` 是芯片能力/依赖标记，不能用默认配置关闭；已检查最终 ELF 无 `esp_wifi_init/start/connect`，无 Wi-Fi 初始化代码。
- **Build PASS / Host tests PASS / Device tests NOT RUN**。配对、回连时间、连接中堆和最大块、实际按键效果均未验证。F0 刷写必须先取得用户授权并识别工牌，不能将已插着的未识别 USB 串口直接当作目标。完整实测表和精确哈希在 `docs/VALIDATION.md`。
- 下一步：用户授权并连接工牌 → 识别目标和分区 → 校验固定归档 → 仅 app 升级 → F0 四系统配对/重启回连/内存实测。F0 门槛未过，不开始 F1；语音 B2、风格板 B6、Grok 第 2 批和 F3 仍待后续。未 commit、push 或发布。

- 设备已由用户连接并开机，只读识别为 ESP32-C3 / 8 MiB，现有 `nabo-adventure 0.1.0` / IDF 6.0.2。实测旧分区为 factory `0x10000`、大小 `0x1f0000`，assets FAT `0x200000`、大小 `0x600000`；不能刷计划表覆盖它。F0 不访问素材，可保留此表仅替换 app；安装器显式支持这一个已测旧布局，按实际 app 分区再次校验长度/擦除扇区边界，新增两项保护测试。当前共 40 项宿主测试；尚未刷写，已向用户请求明确授权。

- 用户随后明确授权刷入 F0；精确 app `ea6789e39fddc8a7063a94d45c6687cf71d61a11eb56c55cb9aa4bcce305074c` 已在同一设备校验刷入，只写应用区并保留实测旧分区。20 秒启动观察无崩溃标记，收到 F0 菜单状态；未连接堆 196,668、最大块 114,688 字节。已请用户在 Mac 配对并测粘贴/音量，配对、回连及连接中堆仍待实测。

## 10. 下班交接：回 Windows 继续（本节为最新状态）

用户已要求将**源码和全部素材**提交推送到私有 `Liutupi/nabo-toolkit` 的 `main`。具体提交看 `git log -1`，Windows 接续步骤与可复制开场白在 `docs/WINDOWS_CONTINUE.zh_CN.md`（英文配对文件同名无 zh_CN）。

- **不用重生成素材**：七条 Grok 原片、七张确认起始图、历史尝试/原始输出/提示词/组装脚本、审片接触表、256 RGBA 母版、索引帧、八个二进制精灵和浏览器 atlas 都在仓库。`python tools/verify_assets.py` 检查 `docs/validation/assets.json` 的 364 份素材文件/90,980,640 字节，逐项 SHA256 与长度对照。`.gitattributes` 固定 LF 和二进制媒体，避免 Windows 换行破坏轨迹与素材校验。
- **功能**：A1/A2 完成；F0 已运行工牌。用户确认 Mac 配对、粘贴、音量都正常；串口 5 次成功/0 失败。连接中堆至少 195,604 字节、最大块 114,688 字节，内存门槛通过。一次串口打开引起真实 USB 重启并自动回连，广播起算 701 ms；多轮“开机到就绪”精确计时仍待做，不能写成三轮都过。
- **下次先测**：用户有 iPhone，今天下班未做；回 Windows 后先测 Windows/iPhone 配对与 HID、连接中内存、重复三秒重启回连，安卓仍需补。当前不开始 F1，除非用户明确修改 F0 验收范围。B2 语音、B6 风格板、第二批 Grok 动作、F3 固件美术仍待后续。
- **设备注意**：factory 为 `0x10000/0x1f0000`，FAT assets 为 `0x200000/0x600000`，与构建计划表不同。当前只刷 app，保留旧表；原 bootloader 日志为 IDF 5.5.3，app 为 IDF 6.0.2。不要直接运行默认 `idf.py flash` 覆盖分区表；Windows 重新识别 COM 与芯片，不沿用 Mac 串口/私有 MAC 收据。串口打开会造成 USB_UART_CHIP_RESET，要计入测试副作用。
- **环境**：SDK 固定 ESP-IDF 6.0.2；BSP 及依赖锁定元数据已在仓库，managed_components、SDK 和 build 由 Windows 重建。完整宿主门禁需要 Node、Python、宿主 C11 编译器，IDF 的 RISC-V 编译器不是宿主 cc；具体 Git Bash/WSL/原生 Windows 命令见接续文档。
- **当前验证**：40 项宿主测试 + JS 1,559 步重录一致 + 精灵逐像素解码 + F0 完整构建/合并/归档校验 PASS。完整 JS–C 应用状态对拍仍未实现。设备精确 app SHA256 及脱敏结果见 `docs/VALIDATION.zh_CN.md`、`docs/validation/f0.json`。
- **不入库**：凭据、设备 MAC/绑定、原始日志与私有收据、build/ELF/MAP；不影响 Windows 用已齐素材接着开发。设备当前已运行 F0，不需要为了接班重新刷。未创建 Release/社区发布。
