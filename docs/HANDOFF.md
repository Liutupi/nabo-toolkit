# 交接本

更新：2026-10-27 · 阶段 M0（设计 + 浏览器原型）完成 · 提交见 `git log`

## 1. 现在是什么状态

《NABO 工具箱》是一个**离线的蓝牙遥控工牌**：工牌模拟蓝牙键盘，用上 / 下 / OK 控制电脑、手机、平板，不联网。

- 开机画面 + 开机语音“那波，陪你遥控万物！”（和算命机、声音实验室同一做法，DESIGN 5.0）。原型里语音先用浏览器 TTS 代替。
- 设计定稿到 M0：快捷键（截屏 / 粘贴 / 复制、Typeless 等 6 组）、PPT 翻页笔、会议键、媒体遥控、拍照快门、名片二维码，加连接和设置。
- 浏览器原型能完整操作所有页面，右侧显示每次会发给电脑的 HID 报告。
- 网页配置页原型能录组合键（分左右修饰键），保存后工牌原型马上生效。
- **美术还没开始**：规格和 Codex / Grok 提示词已写好，NABO 现在是参考图原样裁出的占位帧。
- **固件还没开始**。

## 2. 先读这些

| 文件 | 内容 |
|---|---|
| `AGENTS.md` | 维护约定（必须遵守） |
| `game-art/toolkit/DESIGN.md` | 规则、按键、连接、各工具细节、配置页、界面、预算 |
| `game-art/toolkit/ART_BRIEF.md` | 美术规格：第 0 节身份锁定、第 1 节分工、行头清单、13 条镜头 |
| `game-art/toolkit/CODEX_PROMPTS.md` | 给 Codex 的 3 轮提示词 |
| `game-art/toolkit/GROK_PROMPTS.md` | 给 Grok 的 2 批图生视频提示词 |
| nabo-passport-game skill | NABO 项目的通用流程（M0–M4、发布） |

## 3. 文件职责

| 文件 | 职责 |
|---|---|
| `game-art/toolkit/prototype/tk_hid.js` | 键位表：HID 键码、会议软件快捷键、6 组默认快捷键、录键用的键码映射 |
| `game-art/toolkit/prototype/tk_core.js` | **规则的标准答案**：菜单、各工具、连接、设置的状态机（纯逻辑，时间作为参数） |
| `game-art/toolkit/prototype/tk_draw.js`、`tk_draw_tools.js`、`tk_draw_boot.js` | 按固件版式画 240×320 画面（`tk_draw_boot.js` 是开机画面） |
| `game-art/toolkit/audio/VOICE.md` | 开机语音的生成和处理步骤；原片放 `audio/originals/` |
| `game-art/toolkit/prototype/index.html` | 工牌原型（键盘 ↑ ↓ Enter，按住 0.5 秒为长按；调试钩子 `TOOLKIT.press/state/advance`） |
| `game-art/toolkit/prototype/config.html`、`config.js` | 网页配置页原型（存在浏览器 localStorage；正式版改为 Web Serial 写入） |
| `game-art/toolkit/prototype/assets/` | NABO 占位帧（参考图原样裁切，不是重画） |
| `game-art/toolkit/art/reference/nabo-idle.png` | NABO 身份参考图，不要改 |

## 4. 怎么跑

```sh
python3 -m http.server 8770 --directory game-art/toolkit/prototype
# 打开 http://localhost:8770/          工牌原型
# 打开 http://localhost:8770/config.html  配置页
```

## 5. 待办（按顺序）

| # | 任务 | 谁 | 完成标准 |
|---|---|---|---|
| 1 | **Codex 第 1 轮**：S0 基础形象 + S0R 拿遥控器 + S1 讲师 A/B | Codex，用户验收 | `art/design/r1/` 下有 S0、S0R、S1_A、S1_B、对比图、小尺寸检查图、README；用户确认是 NABO 本人并选定 S1 |
| 1b | **开机语音**：即梦“阳光小男孩”读“那波，陪你遥控万物！” | 用户生成，Claude 处理 | 原片在 `audio/originals/`；`audio/boot-welcome.wav`（16 kHz 单声道）和 `generation.json` 写好 |
| 2 | Codex 第 2 轮：S2–S5 行头 | Codex，用户验收 | 6 张起始图都放进 `art/start/` |
| 3 | Grok 第 1 批：开机欢迎 + 6 条待机循环 | 用户跑 Grok | 原片放进 `art/video/batch1/` |
| 4 | 审片、抽帧、接进原型 | Claude | `art/qa/` 有审查记录；原型里换上真 NABO |
| 5 | Grok 第 2 批 + Codex 第 3 轮（风格板，用户选）+ 第 4 轮（字标、图标、九宫格、数字） | 用户 / Codex | 同上 |
| 6 | **蓝牙探路**（M2 前） | Claude + 用户的工牌 | 离线底座打开 NimBLE 后空闲堆 ≥ 60 KB；Mac / Windows / iPhone / 安卓配对和重连；相机快门实测 |
| 7 | 会议快捷键实测 | 用户 | DESIGN 5.2 的表逐条确认 |
| 8 | M2–M4 固件 | Claude | 按 skill 流程 |

## 6. 注意事项

- 会议快捷键表是凭记忆写的，**全部没实测**。
- 用户的键盘没有 F13 以上的键，不要设计依赖 F 键的默认键位。
- 截屏默认用“截到剪贴板”（Mac Ctrl+Cmd+Shift+4，Windows Win+Shift+S），截完直接粘贴。
- GitHub 私有仓库：https://github.com/Liutupi/nabo-toolkit（main）。

## 7. 给 Codex 的开场白（可直接复制）

> 这是《NABO 工具箱》（ESP32-C3 AI Passport 工牌的离线蓝牙遥控工具）。先读 `AGENTS.md`、`docs/HANDOFF.md`、`game-art/toolkit/ART_BRIEF.md`。今天做美术：请打开 `game-art/toolkit/CODEX_PROMPTS.md`，执行“第 1 轮”。NABO 的身份不能改，必须拿 `game-art/toolkit/art/reference/nabo-idle.png` 左帧做图像编辑，只换衣服。只在 `game-art/toolkit/art/` 下工作。
