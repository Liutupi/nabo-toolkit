# NABO 工具箱 · v0.3.2-voice-dev4 社区更新准备稿

这是原项目 **1701**「NABO 工具箱 · 随身蓝牙遥控器」的新固件/文字准备稿，**未在本轮保存到社区、未提交审核、未确认公开**。用户授权更新 GitHub、新固件和原社区条目，图片保持原样。六个字段已备齐；本目录不代表平台保存结果。

本轮社区界面工具被策略中止，无法可靠确定页面 URL，因此停止社区页面操作，也不通过 API 绕过。原项目此前的“审核中”是 v0.3.1 历史状态，不代表本版已提交。GitHub 的发布状态由最终发布核验单独确认。

发布前匿名复核发现[原公开条目](https://ai-passport.folotoy.cn/plays/1701/)已上架，仍为上一版2,077,152B/9bcc…完整固件；不是本次dev4。五张公开WebP逐张重新下载，字节和SHA均与上一版接受的图片相等，封面及顺序未动，见[公开预检](public-preflight.json)。

| 字段 | 中文 | English |
|---|---|---|
| 介绍 | [COPY_ZH.md](COPY_ZH.md) | [COPY_EN.md](COPY_EN.md) |
| 使用方法 | [USAGE_ZH.md](USAGE_ZH.md) | [USAGE_EN.md](USAGE_EN.md) |
| 更新记录 | [CHANGELOG_ZH.md](CHANGELOG_ZH.md) | [CHANGELOG_EN.md](CHANGELOG_EN.md) |

## 版本和安装边界

- 标签：`v0.3.2-voice-dev4`，公开实验测试版，不称稳定版或全门槛验收通过。
- 计划 Release：[v0.3.2-voice-dev4](https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.2-voice-dev4)；本准备稿不单独宣称 Release 已上线，资产须由正式发布核验确认。
- 配置页：[NABO 配置页](https://liutupi.github.io/nabo-toolkit/)；[源码仓库](https://github.com/Liutupi/nabo-toolkit)。正式源码提交以 Release manifest 为准，本稿不预填未确定的提交号。
- 固定 app：**2,030,864 字节**，SHA256 **`d748e54395bff10eaa85530d4287198607fc3fcd17f2d1da8250b272b15d1829`**。复用已验收固定产物，不为打包重编译。
- 原用户保留数据须使用受保护 **app-only `0x10000`** 升级；旧 factory 为 `0x10000/0x1f0000`，assets FAT 为 `0x200000/0x600000`。不默认 flash、不刷默认表、不整片擦除。
- 社区完整首装从 **`0x0`** 写默认分区表并重置 NVS、配置、蓝牙绑定及个人样例；安装后需本人重新录入/配置。**完整首装未真机验收**，不能沿用 app-only 验收。社区完整镜像的打包/上传/下载核验另记，当前没有本版社区文件保存证明。

## 原五图只引用，不产生新图片

本目录没有新增图片，不重绘、重排、重传、替换或删除平台图片。下表只是原文件/原修订资产引用，未在本轮打开或操作社区图像。

| 原顺序 | 本地历史参考 | 原平台修订资产参考 |
|---|---|---|
| 1 封面 | [01-cover.png](../v0.3.0-f3-dev3/01-cover.png) | [原图 0](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/0?v=1) |
| 2 六工具 | [02-six-tools.png](../v0.3.0-f3-dev3/02-six-tools.png) | [原图 1](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/1?v=1) |
| 3 操作 | [03-controls.png](../v0.3.0-f3-dev3/03-controls.png) | [原图 2](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/2?v=1) |
| 4 配置 | [04-configuration.png](../v0.3.0-f3-dev3/04-configuration.png) | [原图 3](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/3?v=1) |
| 5 配对/范围 | [05-pairing-and-scope.png](../v0.3.0-f3-dev3/05-pairing-and-scope.png) | [原图 4](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/4?v=1) |

原图为玩法示意/C 宿主渲染，非 LCD 实拍；其中旧版本和键位为历史示意，**本版文字与实际界面优先**。原图历史核验见[上版记录](../v0.3.1-remote-dev2/README.md)，不能据此声称本轮重新下载或平台图像检查通过。六大工具、五组默认快捷键和七个语音目标是三个不同数量。

## 本版范围与证据

- 主菜单长按底部 OK 进入语音查找。本人分别录三次七个固定短口令；短 OK 匹配全部已录词，成功只导航，不自动发 HID。Typeless 进组后再按原键。
- 不持续监听、不联网、不保存/上传原始录音。个人模板只在本机，公开固件无作者样例；不宣称通用 ASR、身份验证或理解任意句子。
- 无损紧凑 A/B 记录与容量预检；旧模板整理仅通过明确 USB `>tk.voice.compact` 发起，不在开机自动迁移。新副本核验后才退休同词旧记录，样例、全部系数、counts 和 next 不变。容量有限，拒存不等于无限覆盖能力。
- 原欢迎、开机/按键音、工具动画、五组默认快捷键、媒体音乐/抖音与 30 秒息屏遥控保留。暗屏长 OK 只亮屏，其他原工具动作不随语音导航自动触发。
- **Build / Host tests：PASS**，ESP-IDF 6.0.2、ESP32-C3、8 MiB、无 PSRAM；213 项（44 Node + 144 Python + 25 声学探针）、2,722 步 JS–C 对拍、3 变异、0 跳过。宿主合成音频不是真人准确率。
- **Device tests：有范围通过**。本人最终确认语音输入/读书正确、没有卡住重启；21 样本共 638 帧整理前后所有系数/count/next 精确一致，受控重启保留七词各三条。未将未知意图的查询或留一分析换算为产品准确率。
- 真机可用 NVS entries 251；同内容 USB 配置保存/读回五组三卡通过，但可能是 SDK 同值跳过。随后个人名片链接真实改写、受控重启读回和手机扫码通过，其他配置保留。独立实际 SDK 后端副本对 1,629B 改动配置及 4,016B opaque blob 写入/重建读回通过；4,016B 不是合法最大配置 schema 的验收。
- **PC USB 耳机共存原因仍未定**：曾间歇断续；电池/外电对照正常，最终用户报告插 PC USB 当前也正常，并要求先停止排查。未改 BLE 参数或驱动，不称已修复；电池/外电仅为已测绕行方式。
- **Unverified**：长稳、更多人/背景噪声、完整七词矩阵、冷断电与真实 Flash 故障、极端容量/GC、功耗、完整首装与历史平台/回连/三槽/睡眠等未测门槛。历史失败证据不删除。

本文和六字段仅是准备产物；社区上传、保存、提交、审核、公开状态及当前文件下载校验，须在实际完成后分别记录。当前不能报告本版“已提交审核”或“已公开”。
