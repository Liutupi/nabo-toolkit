# 维护约定

这是《NABO 工具箱》：离线的蓝牙遥控工牌（FoloToy AI Passport，ESP32-C3）。先读 `docs/HANDOFF.md` 和 `game-art/toolkit/DESIGN.md`，按 nabo-passport-game skill 的流程工作。

- 规则以 `game-art/toolkit/prototype/tk_core.js` 为准，键位表以 `tk_hid.js` 为准：先改原型，再改文档和固件。
- **先能用，再好看**：功能（HANDOFF A 线）是关键路径，美术不挡功能发布。固件的结构和运行逻辑按 `game-art/toolkit/FIRMWARE_PLAN.md`，界面按 `game-art/toolkit/UI_DESIGN.md`。
- **NABO 的身份不能改**：脸、眼睛、细圆框眼镜、发型、白帽和帽标、比例以 `game-art/toolkit/art/reference/nabo-idle.png` 左帧为准，只能换衣服和道具。必须拿参考图做图像编辑，不要重画、不要用 SVG 拼脸。帽标不能左右镜像。
- 美术只在 `game-art/toolkit/art/` 下工作，规格见 `game-art/toolkit/ART_BRIEF.md`，提示词见 `CODEX_PROMPTS.md`、`GROK_PROMPTS.md`。原片和参考图不要覆盖、不要改名；重做用 `_v2`、`_v3`。
- 不联网：不做 Wi-Fi 功能。蓝牙只做 HID 外设。
- 出厂默认键位是作者自己电脑上的配置（DESIGN 第 5.5 节），不要随意改；别人用配置页改。
- 固件阶段：整数运算；不把代码放进 IRAM；每个源文件尽量不超过约 400 行；分区表和板型身份不变；NVS 用命名空间 `nabo_tk`。
- `private/`、凭据、设备备份、NVS 和原始设备日志不得提交。配置导出文件里可能有 Wi-Fi 密码，不要提交。
- 在 macOS 外接卷上工作会产生 `._*` 文件，提交前 `find . -name '._*' -delete`。
