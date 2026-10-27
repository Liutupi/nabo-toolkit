<p align="right"><strong>简体中文</strong> · <a href="WINDOWS_CONTINUE.md">English</a></p>

# Windows 接班

私有仓库 `Liutupi/nabo-toolkit`，分支 **main**。全部已确认起始图、Grok 原片、各轮设计/提示词/组装脚本、审片、RGBA 母版、索引帧、二进制精灵、浏览器 atlas、原型、对拍基准、F0 源码及依赖锁定文件都进 Git，**不用重生图或重跑 Grok**。`docs/validation/assets.json` 逐文件记录素材字节数/SHA256，运行 `python tools/verify_assets.py` 可检查齐全性；`.gitattributes` 保持 Windows 源码/基准 LF 换行和媒体二进制不变。

建议克隆到短路径；已有仓库则先保留本地修改再 pull：

```powershell
git -c core.longpaths=true clone https://github.com/Liutupi/nabo-toolkit.git C:\nabo-toolkit
cd C:\nabo-toolkit
git status --short --branch
python tools/verify_assets.py
python -m http.server 8770 --directory game-art/toolkit/prototype
```

打开 `http://localhost:8770/`。原型已用第一批 Grok 精灵，但蓝牙/HID 为模拟。↑↓Enter 操作，按住 0.5 秒为长按；欢迎完整约 5.5 秒，任意键跳过。原型目前用 Google Fonts 和 QR 辅助 CDN，可联网加载或用字体回退；工牌固件不联网。

先读 `AGENTS.md`、`docs/HANDOFF.md`、`docs/VALIDATION.zh_CN.md`、`game-art/toolkit/FIRMWARE_PLAN.md`、`UI_DESIGN.md`。游戏 skill 源在私有 `Liutupi/nabo-skills` 的 `nabo-passport-game/SKILL.md`，请 Windows 上的 agent 自行检查安装；同时检查环境要求的五个 Passport skill。不要沿用 Mac 安装绝对路径；按阶段调用匹配 skill，SDK 以项目要求为准。

固件要求 **ESP-IDF 6.0.2、ESP32-C3、8 MiB、无 PSRAM**，先激活该版本环境。`firmware/dependencies.lock` 与 BSP 组件清单锁定依赖；`managed_components`、SDK、本地 venv、build/调试文件不从 Mac 拷贝，按锁定版本重建。完整宿主门禁需要 Node.js、Python、宿主 C11 编译器。可在工具齐全的 Git Bash 或 Linux/WSL 中运行 `./tools/validate.sh`；IDF 自带 RISC-V 交叉编译器不能替代 ctypes 测试用的宿主 `cc`。WSL USB 访问须另配置，不能假定能看见 Windows 工牌。原生 Windows IDF 终端可以用绝对路径构建：

```powershell
idf.py -C firmware -B C:\nabo-toolkit\build\f0 -D SDKCONFIG=C:\nabo-toolkit\build\f0\sdkconfig build
```

单独宿主检查：`node --test tests/tk_golden/model.test.js tests/tk_golden/prototype.test.js`、`python -m unittest discover -s tests -p "test_*.py" -v`、`python tools/verify_golden.py`。原生 Windows 的 `cc` 必须生成 Windows 可加载库；没有宿主编译器时走 Bash/WSL。素材处理额外需要 ffmpeg/ffprobe，在独立 Python 3.11+ venv 中 `pip install -r tools/requirements-art.txt`；直接用现成素材不需要这些处理依赖。

Mac 构建并已刷入工牌的 F0 app SHA256：`ea6789e39fddc8a7063a94d45c6687cf71d61a11eb56c55cb9aa4bcce305074c`。40 项宿主测试和 Mac 完整门禁通过。用户确认 **Mac 配对、粘贴、音量正常**；连接中堆至少 195,604 字节，最大块 114,688 字节。一次实际 USB 重启后自动回连，广播起算 701 ms；多轮“重启到就绪”精确计时待做。本机打开串口会导致 `USB_UART_CHIP_RESET`，测试时注意这个重启副作用。用户有 iPhone，但因下班暂停此项；**iPhone、Windows、安卓配对仍未验证**。除非用户明确修改验收范围，F0 真机门槛过后才进入 F1。

工牌实测旧分区与构建计划不同：NVS `0x9000/0x6000`、PHY `0xf000/0x1000`、factory `0x10000/0x1f0000`、FAT assets `0x200000/0x600000`。保留的引导程序日志为 IDF 5.5.3，原 Adventure app 和当前 F0 app 为 IDF 6.0.2。**保留现有分区表**。F0 不访问 assets/files，可放入较小 app 区，已只写 app 升级。不要直接 `idf.py flash` 或刷合并镜像覆盖表。保护安装器显式支持这份旧表，并按实际 app 容量检查。Windows 上重新枚举 COM 与设备身份，不要套用 Mac `/dev/cu.usbmodem212401` 或私有收据；新设备/写入范围按要求重新取得授权。NVS 报错不能擦片绕过。

下一步：Windows 配对/粘贴/音量、iPhone 配对/音量，测连接中内存、多轮三秒重启回连，补安卓测试，过约定门槛再做 F1。B2 语音、B6 界面风格板、Grok 第 2 批、F3 素材接固件仍待后续。不要重做第一批素材，不要把 JS 参考轨迹当成完整 JS–C 应用对拍已完成。

MAC/绑定数据、原始设备日志、凭据、build/ELF/MAP 包不进 Git；脱敏结果/哈希在 `docs/validation/f0.json` 和 `VALIDATION.zh_CN.md`。历史 Grok ZIP 的 README 可能提 Mac 投递绝对路径，Windows 以仓库相对 `game-art/toolkit/art/video/batch1/` 为准。

可直接发给 Windows Codex：

> 接续当前仓库的 NABO 工具箱。先读 AGENTS.md、docs/HANDOFF.md、docs/WINDOWS_CONTINUE.zh_CN.md、docs/VALIDATION.zh_CN.md，检查素材清单，保留用户修改。第一批美术、视频、精灵和 F0 源码都已在仓库，不要重做。工牌已运行已校验 F0，Mac 配对/粘贴/音量通过。先做 Windows 与 iPhone 的 F0 测试，再补回连、内存、安卓验收。保留工牌实测旧分区表，重新枚举 COM，需要刷机时取得对应授权。F0 门槛未过不做 F1，不重画 NABO，不改作者默认键位，不提交私有设备数据。
