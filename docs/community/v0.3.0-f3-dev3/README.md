# NABO 工具箱 · 社区投稿记录

版本 `v0.3.0-f3-dev3`，项目 **1701**，修订 **3928**。标题为「NABO 工具箱 · 随身蓝牙遥控器」，分类「效率与工具」。

**已提交，当前审核中；尚未确认公开上架。** `submission-status.json` 的 `publicly_published` 保持 `false`，`public_url` 保持 `null`。创作者可在[项目工作台](https://ai-passport.folotoy.cn/account/?project=1701)查看；此地址不是公开玩法页。

## 已保存的内容

- 五张图片，顺序见下表；社区保存版本均为900×1200，第一张是封面。
- [中文介绍](COPY_ZH.md)及[中文操作说明](USAGE_ZH.md)，包含六大工具、全部按键、蓝牙配对、网页配置和首装注意事项。
- [英文介绍](COPY_EN.md)及[英文操作说明](USAGE_EN.md)。
- 配置页：https://liutupi.github.io/nabo-toolkit/ 。
- 固件、离线配置包和安装说明：https://github.com/Liutupi/nabo-toolkit/releases/tag/v0.3.0-f3-dev3 。
- 公开源码：https://github.com/Liutupi/nabo-toolkit 。

| 顺序 | 文件 | 本地尺寸 | 内容 |
|---|---|---|---|
| 1 | `01-cover.png` | 1086×1448 | ImageGen宣传封面，基于已有NABO参考；标明玩法示意图和公开测试版 |
| 2 | `02-six-tools.png` | 900×1200 | 快捷键、PPT、会议、媒体、拍照、名片的实际C渲染器宿主预览 |
| 3 | `03-controls.png` | 900×1200 | 三键操作与各工具按键 |
| 4 | `04-configuration.png` | 900×1200 | 配置网址、连接/读回/编辑/写入与核对流程 |
| 5 | `05-pairing-and-scope.png` | 900×1200 | 三份绑定、单连接、配对步骤和测试范围 |

封面源文件是 `game-art/toolkit/art/community/v0.3.0-f3-dev3/01-cover-v1.png`，与本目录`01-cover.png`逐字节一致。生成参考与校验见[封面记录](cover-generation.json)和[提示词](cover-prompt.txt)。说明图是原界面的宿主渲染合成，不是真机照片；演示设备/连接状态不作为实机验收证据。`images.json`记录各本地文件尺寸与SHA256。原364份素材保持不变；当前素材库存368文件/93,040,985字节，新增的第四份素材是本次社区封面，其余三份新增素材为此前授权的开机语音来源/派生/记录。

## 两种安装文件的边界

社区表单要求完整`.bin`，一键安装从`0x0`写入。本轮用户单独明确授权发布现成完整镜像并提交审核：

- 完整首装镜像：`nabo-toolkit-community-full.bin`，**2,065,136字节**，SHA256 `9fa968de2a4837d130188bb9541ec55a67a3f1bd936b01eeeb4b81ea5047ad1c`。
- 内含同一已验收app：1,999,600字节，位于`0x10000`，SHA256 `d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`。没有重新编译或替换app。
- 完整首装会写入默认分区表，并重置NVS、PHY、原设置和蓝牙绑定。镜像的NVS/PHY区域是构建生成的`0xff`填充，不含设备读回或凭据。
- **完整首装路径尚未真机验收。** 社区文案已说明这一点。本轮没有刷写作者当前工牌。
- 要保留已有分区/设置/绑定/素材，使用Release里的app-only保护升级方式，只写`0x10000`，不要使用社区一键完整安装。详见[版本安装说明](../../RELEASE_v0.3.0-f3-dev3.md)。

## 核验结果

- **Build：PASS**。复用ESP-IDF6.0.2/C3/8MiB/无PSRAM的固定构建归档，布局和产物哈希重新验证；完整镜像内app与已验收app逐字节相等。
- **Host tests：既有100项/1,710步PASS**。这是同一app的既有宿主验收；本次投稿没有重新编译或重复宣称设备测试。
- **Device tests：部分PASS**。最终app此前通过用户声音、完整欢迎与工具动画验收。本轮只做发布核验，没有刷设备；完整首装的设备验收未做。
- **Unverified：** 社区公开上架、匿名当前修订下载、完整首装实机路径及`docs/validation/f3.json`列出的其余兼容/回连等设备项目。

已从当前保存页读取实际固件链接 `https://ai-passport.folotoy.cn/api/me/revisions/3928/firmware`，在登录浏览器上下文下载后，字节和SHA256与本地固定完整镜像、GitHub公开下载均相等。对同一修订链接的匿名请求返回**HTTP401**，不宣称匿名社区固件可下载，也不将登录下载等同于匿名CDN验证。详见[固件核验](firmware-validation.json)。

GitHub Release现有八个资产已全部匿名重新下载核对，记录见[GitHub核验](github-redownload-verification.json)。社区的审核状态、公开URL和权限需要分别确认；「审核中」不等于「已发布」。

后续用户要求删除浏览器/PS/窗口默认组、加入微信读书和抖音，属于下一版本修改，**不包含在本修订3928的描述或固件中**。
