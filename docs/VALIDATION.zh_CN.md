<p align="right"><strong>简体中文</strong> · <a href="VALIDATION.md">English</a></p>

# 验证记录 — 2026-10-28

**最新dev4：Build/Host PASS（213项：44 Node+144 Python+25声学探针；2,722步、3变异、0跳过），本轮语音/无损整理/受控重启保留限定PASS，实际名片配置改动写入/读回/重启留存及手机扫码PASS。** 固定app2,030,864B/SHA256 `d748e54395bff10eaa85530d4287198607fc3fcd17f2d1da8250b272b15d1829`，旧factory余752B，归档9f6ac2a6…729dd78独立verify、130份输入匹配。显式compact返回0，21样本/638帧全部系数/counts/next保留，七词均3条；真实available251。早先生产JS+USB同内容写/读可能SDK skip的边界保留为历史；后续真实payload变化已通过，不再称changedcfg物理Flash未测。SDK4,016B opaque blob写入仍不等于合法最大cfg schema测试。

个人名片只把 `cards[0].qr` 改为 [土皮作者页](https://ai-passport.folotoy.cn/creators/?id=14101)，其它全部groups/cards字段canonical一致。JSON1,613→1,632B/NVS record1,629→1,648B，真实USB保存读回相等，受控reset后生产客户端再次读回expected相等；用户手机确认作品列表正确。公开作者页匿名HTTP200、Adventure1662条目关联Liutupi/nabo-adventure且authorProfile14101，creator API10个公开作品同作者、无下一页。私人配置不发布，默认名片/app不改；详见HANDOFF34。

最终用户确认dev4语音输入/读书正确、无卡住重启；另外未知意图查询不计accuracy。准确初始观测目录162339（69.19秒），最终162551（127.09秒、253 tk/254 voice），两窗口分开、panic/reset0；最终global min64,160B、heap67,444/largest55,296、UI/worker栈余5,560/2,748、最大特征帧6,071us、完整性true，sent查询阶段1→1，前一条普通HID另计。耳机间歇问题当前PC USB也恢复正常，用户要求“先不理”，已停止BLE排查，根因OPEN、不改BLE参数/驱动、不称修复。

用户已明确授权发布 `v0.3.2-voice-dev4` **公开实验测试版**，复用同一已验收app不重编译；发布准备中，尚不声称GitHub已上线或社区已提交。完整首装复用同一固定9f6镜像2,096,400B；其bootloader与上一公开版37字节不同，来自本次固定归档，不称旧bootloader同字节复用；完整0x0首装未真机验收。社区本轮受浏览器能力/策略限制，仅准备bundle，未更新/未提交；原五图不改。合法最大配置schema、全七词/多用户噪声矩阵、长稳、冷断电/故障、极端容量GC、功耗与旧平台门槛仍未测。见[dev4详细记录](validation/offline-voice-v0.3.2-dev4.json)和HANDOFF33–34；下方dev1–dev3失败/禁止发布字样为各自镜像的历史检查点，不替代本次新授权。

本人离线语音dev1（HANDOFF28–29）：**Build PASS；Host tests PASS：192项（44 Node+124 Python+24声学探针），2,666步、3变异、0跳过；Device tests FAIL：用户连续录入时重启/卡死，根因未定。** 固定app2,029,088B/SHA256 `acbfd4f7e0f1aa41b0acad5af3f044ddfec623046a82558c561c8631a89d3ffb`，旧factory余2,528B；130份输入匹配/独立归档verify、授权app-only刷入/verify/复位和复位前保护区检查PASS，未刷超界镜像。原7份字体C/动画保持。

保留早期正向证据：启动menu/蓝牙ready/voice available；读书3条保存读回及一次独立查询导航到macro，HID sent前后0。早期运行heap最低69,636/largest53,248、全局最低63,152B、单帧最高11,949us、保存/读回错误0；不能当连续录入稳定性PASS。dev1失败现场当时模板计数为 **[3,3,3,3,1,0]**，后续录入见dev2段。匹配固定ELF `3a9c1604f477f002c557a2a495bac9bc75cc668a240bbb2e92feaf8e9d072d3b` 的Store access fault为PC `0x42019de0` / RA `0x42019dde`，另见ret循环 `0x42019dd4`；观察UI bridge返回地址比预期正常返回多 `0x1000`，原因未定，不预先归因为matcher或低内存。私有完整app回读字节/SHA与固定app相等，排除该次读回时的app镜像字节损坏；不排除其他运行期问题。见[dev1失败记录](validation/offline-voice-v0.3.2.json)。

**dev2：Build PASS / Host tests PASS：197项（44 Node+129 Python+24声学探针）、2,722步对拍、3变异、0跳过；Device tests FAIL，完整验收未过。** 固定app2,031,152B/SHA256 `c55e1307e367de2ca9b09fcea795efe93b91fc5499427a0559cc848d292442dc`，旧factory余464B，归档43756fdf…edd77d独立verify及130份source输入匹配。授权app-only刷写/verify/复位、fresh USB/芯片/安全/实际8MiB/旧表/原app核对和复位前表/NVS/PHY/素材首扇区hash均PASS；整素材未读回。原13条模板启动保留。二进制字节counts检查不是dev1根因或永久修复结论。

30条open/cancel命令及后续220.28秒/15次录入有界窗口panic/reset均0，只说明本轮未复现原重启。拍照2条/截图3条保存并补一次过短后，旧六词均3条；第七词example1四次4357（NOT_ENOUGH_SPACE）/读回-1，计数降0，用户确认“语音输入”录入失败。冷重启旧六词仍[3,3,3,3,3,3,0]、invalid_mask0；NVS used546/free210/available84/total756。SDK6.0.2源码审计发现可能的chunkStart错误cleanup/读缺chunk清旧blob路径，未设备逐指令证明。

status堆最低67,276/largest51,200，voice堆最低67,456；global minimum60,936B低于60KiB门槛504B，资源门槛FAIL。UI栈余6,180/worker2,392B，堆完整性均true；最大特征帧22,577us超过20ms。用户读书/音乐查询仍未识别或歧义：8次查询含4歧义（5/5、4/6、3/5、4/5）、3过短（14/11/12帧）、1无语音，接受0，无panic。详见[dev2记录](validation/offline-voice-v0.3.2-dev2.json)和HANDOFF30；原始日志/个人模板留private。

**dev3：Build PASS / Host tests PASS：207项（44 Node+138 Python+25声学探针）、2,722步、3变异、0跳过；Device PARTIAL：语音PASS、PC USB共存FAIL/电池供电当前PASS，配置容量BLOCKED。** 固定app2,031,472B/SHA256 `2101d1d65355640b07e116701c401c5e53d281fa991d2cb76ef6bcc7ffe6dace`，旧factory仅余144B，写[0x10000,0x1fff70)、擦除截止0x200000 exclusive。归档2e4a50f8…e9e0de20独立verify及130份source输入匹配；最终host/build/reconfigure分别记录voice-dev3-host.log、voice-dev3-build.log、voice-dev3-reconfigure.log。counts仍lbu/sb、offset28/align4，仅为生成代码证据；3个存储/控制源-Os，DSP/动画/UI O2不变，7份字体C/素材仍与HEAD相同。

候选使用无损compact/每词新A-B键/写前预检/验证后只退休同词旧key，不批迁旧六词；base16,864B先读完NVS，再分配enrollment576B或matcher3,104B，错开读临时缓冲、分别wipe/free，资源门槛不降。实际IDF6.0.2 backend在独立24KiB NOR副本（非实物Flash）做24矩阵：19项4357/unknown=false安全拒绝，整副本拒绝前后字节不变，旧六词/非voice一致，原私有镜像未改。47帧sum63/64与48帧sum63各30轮成功；更宽数据可三例齐但第四次覆盖拒绝，8bit极端仅两例，不能宣称容量无限或真机断电已验收。

query最短15→8、enroll仍15，margin4→2/绝对距离18/声学系数不变，ties/gap1仍拒绝；私有录入库18留一第一名全对、margin2接受17/18，仍只是模型诊断，不是独立准确率。安装前fresh USB及同连接C3/8MiB/security/旧表/当前c55e固定app均核对；仅刷2101固定app并verify/复位，复位前表/NVS/PHY/素材首扇区hash一致，整素材未读回。

用户确认旧读书/音乐正确跳转且未重启（USB暂断，无对应UART job）。USB重接fresh identity后，“语音输入”录入46/45/46帧三条，写/读错误0、invalid_mask0；独立查询41帧、winner6/best3/runner5，进入Typeless由用户确认，sent0→0。授权只读NVS容量后受控reset，七词各3条且invalid_mask0；再query40帧以同样best3/runner5进入Typeless，用户确认。负例“你好”16帧/best5/runner6/decision7 ambiguous，未跳页且用户确认；后续普通HID不归给识别。

三段观测33.11秒（USB断开终止）、113.05秒（三录一识别）、326.0秒（重启后识别/负例）各panic/reset markers0，受控reset在窗口间，不合称连续472秒。global heap最低64,140>61,440B；status/voice67,424、largest55,296>30,720，UI栈余5,556/worker2,508B，完整性均true、最大特征帧13,702us，BLE ready、audio error/HID failed0。本轮资源门槛PASS不等于所有负载或长稳。

只读对比47个原NVS逻辑记录：旧六词v1、nabo_tk配置/设置/slots逻辑字节保持，仅新增vc6一有效journal（1,108B/37entries）；used583/free173/available47/total756，物理Written583/Empty133/Erased40。另有一份PHY校准blob正常启动后变化，整个NVS并非全部逻辑值相同；保护hash仅刷后复位前成立。这些保留结果不代表配置更新可保存，后续SDK副本已复现容量阻断。

**PC USB场景耳机共存FAIL（用户明确确认）**：PC USB连着工牌并连接Windows时耳机断续，主菜单静置15秒仍断续；只关工牌、不动PC蓝牙后恢复。快照voice inactive/BLE ready、CI7500us/latency0/STO2000ms，无新增HID或错误；这些正常计数不能覆盖耳机失败。适配器BARROT Bluetooth5.4，驱动17.55.6.566（2024-07-26）。

**USB隔离补测：电池供电当前PASS（用户确认）**。同位置拔PC USB、工牌电池供电并继续蓝牙连接Windows时耳机正常；原PC仅该USB口可用，换口暂不可行。只读WinRT probe仍Connected=true、CI7.5ms/latency0/STO2s，未请求参数、未建GATT会话、未改驱动；不能把7.5ms单独定因，不改BLE策略。外部充电器/充电宝对照待回复，USB供电/数据/位置/驱动与无线因素仍未判。

**配置容量BLOCKED（非物理工牌写入）**：实际SDK6.0.2在used583/available47私有NOR副本，原样1,629B cfg返回0、NOR写0，仅同值skip；另一个副本等长改一位返回4357，431次NOR writes/2 sector GC，新候选未保存。reinit后旧cfg和其余41个逻辑记录保持，物理副本因GC改变。真实cfg未改；这是已复现的配置存储发布阻断，不是“尚未测试”，也不是配置更新PASS。

**历史dev3检查点：当时未最终验收、禁止发布。Unverified（当时）**：剩余USB供电/数据/位置/驱动与无线因素、配置容量修复后的保存验收、原故障根因/长稳、更多用户/背景噪声/完整七词矩阵、冷断电/掉电、极端位宽/大配置NVS与GC、真实Flash故障、功耗及全部旧门槛。见[dev3记录](validation/offline-voice-v0.3.2-dev3.json)和HANDOFF31–32；root_cause_fixed=false。当时设备为电池供电/PC USB拔除/蓝牙连接，暂停设备写入，compact_legacy尚未接入口，安装2101。后续dev4整理/验收和新发布授权见本页顶部与HANDOFF33；原图片/字体/素材不变。

v0.3.1 GitHub/Pages发布核验PASS：新Release8资产匿名重下、ZIP37成员、公开配置页11文件均字节/SHA一致。**原社区项目1701/可变修订3928已更新为v0.3.1-remote-dev2并重新提交审核，当前“审核中”，尚未公开上架。** 原五图逐张重下字节/SHA与更新前一致；社区当前完整固件重下2,077,152字节、SHA256 `9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b`，与已发布GitHub full相等。见[发布核验](validation/publication-v0.3.1-remote-dev2.json)、[社区更新](community/v0.3.1-remote-dev2/README.md)和HANDOFF27。

媒体/息屏0.3.1-remote-dev2：**Build PASS；Host tests PASS（127：37 Node+90 Python，2206步，3变异，0跳过）；Device tests 本轮新增行为PASS：固定app-only安装/保护区/五组配置迁移、媒体实体顺序、持续按键后息屏、暗屏HID和长OK只亮屏、本轮耳机键盘共存正常。** 两轮505/505 ready，连接堆最低92,624/最大块77,824；暗屏独立16条HID/32次TX、动画帧冻结，相关错误0。Unverified：实测功耗/冷启动开关保留/完整App与平台矩阵/历史间歇连接原因/原回连三槽深睡长稳及完整首装；不是全F0/F1门槛放行。见[记录](validation/remote-control-v0.3.1.json)和HANDOFF26。GitHub/Pages与社区保存文件核验已通过；社区公开状态仍待审核。

快捷键改版：Build PASS（0.3.1-shortcuts-dev1候选，未刷/未发布）；Host tests PASS（102：29 Node+73 Python，1710步）；Device tests：旧dev3真实USB配置保存+3读回通过，截图/Esc及读书/抖音当前端由用户确认可用。候选实机、手机/电脑逐项矩阵和新配置拔电保留仍Unverified。见[新分组记录](validation/shortcuts-v0.3.1.json)。

新版配置交付PASS：Pages提交f8b8ad8部署成功，11个可访问文件匿名HTTP200/字节/SHA一致；公开浏览器预设切换/名片保留/未连接禁写通过。Release另增仅配置更新包及独立manifest/校验文件，11资产匿名重下通过，原8资产不变；未发布新候选固件。见[交付核验](validation/shortcuts-publication-20261028.json)。

## 社区更新核验 — v0.3.1-remote-dev2（2026-10-28）

同一项目1701/修订3928在用户手动撤回后原位更新，已重新提交审核，当前**审核中、非公开**。六个中英介绍/操作/更新记录字段保存核对一致，原五图、封面和顺序保持，五张服务器WebP逐张重下的字节/SHA均与更新前一致。

- Build：PASS，固定完整镜像2,077,152字节/SHA256 `9bcc39298ddaced09803052de27b6671d502e5d72cd5e249e55140f48abe548b`；登录创作者上下文从当前保存href重下，与固定产物/已发布GitHub full逐字节相等，内嵌app相等。
- Host tests：固定app既有127项/2,206步/3变异PASS，发布核验不冒充重新执行设备测试。
- Device tests：第26节固定app-only安装/配置迁移/本轮媒体与息屏部分PASS；本次社区更新没有再刷作者设备，完整0x0首装仍NOT RUN。
- Unverified：社区公开上架、当前匿名端点（本轮未重查）、完整首装实机，以及功耗/冷启动开关保留/全部App平台/历史蓝牙间歇原因/原回连三槽深睡长稳。

当前保存href：`https://ai-passport.folotoy.cn/api/me/revisions/3928/firmware`；工作台：https://ai-passport.folotoy.cn/account/?project=1701 。只证明登录上下文重下，不称匿名CDN可下载。见[固件核验](community/v0.3.1-remote-dev2/firmware-validation.json)、[图片继承](community/v0.3.1-remote-dev2/images-reused.json)和[提交状态](community/v0.3.1-remote-dev2/submission-status.json)。3928是可变修订，当前href已替换为新二进制，以下旧记录保留为历史快照。

## 历史首次投稿核验 — v0.3.0-f3-dev3（2026-10-28）

首次投稿当时AI Passport项目1701/修订3928已提交、**审核中，尚未确认公开上架**；此段为旧版本历史快照，当前同修订已更新，见第27节与上文。五张图、六工具中英文玩法/按键/配对说明、[配置页](https://liutupi.github.io/nabo-toolkit/)和安装边界已保存。完整首装镜像经用户单独授权；作者当前工牌未刷写。

- Build：PASS，复用并校验固定完整镜像2,065,136字节，SHA256 `9fa968de2a4837d130188bb9541ec55a67a3f1bd936b01eeeb4b81ea5047ad1c`；内嵌app与已验收dev3相等。
- Host tests：同一app既有100项/1,710步PASS；本次发布核验不代表重新执行完整首装验收。
- Device tests：既有app声音/完整欢迎/动画部分PASS；本轮未刷设备，完整首装NOT RUN。
- Unverified：社区公开上架、匿名修订固件下载（首次检查时HTTP401，非本轮新请求）、完整首装实机路径及剩余设备兼容/回连项目。首装0x0会改分区表并重置NVS/绑定，保留数据使用app-only升级。

首次投稿时从保存页实际固件href登录浏览器下载，与当时本地/GitHub逐字节核对通过；GitHub8个资产匿名重下通过。素材库存368文件/93,040,985字节，原364不变。详细证据见[社区投稿记录](community/v0.3.0-f3-dev3/README.md)。后续微信读书/抖音改动不包含在该首次投稿快照；3928当前内容已在第27节原位更新，旧下载记录不代表当前二进制。

首次GitHub/Pages发布PASS（第23节阶段记录）：仓库PUBLIC，测试版Release及NABO配置页已上线；5个下载文件匿名下载、37个ZIP成员和网页11文件校验通过。浏览器名片/Wi-Fi编辑、保存/重载及NABO形象显示通过；未开串口，真实权限/USB传输仍未验收。详情见[发布核验](validation/publication-v0.3.0-f3-dev3.json)。

- Build: PASS（F3 dev3，ESP-IDF6.0.2/C3/8MiB/无PSRAM；固定app已安装）
- Host tests: PASS（100：27 Node+73 Python；1,710步完整JS–C对拍；跳过0）
- Device tests: 部分PASS：用户确认完整欢迎、各工具服装/动画、开机音和无爆破按键音；240次连接采样堆最低92,696/最大块77,824，音频错误0、崩溃0。
- Unverified: 最终镜像重复USB配置/断电保留、实体开机跳过、浏览器权限、全部宿主与三槽/长稳/睡眠。历史三秒FAIL保留。

精确app SHA256：`d2032e7b95d6e45aa0cc7e8fb6a9acdfb1628e3ea09578b7eafb061f866b4711`；1,999,600字节。发布只用此已验收app。详情见HANDOFF22–23及[机器记录](validation/f3.json)。F2/dev1结果按镜像分别保留，不作为dev3重测。

## F2 历史概览（2026-10-27）

- Build: PASS（F2 dev2，ESP-IDF6.0.2；已app-only安装）
- Host tests: PASS（87：27 Node +60 Python；1,710步含自定义配置完整JS–C对拍）
- Device tests: 部分PASS：真实USB保存/读回、异常拒绝、两轮重启保留、20次读回；Windows重新配对/粘贴/音量/连接内存通过，自定义文字/名片/扫码/断电保留通过。
- Unverified: 浏览器USB权限/传输中拔线/写入中断电及剩余F1/F3；历史三秒FAIL保留。

此前F2结果见本页末尾、HANDOFF 第21节及 `validation/f2.json`。以下为按时间保留的历史记录，历史“F1未开始”等判断已被最新开发记录接续。

已使用项目 FIRMWARE_PLAN 指定的 **ESP-IDF 6.0.2**，从受版本管理默认配置生成隔离配置，运行完整 `./tools/validate.sh` 通过。含 18 项 Node、7 项 C 探路/按键、8 项精灵、7 项刷写保护测试、JS 重录一致性、差异空白检查、构建/合并/分区验证及精确归档校验。未套用通用 skill 的 5.5.3 默认版本。

| 原 Mac 构建产物（已刷入） | 字节 | SHA256 |
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
| 配对 | Mac、Windows、iPhone、安卓；需要时能输入六位码 | Mac/Windows/iPhone PASS；安卓待测，新鲜 iPhone 配对码交互未独立观察 |
| 重启回连 | 上次设备三秒内自动认证/订阅就绪 | Windows USB 复位 3/3 自动回连；全程主机上界 2.219/3.125/2.812 秒，严格三秒门槛未证实 |
| 连接中内存 | 空闲堆 ≥60 KiB，最大块 ≥30 KiB | Mac 195,604、Windows 195,848、iPhone 196,244；最大块均 114,688 字节，PASS |
| HID | Mac Cmd+V / Windows Ctrl+V、音量加、不粘修饰键 | Mac 粘贴/音量、Windows 粘贴/音量、iPhone 音量由用户确认 PASS；安卓待测 |

用户已确认正确设备开机并连接。对 `/dev/cu.usbmodem212401` 只读识别，确认 ESP32-C3、8 MiB，无安全启动/Flash 加密限制；现有 `nabo-adventure 0.1.0` / IDF 6.0.2。首次严格布局检查拒绝写入；随后实测旧表为 NVS `0x9000/0x6000`、PHY `0xf000/0x1000`、factory `0x10000/0x1f0000`、FAT assets `0x200000/0x600000`，MD5 正确，与构建计划表不同。F0 不访问 assets/files，643,392 字节 app 可放入较小的旧 factory。安装器仅显式接受计划表或这一实测旧表，再按实际 factory 大小检查候选和擦除扇区边界；新增旧布局/超长候选两项测试。不能将构建分区表刷到这台设备。MAC、原始检查输出仅存忽略的 `private/device/`，未要求或读取全 Flash 备份。

用户已在当前聊天明确授权“允许，刷入 F0 并开始测试”。已先重验固定归档，核对同一串口和私有设备 MAC，保留实测旧表完成 app-only 刷写：镜像 `[0x10000, 0xad140)`，擦除扇区 `[0x10000, 0xae000)`，写后 app 校验 PASS。没有写合并镜像、分区表、NVS 或素材区，没有整片擦除。随后 20 秒串口观察收到 F0 菜单状态，无崩溃标记。未连接时空闲堆 196,668 字节、最大块 114,688 字节、最低堆 189,908 字节；**不是连接中堆验收**。用户已确认 Mac 配对、OK 粘贴与上键音量正常；串口收到 5 次成功、0 次失败。Mac 连接中堆最低观察值 195,604 字节，最大块 114,688 字节，超过门槛。串口打开会触发 USB_UART_CHIP_RESET；已观察一次实际重启自动回连，广播起算 701 ms，重复开机全程计时尚未完成。原引导程序为 IDF 5.5.3，未覆盖。用户有 iPhone，因下班交接，本轮未继续测；Windows/iPhone/安卓留待接续。屏幕完整效果尚待用户验收。F0 全部门槛未过前不开始 F1。

原型：通过实际浏览器控件操作十个页面，检查配对码、Typeless 右修饰键、PPT 计时、相机倒数及菜单/连接/设置/名片；最后刷新之后控制台错误/警告为零。截图位于 `docs/images/prototype/`；`overview.png` 是实际浏览器截图裁切拼接，不是真机证据；浏览器不向设备真实发 HID。

JS 基准共 1,559 步，覆盖 10 页、4 OS、6 键、5 连接事件；三项故意修改的时间/修饰键/连拍节奏会被测试抓到。C 按键与 JS 对比 4,000 次事件，另测 uint32 回绕；完整 C 应用状态对拍待 F1。

视频：7 条 720×720/24 fps 原片，535 帧全自动解码。人工检查每 0.25 秒接触表、首尾和头部对比，说明与源哈希在 `art/qa/batch1/review.json`。欢迎 4,042 ms，从 1.4 秒播到约 5.44 秒；用户已选 5.5 秒进菜单、任意键跳过。8 个精灵包共 405,362 字节；解码与索引目标逐像素一致，RGBA 量化损失另记；LCD 可读性/帧率、C 解码器待 F3。语音、界面美术和 Grok 第 2 批动作仍待后续。

用户已要求将当前源码和全部素材提交推送至私有仓库 main；交接见 `WINDOWS_CONTINUE.zh_CN.md`，具体提交以 git log 为准。未创建发布版本。

## Windows 接续 — 2026-10-27

仓库基线为 `5fb23a0`，本地 `main` 初始干净。素材校验 **364 文件 / 90,980,640 字节 PASS**，没有重生图或视频。现有游戏 skill 与私有正本内容一致（仅换行形式不同）；五个 Passport skills 已安装并阅读相关阶段指引。

**Host tests PASS**：Windows 的现有 Git Bash 静态门禁实际运行通过，18 项 Node + 26 项 Python = 44 项；1,559 步 JS 重录逐字节一致，`git diff --check` 通过。原 40 项保留，新增 4 项状态采集器检查：只输出允许的字段、坏数据拒绝、模拟/未连接采样不计连接中内存、广播计时不冒充全程开机。Windows 下清理临时目录前释放 ctypes 库，避免 WinError 5；完整 JS–C 应用状态对拍仍未实现。

**Build PASS**：本机 `C:\Espressif\esp-idf-v6.0.2` 激活后实际报告 v6.0.2；ESP32-C3、8 MiB、无 PSRAM，依赖锁未更新。原生 Windows 构建、合并、分区 MD5/布局/镜像偏移验证、无 Wi-Fi 初始化符号检查、精确归档及独立 `verify` 通过。归档脚本显式使用 UTF-8，避免系统 GBK 解码 SDK 配置失败；源清单使用可移植的 `/`。

| 本轮 Windows 构建产物（未刷入） | 字节 | SHA256 |
|---|---:|---|
| F0 app | 643,392 | `dbefb160c7cae4b9eb5513e28034395b94d419035c18ee4357bb4781b96eb1b4` |
| 合并镜像 | 708,928 | `dec04d19d09f5ac57a86433d30572a6841a96922cd50640f595e67c8e4f05df9` |
| ELF | 8,537,344 | `352874748b796795215eb1e49d250ad9323b10e2912cd8bb9160c5d74fa25af6` |
| MAP | 5,810,140 | `8592ded5becbe110aa75f4a605332fe1426c06f2659f8d4f2e61c554c42ea924` |

本机精确归档在 `build/firmware/dec04d19d09f5ac57a86433d30572a6841a96922cd50640f595e67c8e4f05df9/`。上方 Mac 归档路径是历史记录，未随 Git 迁入 Windows；不能将这份新构建冒充已验收的 Mac 二进制。设备仍使用交接时 app `ea6789e…5074c`，本轮未读回重算其 SHA256、未刷写。构建产物的默认分区表与设备实测旧表不同，仍禁止直接刷合并镜像或默认 `idf.py flash`。

**Device tests 部分完成**：Windows 重新枚举找到 `COM12`（Espressif USB），运行标记确认 `NABO Toolkit F0 / ai-passport-nabo / no Wi-Fi`。状态 `menu / windows / ready=false / test=false`，堆 196,516、最大块 114,688、最低堆 189,756 字节，0 次发送、0 次失败。仅证明 F0 状态可读及未连接内存；不能据此宣称 Windows 配对、HID 或连接中内存通过。日志仅保存在忽略的 `private/device/`；本轮没有设备写入，既有分区、NVS、绑定和素材未被刷写工具更改。

300 秒观察已结束并释放串口：142 次状态，0 次真实连接就绪采样。没有用户完成操作的证据，配对结果保持未验证，不记为失败或通过。

**Unverified**：Windows 配对/Ctrl+V/音量；iPhone、安卓；各平台连接中堆；至少三轮完整开机到认证及双报告订阅就绪 ≤3 秒；完整显示/实体按键验收。用户的 Windows 配对/操作反馈仍待取得；之后再安排 iPhone。原 Mac 通过项沿用历史证据，未作为本次复测。F0 未完成，未进入 F1、未提交推送或发布。

### 后续配对故障观察

用户确认已连接开机，并报告 **Windows 看得到目标，但配对时报错**。Windows 配对：FAIL（用户报告）；HID 和连接中内存仍 NOT RUN。独立 BLE 扫描 PASS（仅发现）：1 个「NABO 工具箱」，HID 服务 0x1812 存在，RSSI −29 dBm。现有 F0 串口命令开放一次 60 秒配对并观察 150 秒，未捕获成功就绪或可定位的握手失败码；串口已释放。Windows 设置没有可读取的目标窗口，精确报错文字和工牌是否出现六位配对码仍待用户提供。原因未定，不将旧系统警告当成此次配对失败的原因。未改固件、刷写、清空绑定或降低配对安全要求；Build/Host tests 无变更，F0 未通过。

用户补充的精确现象：**“请尝试重新连接设备”，工牌未出现六位码**。随后在新配对窗口内，用刚扫描到的唯一目标匹配 Windows AEP 端点，状态为未配对且可配对；系统 `PairAsync` 返回 `FAILED / 19`，未观察到工牌就绪。[微软结果定义](https://learn.microsoft.com/en-us/uwp/api/windows.devices.enumeration.devicepairingresultstatus)将 19 定义为通用失败，因此不能据此归因认证、驱动或设备固件。Windows 已存的旧 NABO 小智条目经私有地址比对确认是另一目标，未删除。设置主窗口后来可读，Shell 的添加设备对话框未能通过主窗口绑定控制；没有自动处理配对码/认证。下一步已安排 iPhone 配对/音量/连接中内存，Windows 失败仍保留，F0 不放行。

### iPhone 已连接；F0 diag1 仅准备，未安装

用户先报告 iPhone 无法发现，随后报告已连接。独立扫描曾捕获可连接无定向、通用可发现 flags 0x06、HID 0x1812、键盘外观 0x03c1。原版 F0 串口随后报告 **ready=true / test=false**，达到认证及双报告订阅就绪条件。iPhone 配对/连接 PASS（用户确认 + 串口）；连接中内存 PASS：空闲堆 196,244、最大块 114,688 字节。实体上键音量待用户确认，不能用 ready 代替功能效果。`ready_ms=41128` 含本次用户配对等待，不能当作自动回连或全程开机数据；新鲜六位码交互未独立观察，多轮重启计时未做。

只读复核再次确认 ESP32-C3、8 MiB 和旧分区；读取的 app 643,392 字节 SHA256 与 `ea6789e…5074c` 完全一致，已私有保存供回退。只读取表和 app，没有读取 NVS、擦除或写入 Flash；分区表 SHA256 `7428911f9c364578c3d57ff0cc315b25442333cad48b1609577e7840124373c2`。

为定位 Windows 准备了 F0 diag1，仅增加不含地址/密钥/配对码的连接、安全、订阅、广播数值日志及启动标记；安全策略、键位和 NVS 存储逻辑无变更。**Build PASS、Host tests PASS（44 项 + 1,559 步重录）**；构建/合并/布局/无 Wi-Fi 初始化符号/归档独立 verify 和候选 inspect 通过。app 644,672 字节、SHA256 `b0c39fb71ca8eb2de0ad0b1f26fd0b7e164f1d4c54cfee92c8738e47c69f7d30`，合并镜像 710,208 字节、SHA256 `d021c36cb54504b91311b16350d5d00464bd85392f1041fb25bc97fcfed6f295`，同哈希归档在 `build/firmware/`。这份候选 **未刷入、Device tests NOT RUN**；若需安装，仅 app `0x10000–0xad640`，擦除扇区截至 `0xae000`，仍必须另取本次固定产物授权并现场重验同一设备。合并镜像不用于本设备升级。当前优先继续原 F0 的 iPhone 验收，Windows/安卓及多轮计时仍待解决，F1 不开始。

用户随后明确确认 **SECURED / ready 且音量增加**：iPhone 上键音量 PASS。90 秒采集共 45 次状态、36 次真实连接就绪采样，连接中堆最低 196,244、最大块最低 114,688 字节。音量按键发生在该采集结束后，因此效果以用户确认记录，未将此前 0 发送改成虚构的成功次数。Windows 下一次复测前先断开 iPhone 的这个设备并保留配对；多轮完整重启/自动回连仍未验证。

### 最新：Windows 通过，三轮自动回连成功但严格三秒未证实

用户在断开 iPhone 该连接并保留绑定后确认 **Windows 配对、粘贴和音量均正常**。串口同一观察期出现 `ready=true / test=false`；150 秒共 73 次状态、30 次就绪采样，连接中堆最低 195,848、最大块最低 114,688 字节。计数由 7 增至 20（13 次完成），失败 0，最终 OS=windows。Windows 配对/Ctrl+V/音量/连接中内存 PASS；使用的仍是读回哈希已确认的原 F0，早先失败具体原因未证实。

三轮 USB 硬件复位均自动连回同一 Windows 主机，每轮新启动标记和清零发送计数证实实际重启，无需重新配对。以主机单调时钟从复位请求发出前到接收新 `ready=true` 状态计时，含复位保持/USB/串口接收开销：

| 轮次 | 复位请求到就绪观测上界 | 广播到就绪 | 堆 / 最大块 | 观测上界 ≤3 秒 |
|---|---:|---:|---:|---|
| 1 | 2,219.0 ms | 1,690 ms | 196,016 / 114,688 字节 | 是 |
| 2 | 3,125.0 ms | 2,608 ms | 196,016 / 114,688 字节 | 否 |
| 3 | 2,812.0 ms | 2,269 ms | 196,016 / 114,688 字节 | 是 |

**自动回连 3/3 成功；严格三秒门槛未证实。** 第二轮上界含宿主开销，不据此声称精确设备耗时超标，也不能算三轮全过。没有做拔电冷启动或休眠唤醒。脚本未进入 ROM、未写 Flash；串口已释放。Android 可用性已向用户询问，未自行减免验收。diag1 保留未刷入状态，Build/Host tests 结果不变；完整 F0 未通过，F1 不开始。

安卓设备现已可用，但配对前发现原 F0 的三份绑定上限配合 `ble_store_util_status_rr`，满额会自动淘汰最早绑定（已按本机 IDF 6.0.2 NimBLE 源码核实）。为保留已有绑定，已向用户说明并等待是否接受一台旧设备可能需重配；未开放新的配对窗口，安卓仍 NOT RUN。本轮仅阅读源码/枚举端口，没有 NVS 读取或更改，没有构建/刷写操作。

用户已明确接受继续安卓并可能需要重配旧设备。已启动原 F0 的状态采集并给出安卓配对/音量操作，结果 IN PROGRESS，未提前记为通过。该授权仅覆盖正常配对可能发生的旧绑定淘汰，未执行 NVS 擦除或固件刷写；diag1 未安装。

本次安卓未完成：用户确认设备可见，工牌出现六位配对码；手机端输入/确认方式及错误仍待厘清。240 秒采集共 136 次状态、0 次就绪，安卓 HID/连接中内存 NOT RUN/未验证；串口已释放。未读取绑定数据，不确定是否已经发生淘汰。下一次按安卓实际弹窗，在新的 60 秒窗口完成输入/确认，不使用过期码。Build/Host tests 无变更，F0 不放行。

最新用户说明：**手机直接配对失败，工牌六位码一闪而过**。Android 配对 FAIL（用户报告），原因未定，不再将其描述为等待输入。原 F0 未提供安全/断开原因码；已重新校验此前 diag1 固定归档（Build/44 项宿主门禁仍 PASS）并请求 app-only 写入授权及手机型号/系统版本。授权尚未取得，未刷入、未清绑定或 NVS、未改安全参数。不能将旧 SDK 相似 issue 当成本机根因；需实际日志后再修复。F0 不放行。

### 最新：diag1 已安装，SMP 确认值不匹配

用户明确批准固定 app-only 写入。安装器同连接重验设备身份、C3/8 MiB、安全状态、实测旧分区；仅 app `[0x10000,0xad640)` 写后校验 PASS，随后启动标记确认 F0 diag1。当前 app SHA256 `b0c39fb71ca8eb2de0ad0b1f26fd0b7e164f1d4c54cfee92c8738e47c69f7d30`；bootloader/表/NVS/素材未被刷写。此前 Mac/Windows/iPhone 结果绑定原 `ea6789e…5074c`，不能当作此镜像已实测。

手机按用户信息记录为“荣耀9s pro / 鸿蒙 OS 3.0.0”，未独立核对型号。diag1 抓到连接成功、security_request rc=0、显示码动作=3，随后 **status=1028 / 0x404：SMP Confirm Value Failed（本地确认值不匹配）**，加密/认证/绑定均未建立；断开 reason=517 / 0x205 是后续认证失败。显示码到失败 251 ms，配对窗口开放到失败 2241 ms，排除该次 60 秒到期；失败发生在新绑定持久化前，并非已证实的槽满写入失败。根本兼容原因尚未确定。

[Espressif 相似 issue](https://github.com/espressif/esp-idf/issues/14959)涉及旧 SDK/其他手机，只作背景；未换 SDK、去掉认证条件或清空绑定。按[华为官方排查步骤](https://consumer.huawei.com/cn/support/content/zh-cn15960040/)安排仅重启手机蓝牙模块后一次受控尝试，结果待取。Build/44 项宿主检查保持 PASS；diag1 刷写/启动 PASS、鸿蒙配对 FAIL；HID/连接中内存、其他平台当前镜像复测、严格三秒门槛仍未验证，F1 不开始。

## 最新：diag2 数字比较路径已通过鸿蒙配对、音量和内存

diag1 重启手机蓝牙模块后仍然 0x404（显示码动作后约 300 ms）；没有解决原显示码流程。新增显式 `>tk.pair.compare` 可选 F0 实验：DisplayYesNo + SC-only，仍要求 MITM/绑定；只允许数字比较动作 4。实体短 OK 接受、长上拒绝，串口模拟键不能批准，过期/零令牌拒绝。默认长下仍是原 DisplayOnly，规则/作者默认键位/素材未改。实验尚未推广为产品默认策略。

**Build PASS / Host tests PASS（46：18 Node + 28 Python，1,559 步 JS 重录一致）**。完整构建/合并/布局、无 Wi-Fi 初始化符号、归档独立校验通过；仍为 ESP-IDF 6.0.2、C3、8 MiB、无 PSRAM。

| diag2 固定产物 | 字节 | SHA256 |
|---|---:|---|
| app（当前已安装） | 646,048 | `00517903fa87f3f3fd9bb820aa6b7882b3356cfc3a343e0694989b06fdc38982` |
| 合并镜像（未刷） | 711,584 | `116944dcbb1ced392e1d16757fc010f7df2de7b3d22458d4f6ead517c9ed5298` |
| ELF | 8,553,072 | `916dbdece9b9772eccf0c30e2cbda9742608ef3ec2a413ddae66ce2fe1a622fd` |
| MAP | 5,812,944 | `9f535b7cde029acb8a48debbedb5e709dccfd078edbbee429619fa0280e82282` |

用户已单独授权该固定 app 及实验，同连接重新核验身份/C3/8 MiB/实测旧表后仅写 `[0x10000,0xadba0)`，擦除扇区截至 `0xae000`，写后验证及 F0 diag2 启动标记 PASS。表/NVS/素材保留，原 app 私有回退文件保留。当前安装镜像已变，历史 Mac/Windows/iPhone 验收仍只对应原镜像。

前两次未完成实验：一次窗口过期后长下切回普通模式（动作 3/0x404）；一次确实显示比较数字（动作 4），但用户只确认手机，没有实体 OK，连接靠近窗口末尾，60 秒到期主动中断（status=7，disconnect=534）。没有把这些记作双方确认后仍失败。私有观察脚本改为未见连接时提前刷新广播，连接后停止刷新；不自动确认。

本次用户确认两边一致、实体短 OK 和手机均确认，随后 `SECURED / ready`；实体上键使手机音量增加且保持就绪。设备时钟：连接 575912、比较提示 576263、实体接受 609692 / rc=0、加密成功 610021（encrypted/authenticated/bonded 全 1）、双报告订阅 612712、ready 612713 ms。**鸿蒙数字比较配对/音量/连接中内存 PASS**：堆最低 195,232，最大块 114,688 字节，test=false。完成计数 5、失败 0 是聚合计数，不推定按键次数；39,521 ms 是人工配对区间，不是重启回连时间。完整采样仍在归档，接着对同一手机做三轮重启计时。

**Unverified**：原显示码兼容根因、默认产品配对策略、当前镜像其他平台完整复测、严格三秒全程回连、冷启动/休眠、完整屏幕/按键及 JS–C 应用状态对拍。F0 尚未全过，F1 未开始；未提交、推送或发布，原始日志/绑定/设备身份不入库。

## 最新：diag2 三轮回连 FAIL；diag3 固定候选待授权

上述比较采集已结束：300 秒、148 次状态、116 次真实就绪，最低堆/最大块及 5 次完成/0 失败与上节一致。随后对同一手机做三轮 USB 硬件复位，新启动标记和清零计数证实重启，均无需重配自动就绪：

| 轮次 | 复位请求到就绪主机上界 | app 的 ready 事件 uptime | 堆 / 最大块 |
|---|---:|---:|---:|
| 1 | 11,640.0 ms | 11,596 ms | 196,116 / 114,688 字节 |
| 2 | 11,250.0 ms | 11,205 ms | 196,116 / 114,688 字节 |
| 3 | 11,547.0 ms | 11,509 ms | 196,116 / 114,688 字节 |

**三秒门槛 FAIL**：app 就绪事件自身已 >11 秒，不只是主机上界较大。三轮定向阶段均无连接，约 10 秒后 reason=13 超时，转 filter=2 上次设备白名单后约 0.7–1.1 秒 ready；延迟阶段已定位，手机不响应定向广播的底层原因未定。没有把自动回连成功当作三秒通过；没有拔电或休眠测试。

已实现 diag3 候选：定向阶段缩为 500 ms，然后只许上次设备连接的白名单广播；整体 10 秒回连界面期限不变，保留最初计时起点，期限不截断活跃安全握手。加密/认证/双订阅要求、默认 DisplayOnly/可选数字比较、键位、NVS 与素材不变。仅传输策略变化，原型页面规则/1,559 步基准不变，FIRMWARE_PLAN 已同步。新增阶段边界/uint32 回绕检查，**Build PASS / Host tests PASS（47：18 Node + 29 Python）**，构建/合并/布局/无 Wi-Fi 初始化/固定归档独立 verify/候选 inspect 全过。

| diag3 固定产物（均未刷） | 字节 | SHA256 |
|---|---:|---|
| app | 646,272 | `cb5eeda654b3e22110dc0119ac17df0773c4c8a56a4ac12fbfaf999c7abf830d` |
| 合并镜像 | 711,808 | `2192d4137e1a12e1d44e798c2c11646e8fd501245004fd8b9b9549160224c532` |
| ELF | 8,554,448 | `913e31042009802f6ecf0bcb09fbb850e492e8bc83fd5b8157a5ca41ac26acbd` |
| MAP | 5,813,301 | `5de5fc7c4922cfe1a129a2d6904826b0eeaf213a40b313f3f88d5573c3295899` |

归档 `build/firmware/2192d4137e1a12e1d44e798c2c11646e8fd501245004fd8b9b9549160224c532/`。重新枚举 COM12，并只读再次核对同一私有身份/C3/实际 8 MiB/旧 factory 容量 2,031,616 字节，分区表 SHA256 不变；读回当前 diag2 哈希一致。候选按实测小分区校验通过；未读 NVS、未写 Flash，已复位释放端口。

仅在取得此固定候选授权后才可 app-only 写 `[0x10000,0xadc80)`、擦除至 `0xae000`；实际写入同连接再次核验设备/容量/布局，保留表/NVS/素材。**授权 PENDING，diag3 Device tests NOT RUN，设备仍为 diag2。** 下一步在保留手机绑定下复测三轮回连。默认显示码兼容、其他平台当前镜像、冷启动/休眠、完整应用状态对拍仍未完成，F0 不放行、F1 未开始；没有提交、推送或发布。

## 最新：diag3 已安装；回连门槛仍 FAIL，Tango 2S 待手机断开

用户明确批准后，固定 `cb5eeda654b3e22110dc0119ac17df0773c4c8a56a4ac12fbfaf999c7abf830d` 已通过同连接身份/容量/旧表校验并仅 app 写入/验证。表/NVS/素材保留。三个新启动标记均为 F0 diag3，无需手机重配。

| 轮次 | USB 复位到就绪主机上界 | app ready uptime | filter=2 开启 uptime | 堆 / 最大块 |
|---|---:|---:|---:|---:|
| 1 | 6,922.0 ms | 6,885 ms | 1,024 ms | 196,108 / 114,688 |
| 2 | 5,344.0 ms | 5,316 ms | 1,003 ms | 196,116 / 114,688 |
| 3 | 11,234.0 ms | 11,214 ms | 997 ms | 196,116 / 114,688 |

已有绑定自动回连 3/3、认证/订阅/内存 PASS，三秒门槛 **FAIL**。白名单已提前开启，实际链路在 6,334 / 5,015 / 10,813 ms 才建立；剩余原因不明，未断言手机或 RF 哪端有缺陷。用户手机目前不在身边，亮屏/锁屏/距离条件未确认，diag3 实体音量复测 **NOT RUN**；不能继承 diag2 物理效果通过。后续 90 秒采集 42 次均真实就绪，堆 196,116/最大块 114,688、发送失败均 0，已释放串口。

用户提供 iReader Tango 2S 作为补充设备（系统版本未提供、HID 兼容未实测），以及未来办公室小米电视目标。新增阅读器试验窗口一打开，旧手机即用已有绑定自动连回，639 ms 就绪、没有新的比较码事件；不能记作阅读器成功或失败。用户表示能让手机断开，待其回复“已断开”再继续，无须删除旧绑定。

用户明确三份绑定满额时新增替换最早绑定，后续普通新增不再逐次请求淘汰授权；这是配对关系而非六位码、当前配置并非芯片固定上限。已将原型/设计/固件计划从“满槽先手删”统一为 FIFO：取消/超时不删除旧记录、普通回连不重排。**最新 48 项宿主检查（19 Node + 29 Python）与 1,582 步 JS 重录 PASS**，新增覆盖满额取消、成功替换、连续淘汰及回连不改先后。作者 HID 默认表字节不变；原 1,559 步保存在 Git 基线。此后仅改原型/文档/基准，安装 app 未变；没有开始 F1 C 应用移植。

**Build PASS（已安装固定 diag3）/ Host tests PASS（48）/ Device tests：diag3 回连/内存部分 PASS、三秒 FAIL；Tango 2S NOT RUN / Unverified：当前实体 HID、默认显示码兼容、其他平台、冷启动/休眠、阅读器/电视及完整 JS–C 对拍。** F0 未放行；没有提交/推送/发布，原始日志与身份/绑定不入库。

## 最新：F1 开发候选完成宿主和构建门禁（实机暂停）

用户明确要求停止本轮设备测试并继续开发。依此实现默认应用的完整纯 C 模型、默认 HID 表、十页中文占位 UI/二维码/六位配对码、真实三槽选择/类型/删除/FIFO、设置及槽 CRC 持久化、开机/按键/音频队列和休眠接线。生产启动没有演示绑定，只在真实认证及双报告订阅完成后允许 HID。切换/删除/配对由 NimBLE 主机队列执行，UI 单独拥有模型；串口 test 模式的模拟动作不发 HID、不写设置/绑定，退出恢复原模型并重读真实槽；真实 BLE 生命周期仍独立维护密钥，test 不是 NVS 只读锁。模拟计数与实际发送结果分开。

**Build PASS**：原生 Windows `./tools/validate.ps1 -Stage F1` 完整通过，ESP-IDF6.0.2/C3/8MiB/无PSRAM，受版本管理 defaults 重新生成隔离配置、构建、合并、布局/MD5/偏移、无 Wi-Fi 初始化符号及固定归档验证。app 小于实测旧 factory 的 2,031,616 字节，但计划分区表仍与设备旧表不同，合并镜像只作构建核验，不能用于这台工牌升级。另以 `-Stage F0 -FirmwareOnly` 回归通过；新 F0 回归 app 647,232 字节也未刷入，固定归档 `d4d5b2d7c3856abae70696ac3424c8de1fbc6592a82ec1fb4acd7ba09eeea17b` 不替代已安装 diag3。

**Host tests PASS：71（20 Node + 51 Python），无跳过**。1,582 步完整 C 状态/全部输出/sleepDue 与 JS 默认参考逐步相等，三项故意 C 变异被抓到；默认四 OS/十页覆盖。渲染器 >80 个代表帧逐像素检查脏刷新与全刷新，检查宽六位码和二维码同尺寸换内容。三槽/设置/迁移/保存失败用合成地址与 RAM NVS/NimBLE 提供器测试，不代表真实 Flash 断电/RTOS 并发验收。F2 自定义配置尚未实现，不能将默认配置对拍扩为 F2 通过。

| F1 固定产物（未刷入） | 字节 | SHA256 |
|---|---:|---|
| app | 909,696 | `2bd07a8b48ebde05ad97ed8d2e9cfcfb22377df94eb66a594e1ec536e17c7d79` |
| 合并镜像 | 975,232 | `93ddf1bad638082fa9881dc54cbb44f866064b9a410fcb659c097e6b2e139e7e` |
| ELF | 9,874,224 | `feff759bec8a7cb279bc7cf63d461df27aebc6645f9239639717e72b946ca73e` |
| MAP | 6,152,385 | `6a4c59b459f844ce9d27e064b2c1ee0e1ced1a4279722acc5c2e9ac0efd9200d` |


精确归档 `build/firmware/93ddf1bad638082fa9881dc54cbb44f866064b9a410fcb659c097e6b2e139e7e/`，已独立 `archive_firmware.py verify` 再验。机器可读证据 `validation/f1.json`；原始364份素材/90,980,640字节再次校验 PASS，未生成新美术，作者 `tk_hid.js` 哈希不变。F1 仅将现有 atlas 首帧转 RGB565 并保留原 alpha，字体子集/OFL/源哈希随源码保存。界面预览：[实际 C 渲染器截图](images/f1/overview.png)，带演示设备，仅为宿主画面。

三槽为“新增替换最早，普通回连不重排”。F1 SDK 的第4份密钥容量只供新配对暂存：先提交新槽，再移除 FIFO 旧密钥；提交失败移除新暂存，保留旧槽；启动清理未引用暂存。首次迁移保留 F0 SDK 绑定并导入已选设备/OS 偏好；现阶段设备名称为通用编号。新配对窗口拒绝旧设备自动回连，已有身份需要先明确删除槽再重配；默认 DisplayOnly 不变，可选数字比较仍须工牌实体确认。

**Device tests：F1 NOT RUN，用户暂停后未再打开串口、复位或刷写**。工牌仍为固定 diag3 `cb5eeda6…abf830d`，分区/NVS/素材保持原状。旧 Mac/Windows/iPhone/diag2 物理效果仅保留各自镜像的历史证据；diag3 鸿蒙三秒 FAIL 不改。

**Unverified**：F1 四平台配对/真实 HID、三槽切换10轮/时限与内存、3秒回连、PPT/会议/相机、1小时稳定和50次快按、断电保留、LCD/实体键/提示音、休眠/唤醒均未测；共享 ADC 引脚电气上可能被任一键唤醒，不声称“只有上键”。Tango2S/小米电视依用户要求延期。F1 使用静态参考图和短开机提示音；完整动画/语音/F2配置不在本轮实现内。没有 commit/push/发布，也没有新的刷写授权。

## 最新：F2 配置宿主与构建验收

用户要求继续配置功能，先宿主测试/构建，刷机和真机以后。本轮在已有F1上接通快捷键/名片编辑、平台组合键/多媒体/ASCII文字、校验、USB分段收发、CRC、NVS保存、开机读回及提交后立即更新模型。网页写入后自动读回核对完整配置才报成功；浏览器保存和工牌写入分开。作者默认HID表、原364份素材、身份/帽标均保留。

**Host tests PASS：87（27 Node +60 Python），无跳过。** 1,710步完整状态/输出/sleepDue对拍（原1,582 +128自定义配置、四OS），三项C变异仍被抓到；JS客户端实际通过stdio连接生产C协议/解析/内存NVS端点，写入/保存/读回通过。另有同语料JS/C校验、模拟重启恢复、64字符宏、空平台、组/卡缩减、4000字节边界、坏CRC/JSON/UTF8/base64、超时/中断/test模式/存储故障和损坏记录保留测试。存储故障为RAM提供器注入，不能当作真实Flash断电验证。

实际本地配置页检查了编辑→浏览器保存→重载读回→恢复默认，未连接时USB读写按钮禁用，控制台错误/警告0；没有点击连接或调用真实串口。截图：[配置页](images/f2/config-page.png)。C渲染器的自定义中文、二维码、名片/组数和脏刷新均检查：[C预览](images/f2/overview.png)，它使用合成配置/演示设备。

自定义名称使用同源思源黑体21,281字形的16px/1bpp Flash备用字库，不新做美术。已修正全字库极端字形撑大line_height而导致普通中文字缩小的问题，按名义字号缩放；新增尺寸断言并复验逐像素脏刷/全刷。真实LCD可读性和内存仍未验收。

**Build PASS：F2 `0.2.0-f2-dev1`，ESP-IDF6.0.2/C3/8MiB/无PSRAM。** 原生PowerShell完整门禁通过，最终字号修正后增量构建/合并/布局/无Wi-Fi初始化/固定归档通过，F0和F1构建也回归通过。新增锁定cJSON1.7.19~2，cmake_utilities保留原1.1.1，其余依赖版本未升级。app 1,849,584字节，小于实测旧factory2,031,616字节，余量182,032字节；计划表仍与设备不同，不能刷合并镜像或默认flash。

| 固定F2产物（未刷入） | 字节 | SHA256 |
|---|---:|---|
| nabo-toolkit.bin | 1,849,584 | `55967cb3a9c89acc520bae2e295e7d92d52db8a0a0a1050cb71718da4428cb67` |
| nabo-toolkit-merged.bin | 1,915,120 | `002ba9facfb572270d1d6c13672994c86e10c468e8cc5c48b7be3846d0f10c13` |
| nabo-toolkit.elf | 11,035,516 | `6eb00de3a5cece2371279bebd420ff915df3919a343d3f220e82c1451e62b5be` |
| nabo-toolkit.map | 6,287,364 | `42f567a86b689a0431bb826e07fc5b317c487b36d49bbcfc16e1cff322641b3a` |

归档 `build/firmware/002ba9facfb572270d1d6c13672994c86e10c468e8cc5c48b7be3846d0f10c13/`，已独立verify，最终源码清单与工作区一致；详细证据 `validation/f2.json`。F1回归 `build/firmware/7b10d300b76d70d1b5f88a96ad55cb74d7ed25f12e84c6fdb07228fc62e48267`，F0回归 `build/firmware/8fbd04b62ad7928c5f9bdaa37a01d7ae2fd0fe41d0e0e6a889fef5b363bd8992`，均未安装。操作/限制/协议见 [配置说明](CONFIGURATION.zh_CN.md)，Windows构建用 `./tools/validate.ps1 -Stage F2`；原始素材再次364文件/90,980,640字节PASS。

**Device tests：NOT RUN。** 本轮不枚举/打开COM、不刷写、不操作蓝牙或设备，工牌仍固定F0 diag3 `cb5eeda6…abf830d`，旧表/NVS/素材原样。没有commit/push/发布。

**Unverified**：实际USB权限/复位/拔线与写入读回、真实Flash断电保留/错误语义、配置后的实体HID/文字/扫码、LCD及连接中堆/最大块，还有既有F0/F1真机项目。鸿蒙三秒FAIL不改，Tango2S/电视延期；完整动画/语音仍待F3。F2源码/宿主/构建完成，不等于F2真机或发布验收通过。

## 最新： F2 已授权刷入；真实 USB 配置与重启保留通过（2026-10-27，最新）

用户随后明确“做好就刷机验证”。重新枚举并同连接核对身份、ESP32-C3、实际8MiB和旧factory0x10000/0x1f0000，先安装固定dev1。用户确认菜单、中文、上/下实体键正常；保存/读回通过，但连续读回出现丢段，客户端按长度检查报错，没有误报成功。保留失败证据，私有备份后恢复了原配置。

修正为IDF带中断缓冲的USB控制台（TX2048/RX512，非阻塞输入）；SDK默认轮询VFS在主机停顿50ms后可丢字节。私有采集也改为立即读取，USB复位后重开端口，不能将改善归为已证明唯一根因。**Build PASS / Host tests PASS：87（27 Node+60 Python），1,710步完整对拍。** 编译依赖显式声明USB驱动，未改SDK版本、键位或美术。

当前安装 **0.2.0-f2-dev2**：app **1,859,696字节**，SHA256 `49e596ca849119428f1d9cc95f6ff91b9c7016a99e6e9fca53e5285bb3185d57`。固定归档 `build/firmware/35b077ef48a7ecbee1b671c28ed60b157deade1028b46bf76a399929bd1a45b4/` 已独立verify及源码清单比对。仅写 `[0x10000,0x1d6070)`，擦除截至0x1d7000；写后app verify PASS，复位前分区表/NVS/PHY/素材首扇区前后哈希相等，整个素材区在写/擦范围外。没有整片素材读回哈希；运行期配置保存/槽选择是正常NVS功能写入，不能称“NVS字节永远不变”。旧diag3和dev1回退app私有保留，未刷合并镜像/分区表、未整片擦除。

**Device tests 部分PASS**：生产JS客户端通过实际USB连接，真实保存/读回、坏CRC/非法ASCII拒绝并保留旧配置、取消、约10,010ms设备接收超时、test模式拒写及允许读回均PASS；两轮USB硬件复位的新F2启动标记uptime748/746ms，临时配置和恢复后的原配置分别保留，最后连续20次完整读回相等，崩溃标记0，原配置已恢复。测试只临时改分组名/名片说明，HID绑定不改。这是实USB和真实NVS，不是浏览器权限弹窗验收，也不是拔电冷启动。

Windows用户确认重新配对、粘贴和音量正常：**dev2 Windows配对/快捷键Ctrl+V/媒体音量 PASS**。旧槽首次回连失败原因未定，不宣称修复旧绑定回连。默认配置220次真实就绪、堆最低113,772；自定义配置175次就绪、堆最低113,664；最大块均98,304字节，达到60KiB/30KiB门槛，发送失败/崩溃标记0。实机操作后槽数为1，三槽压力和全部旧设备迁移尚未验收。

**自定义配置实体效果和断电保留 PASS**：用户确认只有一组“配置验收”，OK实际输入NABO-F2-TEST；名片显示“验收 / NABO-F2 / 保存读回测试”，手机实际扫码识别https://example.org/nabo-f2。最初“网页不对”指测试地址没有NABO页面，后续已核对原始链接相等，不记作二维码编码失败。用户拔USB、侧面关机、约5秒后开机，确认测试配置仍在；接回USB后程序读回确实与临时配置完全相等，再恢复原快捷键/名片并读回一致。临时配置已清除。该结果证明成功提交后实际断电保留，不证明写NVS过程中断电/硬件存储故障的语义。

**Unverified**：实际Chrome/Edge权限/页面USB流程、传输中拔线、写NVS过程中断电/真实硬件故障语义、新镜像其他平台及旧绑定回连、三槽压力/时限、3秒回连、睡眠和其余F1验收。既有鸿蒙三秒FAIL保留；Tango2S/电视延期。无commit/push/发布；身份、绑定、配置备份与原始日志仅在忽略的private目录。

用户再次提醒：完整开机画面、开机音、各工具的素材和动画必须接上。**当前固件仍仅为静态首帧占位，完整F3尚未完成**；七条既有原片/精灵包405,362字节继续沿用，约5.5秒欢迎完整播放/任意键跳过要求保留，不重做素材。旧factory余量现为171,920字节，不能把精灵全部硬塞进app或擅改分区；下一阶段先核对保留FAT资源的访问/可用空间与工具箱专用开机音来源。现有素材索引中音频目录仅VOICE.md，不能将其他项目欢迎语或短提示音冒充工具箱开机音，也不重复付费生成。
