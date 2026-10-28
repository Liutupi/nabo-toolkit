# NABO 工具箱 · v0.3.1-remote-dev2 社区更新记录

本次更新现有项目 **1701**「NABO 工具箱 · 随身蓝牙遥控器」，不是另建玩法。用户明确授权发布新固件并更新原条目，**只更新固件/文字，不动原上传图片**。

**已更新并重新提交审核，当前“审核中”，尚未公开。** 用户手动撤回原投稿并进入编辑后，继续原项目1701/同一可变修订3928，更新固件与双语内容，没有另建项目。[工作台](https://ai-passport.folotoy.cn/account/?project=1701)不是公开玩法页；publicly_published=false、public_url=null。

本目录保存实际提交的[中文介绍](COPY_ZH.md)、[中文用法](USAGE_ZH.md)、[英文介绍](COPY_EN.md)、[英文用法](USAGE_EN.md)、[中文更新记录](CHANGELOG_ZH.md)与[英文更新记录](CHANGELOG_EN.md)，六个保存字段与本地文本归一空白后一致。原目录的[历史首次投稿记录](../v0.3.0-f3-dev3/README.md)保留v0.3.0快照；同一3928 href现在已替换为新二进制，旧下载记录不是当前文件。

## 本轮链接和固定固件身份

- 已发布本版Release：https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.1-remote-dev2 。8个资产匿名重新下载、字节/SHA与固定产物相等，app-only ZIP37成员校验通过。
- 已核验配置页：https://liutupi.github.io/nabo-toolkit/ 。五组/实体UP-DOWN-OK版已公开，manifest及11个可访问文件匿名HTTP200、字节/SHA相等；本版离线配置包匹配。旧v0.3.0/f8b8ad8/20261028快照保留原内容，不混称本版交付。
- 源码：https://github.com/Liutupi/nabo-toolkit 。
- 现有创作者项目：https://ai-passport.folotoy.cn/account/?project=1701 。这是项目工作台，不是已确认的公开玩法页。
- 固定app：`nabo-toolkit-app.bin`，**2,011,616字节**，SHA256 `b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe`；版本 `0.3.1-remote-dev2`，app-only写`0x10000`。
- 社区完整首装：`nabo-toolkit-community-full.bin`，**2,077,152字节**，SHA256 `9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b`；复用固定归档 `build/firmware/9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b/` 的完整产物，不重新编译已验收app。

完整镜像从`0x0`首装，会写默认分区表并重置NVS/设置/绑定；**完整首装路径仍未真机验收**。已通过的是同一固定app的保护app-only安装、校验与复位，二者不能混称。保留旧factory0x10000/0x1f0000、FAT0x200000/0x600000及数据时继续使用受保护的app-only升级；不要默认flash、完整首装或整片擦除。

## 图片原样继承，不做本轮图片产物

**原五图继承核验PASS**：原封面、五图和顺序均保留，未上传、删除、重排、替换或重绘。更新后五张服务器900×1200 WebP已逐张重新下载，字节与SHA256全部等于更新前快照。目录保存文案与核验记录，不复制或新做图片；见[图片继承记录](images-reused.json)。

| 顺序 | 原本地参考（只引用） | 原平台修订3928已保存图片参考 |
|---|---|---|
| 1 封面 | [01-cover.png](../v0.3.0-f3-dev3/01-cover.png) | [原图0](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/0?v=1) |
| 2 六工具 | [02-six-tools.png](../v0.3.0-f3-dev3/02-six-tools.png) | [原图1](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/1?v=1) |
| 3 操作 | [03-controls.png](../v0.3.0-f3-dev3/03-controls.png) | [原图2](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/2?v=1) |
| 4 配置 | [04-configuration.png](../v0.3.0-f3-dev3/04-configuration.png) | [原图3](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/3?v=1) |
| 5 配对/范围 | [05-pairing-and-scope.png](../v0.3.0-f3-dev3/05-pairing-and-scope.png) | [原图4](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/4?v=1) |

这些图片引用延续原[submission-status.json](../v0.3.0-f3-dev3/submission-status.json)，本次仍为同一修订3928，图片字节/SHA前后相等；不据这些登录上下文链接推定匿名CDN可用。原本地PNG尺寸/哈希见[原images.json](../v0.3.0-f3-dev3/images.json)，服务器WebP前后核验见[images-reused.json](images-reused.json)，不要混用两者格式/哈希。原封面为玩法示意，说明图是C宿主渲染、非LCD照片；旧版本/按键可能为历史示意，**本次文字与实际界面优先**。六大工具和五组默认快捷键是不同数量。

## 本版变化和验收边界

- 默认五组：截图、Typeless、剪映、微信读书、编辑；抖音移入媒体。旧个人六组仍兼容，不自动删除或覆盖。
- 媒体先选音乐/抖音；音乐原音量/播放/切歌保留，抖音↑/↓/→。所有屏幕/配置页提示按实体从上到下UP、DOWN、OK，OK在底部。
- 30秒息屏从进入/亮屏起计，短键不续时；暗屏短键照发，长OK只亮屏并消费，亮屏长OK保留原工具动作，长UP仍返回。remote_v1独立保存，不迁移/擦除旧设置/配置/绑定；具体公开配置迁移须显式读回/写入。
- **Build PASS / Host tests PASS**：ESP-IDF6.0.2、ESP32-C3、8MiB、无PSRAM；37 Node+90 Python=127，跳过0，2,206步，3项故意变异；固定归档/源码输入/二进制版本已核验。原素材保持不变。
- **Device tests PASS（有范围）**：固定app-only安装/应用校验/复位；授权USB迁移仅移除箭头绑定匹配的旧抖音组，其余groups/cards逐项保持，自动加连续3次读回一致。用户通过媒体选择/实体顺序、自动息屏、暗屏翻页与长OK仅亮屏；本轮耳机/键盘正常。
- **有界设备日志**：两轮共505/505真实ready、约504秒，连接堆最低92,624/最大块77,824字节，31条HID成功/62次notification TX，各类错误与崩溃0。独立暗屏补采全程screen_off=true，完成16条HID/32次TX，anim_frame9冻结，用户复测“都正常”。CI7,500微秒/latency0/supervision2,000毫秒；只读探针不改变BLE策略，TX完成非宿主ACK，约504秒不能冒充1小时长稳。
- **Unverified**：功耗/续航、remote_v1真实冷启动保留、完整App/宿主矩阵、原三槽/回连/深睡/长稳及完整首装。旧间歇蓝牙连接根因未定，本轮正常不代表已修复或全平台通过；历史三秒回连FAIL保留，阅读器/电视未验收。

## 保存与重新提交核验

- **社区当前固件重下PASS**：最终保存页href为 `https://ai-passport.folotoy.cn/api/me/revisions/3928/firmware`；登录创作者上下文下载2,077,152字节，SHA256 `9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b`，与本地固定full及已发布GitHub full逐字节相等，内嵌app亦与b4043d24…211b8ffe精确相等。
- **图片/文字PASS**：五图前后逐张字节/SHA一致，封面/顺序不变；中英介绍、操作、更新记录共六字段在重新提交后与本地文本归一空白一致。
- **状态：重新审核中，非公开。** 沿用project1701/revision3928，未建新项目；状态截图保存在本地build/community-v0.3.1-submitted-status.jpg。
- **匿名当前社区端点未重查**：旧HTTP401是首次投稿历史，本次只证明登录上下文重下，不能称匿名当前CDN可下载。3928是可变修订，旧版2,065,136字节镜像记录不代表当前内容。
- **Device tests边界不变**：本次社区更新没有再刷作者设备，完整首装实机仍NOT RUN；不因重新提交而放行功耗/冷启动/全平台/原回连等未测项。

证据：[新提交状态](submission-status.json)、[新固件下载核验](firmware-validation.json)、[原图继承](images-reused.json)、[GitHub/Pages发布核验](../../validation/publication-v0.3.1-remote-dev2.json)。这些核验不包含凭据、设备身份、绑定、个人配置或原始日志。
