# NABO 工具箱 · v0.3.1-remote-dev2 社区更新文案

本次更新现有项目 **1701**「NABO 工具箱 · 随身蓝牙遥控器」，不是另建玩法。用户明确授权发布新固件并更新原条目，**只更新固件/文字，不动原上传图片**。

本目录保存待执行更新的[中文介绍](COPY_ZH.md)、[中文用法](USAGE_ZH.md)、[英文介绍](COPY_EN.md)、[英文用法](USAGE_EN.md)。文案准备完成不等于Release已发布、页面已更新、社区已提交或公开；实际上传/提交/审核结果由后续核验记录确认。旧项目修订3928的记录保持在[原目录](../v0.3.0-f3-dev3/README.md)，不改写为本版本。

## 本轮链接和固定固件身份

- 本版Release目标：https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.1-remote-dev2 。
- 配置页：https://liutupi.github.io/nabo-toolkit/ 。本轮需核对在线页和本版离线配置包确为五组/实体UP-DOWN-OK版；此前f8b8ad8六组页面和原Release资产不当作新页面已上线的证据。
- 源码：https://github.com/Liutupi/nabo-toolkit 。
- 现有创作者项目：https://ai-passport.folotoy.cn/account/?project=1701 。这是项目工作台，不是已确认的公开玩法页。
- 固定app：`nabo-toolkit-app.bin`，**2,011,616字节**，SHA256 `b4043d24fb20bf4ad68091587486ded70d889e0a42579edca0e44e9e211b8ffe`；版本 `0.3.1-remote-dev2`，app-only写`0x10000`。
- 社区完整首装：`nabo-toolkit-community-full.bin`，**2,077,152字节**，SHA256 `9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b`；复用固定归档 `build/firmware/9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b/` 的完整产物，不重新编译已验收app。

完整镜像从`0x0`首装，会写默认分区表并重置NVS/设置/绑定；**完整首装路径仍未真机验收**。已通过的是同一固定app的保护app-only安装、校验与复位，二者不能混称。保留旧factory0x10000/0x1f0000、FAT0x200000/0x600000及数据时继续使用受保护的app-only升级；不要默认flash、完整首装或整片擦除。

## 图片原样继承，不做本轮图片产物

用户要求保留平台原五张上传图片、封面及顺序。本目录只放文字文件；不复制、编辑、重新渲染、重绘、下载后重传或另做封面。既有平台资产沿用，编辑表单时不点击图片删除/替换/上传。

| 顺序 | 原本地参考（只引用） | 原平台修订3928已保存图片参考 |
|---|---|---|
| 1 封面 | [01-cover.png](../v0.3.0-f3-dev3/01-cover.png) | [原图0](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/0?v=1) |
| 2 六工具 | [02-six-tools.png](../v0.3.0-f3-dev3/02-six-tools.png) | [原图1](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/1?v=1) |
| 3 操作 | [03-controls.png](../v0.3.0-f3-dev3/03-controls.png) | [原图2](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/2?v=1) |
| 4 配置 | [04-configuration.png](../v0.3.0-f3-dev3/04-configuration.png) | [原图3](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/3?v=1) |
| 5 配对/范围 | [05-pairing-and-scope.png](../v0.3.0-f3-dev3/05-pairing-and-scope.png) | [原图4](https://ai-passport.folotoy.cn/api/me/revisions/3928/images/4?v=1) |

这些链接来自原[submission-status.json](../v0.3.0-f3-dev3/submission-status.json)，用于核对原资产继承，不是新修订ID或匿名CDN可用性证明。原图尺寸/哈希仍见[原images.json](../v0.3.0-f3-dev3/images.json)。原封面是玩法示意，说明图为C宿主渲染合成、不是LCD照片；旧版本/按键可能为历史示意，**本次文字与实际界面优先**。六大工具仍是六个，默认快捷键改五组，两者不要混淆。

## 本版变化和验收边界

- 默认五组：截图、Typeless、剪映、微信读书、编辑；抖音移入媒体。旧个人六组仍兼容，不自动删除或覆盖。
- 媒体先选音乐/抖音；音乐原音量/播放/切歌保留，抖音↑/↓/→。所有屏幕/配置页提示按实体从上到下UP、DOWN、OK，OK在底部。
- 30秒息屏从进入/亮屏起计，短键不续时；暗屏短键照发，长OK只亮屏并消费，亮屏长OK保留原工具动作，长UP仍返回。remote_v1独立保存，不迁移/擦除旧设置/配置/绑定；具体公开配置迁移须显式读回/写入。
- **Build PASS / Host tests PASS**：ESP-IDF6.0.2、ESP32-C3、8MiB、无PSRAM；37 Node+90 Python=127，跳过0，2,206步，3项故意变异；固定归档/源码输入/二进制版本已核验。原素材保持不变。
- **Device tests PASS（有范围）**：固定app-only安装/应用校验/复位；授权USB迁移仅移除箭头绑定匹配的旧抖音组，其余groups/cards逐项保持，自动加连续3次读回一致。用户通过媒体选择/实体顺序、自动息屏、暗屏翻页与长OK仅亮屏；本轮耳机/键盘正常。
- **有界设备日志**：两轮共505/505真实ready、约504秒，连接堆最低92,624/最大块77,824字节，31条HID成功/62次notification TX，各类错误与崩溃0。独立暗屏补采全程screen_off=true，完成16条HID/32次TX，anim_frame9冻结，用户复测“都正常”。CI7,500微秒/latency0/supervision2,000毫秒；只读探针不改变BLE策略，TX完成非宿主ACK，约504秒不能冒充1小时长稳。
- **Unverified**：功耗/续航、remote_v1真实冷启动保留、完整App/宿主矩阵、原三槽/回连/深睡/长稳及完整首装。旧间歇蓝牙连接根因未定，本轮正常不代表已修复或全平台通过；历史三秒回连FAIL保留，阅读器/电视未验收。

后续发布核验需分别记录：Release资产公开重新下载、配置页实际版本、社区保存的新修订/固件下载和原五图未改、提交/审核/公开状态。当前目录本身不替代这些结果，也不提交凭据、设备身份、绑定、个人配置或原始日志。
