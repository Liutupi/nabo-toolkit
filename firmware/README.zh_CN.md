<p align="right"><strong>简体中文</strong> · <a href="README.md">English</a></p>

# NABO 工具箱 F0

这是完整工具固件之前的蓝牙探路版。复用 Adventure 的 BSP、直绘渲染器和文字读取器，诊断界面重新实现，没有地图、游戏或旧菜单。屏幕用已启用 Montserrat 字体的英文 ASCII 文案；中文蓝牙名称不由 LCD 字库显示。

使用 **ESP-IDF 6.0.2**、ESP32-C3、8 MiB Flash、无 PSRAM。NVS/PHY/factory/assets/files 边界及 `ai-passport-nabo` 板型身份保持不变；应用使用整数，无 IRAM 标记，不初始化 Wi-Fi。

激活 IDF 后，在仓库根目录运行：

```sh
./tools/validate.sh --static
./tools/validate.sh --firmware
./tools/validate.sh
```

完整门禁从受版本管理的默认配置建立隔离配置，清除依赖 C 源码目录的 macOS AppleDouble 元数据，构建、合并、检查镜像偏移/分区 MD5/重叠，并将精确产物按合并镜像 SHA256 归档到 `build/firmware/<sha256>/`。依赖已锁定；BSP 来源与许可在 `LICENSE.FoloToy`，渲染/文字代码来自 `nabo-adventure/firmware/main/adv_{gfx,shapes,text}`。

| 操作 | 效果 |
|---|---|
| 菜单 OK | 进入蓝牙测试 |
| 测试页上 / OK | 音量加 / Mac Cmd+V 或 Windows/手机 Ctrl+V |
| 测试页下 | 切 Mac/Windows，保存在 `nabo_tk` |
| 长上 500 ms | 返回；正在配对则取消 |
| 长下 500 ms | 开放配对 60 秒 |
| 长 OK 500 ms | 回连上次设备 |

没有保存设备时，开机开放配对 60 秒；已有设备则先低占空比定向广播 10 秒，再仅允许上次设备通过白名单连接。屏幕保留配对码前导零，不向日志输出配对码和设备地址。使用 DisplayOnly、绑定、MITM、安全连接；认证加密且两个报告都订阅后才发 HID。64 深队列按“按下 → 45 ms → 松开 → 35 ms”发送；断线用代次废弃排队和在途请求。松开失败先重试，再断连，避免修饰键粘住。

F0 保存一个上次设备和 OS 偏好，NimBLE 最多存三份绑定。三槽 UI、完整工具、开机动画、配置导入、语音和休眠属于后续阶段。只有 UI 改模型；按键/蓝牙/串口回调只入队。探路模型与后续完整 JS–C 移植分开。

串口命令：`>tk.status`、`>tk.key=up|down|ok|long_up|long_down|long_ok`、`>tk.pair`、`>tk.reconnect`、`>tk.test=1|0`。测试模式不发 HID，不算真机验收。`ready_ms` 从广播尝试开始计时；验收三秒回连还要结合开机时间戳。

构建门禁不会刷机。`tools/flash_candidate.py` 默认只检查本地镜像；显式 `upgrade` 模式必须给设备 MAC 与 app SHA256，在同一连接校验芯片、安全状态、8 MiB 和计划表或实测旧 Adventure 表（factory 0x10000/0x1f0000、FAT assets 0x200000/0x600000），并按实际 app 容量再次检查，只写 `0x10000` 的 app 并校验，收据放私有目录。不整片擦除，也不强制全 Flash 备份。须先识别设备并取得用户刷写授权。合并镜像用于 `0x0` 且可能重置数据，不能混用为 app 单独升级。

精确产物身份及 F0 真机待验项见[验证记录](../docs/VALIDATION.zh_CN.md)。配对、回连和堆实测通过后才进入 F1。
