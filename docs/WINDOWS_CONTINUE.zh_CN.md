<p align="right"><strong>简体中文</strong> · <a href="WINDOWS_CONTINUE.md">English</a></p>

# Windows 接班

**最新（2026-10-28，HANDOFF22–23）**：F3 dev3已安装；100项宿主/1,710步对拍/构建通过，完整欢迎、各工具动画、开机音及无爆破按键音获用户验收。原364份不变，现367份素材。公开测试版发布及配置页见README；固件固定ESP-IDF6.0.2，旧分区保护不变。

沿用 `Liutupi/nabo-toolkit`、main、交接基线5fb23a0及本地修改。先找已有仓库、`git status --short --branch`，保留本地修改后再同步 main；没有才克隆，不另开项目。不要用重置/覆盖清理本地修改。AGENTS、HANDOFF最新节、VALIDATION、FIRMWARE_PLAN、UI_DESIGN为权威。

素材全在 Git：364文件/90,980,640字节，原图/视频/提示词/脚本/审片/RGBA/索引/精灵/原型都齐全，不需要用户重传或重新生成。先运行：

```powershell
python tools/verify_assets.py
git status --short --branch
```

`python -m http.server 8770 --directory game-art/toolkit/prototype` 可看原型。浏览器 HID 是模拟；完整欢迎约5.5秒、任意键跳过。固件离线，作者默认键位以 `tk_hid.js`、规则以 `tk_core.js` 为准。

检查已安装的 `nabo-passport-game` 和五个 `passport-*` skills，缺失按交接安装。**项目固定 ESP-IDF6.0.2、ESP32-C3、8MiB、无PSRAM**，不用通用 skill 的其他 SDK。Node、Python、可生成本机动态库的宿主 C11 `cc` 必需；RISC-V交叉编译器不能替代宿主编译器。

本机已找到 IDF6.0.2 和 w64devkit；其他机器先确认实际位置。先把宿主编译器加入 PATH，再激活 IDF，让 SDK 自带 CMake/Ninja 优先，避免 w64devkit 工具覆盖 SDK 工具：

```powershell
$env:Path = 'D:\nabo-passport-tools\w64devkit\bin;' + $env:Path
. 'C:\Espressif\esp-idf-v6.0.2\export.ps1'
$env:PYTHONIOENCODING = 'utf-8'
idf.py --version  # 必须 ESP-IDF v6.0.2
./tools/validate.ps1 -Stage F3             # 宿主+构建/合并/验证/归档
./tools/validate.ps1 -Static               # 只做宿主
./tools/validate.ps1 -Stage F0 -FirmwareOnly # 保留 F0 探路版的回归构建
```

F2门禁从 `sdkconfig.defaults;sdkconfig.f1.defaults;sdkconfig.f2.defaults` 重建隔离 `build/f2/sdkconfig`；F0在 `build/f0/`。已生成字体/派生占位图随源码保存，普通构建无需字体转换器/Pillow/ffmpeg。依赖由锁定清单重建，不复制旧 SDK/managed_components/build。原生 PowerShell 完整门禁已经实跑；ESP-IDF6不支持MSYS，Git Bash只跑静态门禁。Linux/WSL可在对应IDF环境运行 `./tools/validate.sh --f3`，USB访问须独立配置。

Git Bash若 `python3` 是 WindowsApps占位，用子进程映射，不改全局别名：

```powershell
& 'C:\Espressif\tools\git\bin\bash.exe' -c 'python3() { python "$@"; }; export -f python3; bash tools/validate.sh --static'
```

完整门禁先 reconfigure 获取 LVGL 头文件，再做 C 渲染检查；静态模式缺头文件会显式 SKIP，不能算通过。Windows ctypes 在清理前卸载库。完整对拍包含默认及F2自定义配置。RAM NVS/NimBLE 提供器测试不代替真实断电/并发；`docs/images/f2/overview.png` 是实际C宿主截图而非工牌实拍。截图重生成另需Pillow：`python tools/render_toolkit_preview.py`。字体重建工具 `generate_toolkit_fonts.py` 需要 converter1.5.3和与 `firmware/fonts/fonts.json` 哈希一致的现有字体输入，普通构建无需重建。

三槽保留最近新增绑定，新增成功后替换最早，普通回连不重排，无需逐次再问淘汰授权。F1 SDK第4份密钥仅供事务暂存，产品仍3槽。F0迁移保留密钥并导入选中身份/Mac偏好；通用编号名称暂未自动读取远端名字。新配对时阻止旧主机抢回；已有身份须先删除其槽再重配。默认DisplayOnly鸿蒙0x404未解决；可选数字比较仍要求核对两边数字、实体短OK确认。

**继续实机验收**：用户已恢复并授权F2刷机验证。当前为dev2固定app49e596ca…3185d57，不能再按“原工牌跑F0”处理。每次重新枚举COM，别硬编码旧端口；串口打开/USB复位可能重启。新固定产物须先验证哈希、同连接身份/C3/8MiB/实际旧容量，遵守既有app-only授权范围。

旧表：NVS0x9000/0x6000、PHY0xf000/0x1000、factory0x10000/0x1f0000、assets FAT0x200000/0x600000。**保留旧表/NVS/素材；禁止默认 idf.py flash、合并镜像或整片擦除**。dev2 app1,859,696字节，写至0x1d6070、擦除截至0x1d7000。私有收据和脱敏证据见validation/f2.json。共享ADC可能任一键唤醒，不能仅凭代码声称只有上键。

下一步补真实浏览器Web Serial权限/页面流程、传输中拔线及剩余F0/F1门槛；Windows已重新配对并通过默认HID、自定义文字/名片/扫码、连接内存及成功保存后断电保留，原配置已恢复。完整F3动画/开机音仍未接入，现有素材继续沿用。分项记录，不继承旧镜像通过项，不提交私有数据，不擅自发布。
