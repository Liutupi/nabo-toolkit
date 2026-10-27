# 交接本

更新：2026-10-27 · 设计、运行逻辑、界面风格已定稿；**接下来主要由 Codex 实现** · 提交见 `git log`

## 1. 现在是什么状态

《NABO 工具箱》是一个**离线的蓝牙遥控工牌**：工牌模拟蓝牙键盘，用上 / 下 / OK 控制电脑、手机、平板，不联网。

| 部分 | 状态 |
|---|---|
| 玩法规则 | ✅ 定稿（DESIGN.md），浏览器原型能完整操作（`prototype/`） |
| 运行逻辑 / 固件框架 | ✅ 定稿（FIRMWARE_PLAN.md）：模块、任务、连接状态机、发送、配置写入、休眠、测试、“能用”的验收标准 |
| 界面风格 | ✅ 定稿“工牌挂绳”（UI_DESIGN.md）：配色、字体、每个画面的坐标 |
| 美术 | 🟡 第 1 轮身份通过，**S1 选 B（炭灰西装 + 浅蓝衬衫）**。`art/start/` 里现在的 S0、S1 是 r1 原版，**还要返工**：去头发黑边、构图放宽到腰部、补 S0R（CODEX_PROMPTS“第 1 轮返工”）。`art/design/r2/` 已开始第 2 轮，但构图要跟返工后的新构图一致，**先做完返工再继续第 2 轮** |
| 开机语音 | ⬜ 等用户在即梦生成“那波，陪你遥控万物！”（`audio/VOICE.md`） |
| 固件 | ⬜ 没开始 |

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
| A1 | 原型跟上 UI_DESIGN 第 6 节（版式、配对码弹窗、`sim('passkey')`） | Codex | 原型画面和 UI_DESIGN 第 4 节一致；无控制台错误 |
| A2 | 对拍轨迹：`tests/tk_golden/record_golden.js`（node 直接跑 `tk_core.js`）+ 键位表导出 JSON | Codex | 轨迹覆盖所有页面和连接事件 |
| A3 | **F0 蓝牙探路**（FIRMWARE_PLAN 第 6 节） | Codex 写，用户的工牌实测 | 配对、回连、空闲堆三项过；**过不了先停下报告** |
| A4 | **F1 能用版**：模型、键位表、全部页面（占位画面）、3 槽连接、开机画面、休眠 | Codex 写，用户实测 | FIRMWARE_PLAN 第 1 节 10 项全过 → 可以先发布“能用版” |
| A5 | F2 配置页 Web Serial 写入和读回 | Codex | 写入立即生效、断电保留、坏数据不破坏旧配置 |
| A6 | 会议快捷键逐条实测，改 `tk_hid.js` 和 DESIGN 5.2 | 用户 + Codex | 表里每条标“已实测” |

### B 线：美术（并行，不挡 A 线）

| # | 任务 | 谁 | 完成标准 |
|---|---|---|---|
| B1 | **Codex 第 1 轮返工**（CODEX_PROMPTS） | Codex，用户验收 | `art/start/` 换成返工后的 S0、S0R、S1（黑边去掉、腰部构图） |
| B2 | 开机语音 | 用户生成，Codex 按 VOICE.md 处理 | `audio/boot-welcome.wav` + `generation.json` |
| B3 | Codex 第 2 轮 S2–S5（**用 B1 的新构图**） | Codex，用户验收 | `art/start/` 共 7 张，头部位置和缩放一致 |
| B4 | Grok 第 1 批（开机欢迎 + 6 条待机） | 用户跑 Grok | 原片在 `art/video/batch1/` |
| B5 | 审片、抽帧、打包（ART_BRIEF 第 6 节） | Codex | `art/qa/` 审查记录；精灵包逐帧比对通过；原型换上真 NABO |
| B6 | Codex 第 3 轮风格板 → 第 4 轮全套界面素材 | Codex，用户确认 | `art/ui/` 齐全 |
| B7 | Grok 第 2 批 7 条动作 + 处理 | 用户 / Codex | 同 B5 |
| B8 | **F3**：素材接进固件 | Codex | 渲染测试更新截图；帧率、内存复测 |

最后 F4 发布：按 skill 第 5 节，社区封面用开机画面。

## 6. 注意事项

- 会议快捷键表是凭记忆写的，**全部没实测**（A6）。
- 用户的键盘没有 F13 以上的键，不要设计依赖 F 键的默认键位。
- 截屏默认“截到剪贴板”（Mac Ctrl+Cmd+Shift+4，Windows Win+Shift+S），截完直接粘贴。
- 出厂默认键位是作者自己电脑上的配置，别人用配置页改。
- 原型的 NABO 是参考图原样裁切的占位，不是重画。
- 参考图只有 224×224，起始图里的头部是原像素等比放大；构图放宽后头部缩放变小，反而更清楚。
- GitHub 私有仓库：https://github.com/Liutupi/nabo-toolkit（main）。
- 构建和宿主测试通过不等于能用，**FIRMWARE_PLAN 第 1 节必须在真机上过**。

## 7. 给 Codex 的开场白（可直接复制）

**功能（A 线）：**

> 这是《NABO 工具箱》（ESP32-C3 AI Passport 工牌的离线蓝牙遥控工具）。先读 `AGENTS.md`、`docs/HANDOFF.md`、`game-art/toolkit/DESIGN.md`、`game-art/toolkit/FIRMWARE_PLAN.md`、`game-art/toolkit/UI_DESIGN.md`，按 nabo-passport-game skill 的流程工作。原则是先能用再好看。今天做 HANDOFF 第 5 节 A 线的第 __ 项。改规则先改 `game-art/toolkit/prototype/tk_core.js`；固件的运行逻辑严格按 FIRMWARE_PLAN 第 4 节。做完把结果（测试数、app 大小、SHA256、真机实测数据、没验证的项）写回 HANDOFF。

**美术（B 线）：**

> 这是《NABO 工具箱》。先读 `AGENTS.md`、`docs/HANDOFF.md`、`game-art/toolkit/ART_BRIEF.md`、`game-art/toolkit/UI_DESIGN.md`。今天做 HANDOFF 第 5 节 B 线的第 __ 项，提示词在 `game-art/toolkit/CODEX_PROMPTS.md`。NABO 的身份不能改，必须拿 `game-art/toolkit/art/reference/nabo-idle.png` 左帧做图像编辑，只换衣服。只在 `game-art/toolkit/art/`（语音在 `audio/`）下工作。
