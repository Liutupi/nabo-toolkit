# NABO 工具箱 · Grok 第 1 批

七张首帧已全部由用户确认，S1 使用 B 套。只使用本包 frames/ 内的 PNG。

1. 对照下表，一次上传一张首帧到 Grok 的图生视频。
2. 打开对应的 prompts/ 文本，整段复制为该条提示词；完整说明见 GROK_BATCH1.md。
3. 目标 720×720、24 fps。00 约 3.5 秒；01–06 约 3 秒，循环尽量锁同图为首尾帧。若界面不提供某项控制，保留实际原片并告知后续审片人员，不自行转换。
4. 下载原片，按表中名称保存。重拍加 _v2、_v3，旧片保留，不缩放、不改帧率、不抠绿、不剪辑。

| 镜头 | 首帧 | 提示词 | 原片文件名 |
|---|---|---|---|
| 00 开机欢迎 | frames/S0R_remote.png | prompts/00_welcome.txt | tk00_welcome_source.mp4 |
| 01 基础待机 | frames/S0_base.png | prompts/01_idle_base.txt | tk01_idle_base_source.mp4 |
| 02 讲师待机 | frames/S1_ppt.png | prompts/02_idle_ppt.txt | tk02_idle_ppt_source.mp4 |
| 03 会议待机 | frames/S2_meet.png | prompts/03_idle_meet.txt | tk03_idle_meet_source.mp4 |
| 04 媒体待机 | frames/S3_media.png | prompts/04_idle_media.txt | tk04_idle_media_source.mp4 |
| 05 摄影待机 | frames/S4_cam.png | prompts/05_idle_cam.txt | tk05_idle_cam_source.mp4 |
| 06 快捷键待机 | frames/S5_macro.png | prompts/06_idle_macro.txt | tk06_idle_macro_source.mp4 |

视频交回：/Volumes/liutupi/ai passport xiaozhi/nabo-toolkit/game-art/toolkit/art/video/batch1/

原片回来后由 Codex 审查身份、镜像、循环、手指、道具和出框，再处理精灵；静态首帧确认不代表视频已经验收。
