**简体中文** · [English](README.md)

# NABO 电脑快捷键桥接（实验版）

现有工牌固件通过蓝牙发送普通键盘按键，电脑端程序接收 F13/F14/F15，分别打开 Codex、Claude、Grok Bot，并尝试聚焦可编辑输入框。**查看窗口并确认焦点后，再手动按自己设置的 Typeless 快捷键。**程序不会启动录音、发送内容或自动提交，也不读取输入文字。识别到可编辑控件不代表它一定是聊天框。

Mac 上，用户已用本版固定固件和保留的个人配置确认三个助手呼出、一次 Typeless 文字进入聊天框及返回切组。Windows 尚未运行验证。应用版本、系统权限、前台窗口和无障碍接口会影响结果。自动选框失败或找到多个框时请手动点击；不能保证每个客户端都能自动找到聊天框。

## 工牌配置

1. 用电脑 Chrome/Edge 打开 [配置页](https://liutupi.github.io/nabo-toolkit/)。如果公开页尚未更新，可在仓库根目录运行 `python3 -m http.server 8770 --bind 127.0.0.1 --directory game-art/toolkit`，打开 `http://localhost:8770/prototype/config.html`。
2. 连接工牌并先“从工牌读回”，点击“加入 AI 助手快捷键组”。组数最多 6；如果已经有 6 组，需要自行决定是否腾出一组。重复添加会被拒绝。
3. 页面会为 Mac 和 Windows 均设置上键 `Codex` → F13、下键 `Claude` → F14、OK `Grok Bot` → F15。只在电脑使用，不表示支持手机。
4. 核对其他组和名片不变，再由本人点击“写入工牌并核对”。此操作会写入工牌配置；桥接程序不自行读写或迁移工牌。预设放在 `Typeless` 前一组：该页亮屏长按 OK 切到 Typeless 组，再按已配置的语音输入键；完成后长按下键回到 AI助手 组。

新版默认快捷键包含 AI助手，已存个人配置不会因为安装桥接程序自动变化。确认 F13–F15 未被其他程序占用；桥接启动失败时会提示冲突。

## macOS

需要已安装 Xcode Command Line Tools 和三个桌面应用。在仓库根目录执行：

```sh
mkdir -p build/desktop-bridge
swiftc desktop-bridge/macos/NaboBridge.swift -o build/desktop-bridge/nabo-bridge
./build/desktop-bridge/nabo-bridge
```

运行窗口保持打开。系统设置 → 隐私与安全性 → 辅助功能中，按系统提示允许运行该程序的终端或编译出的程序；权限生效后重新启动。Codex、Claude 使用各自应用标识；Grok Bot 使用 `/Applications/Grok Bot.app` 或 `~/Applications/Grok Bot.app`。按 Ctrl+C 停止。

## Windows

使用 Windows PowerShell 5.1；将以下三个路径换成**本机已安装的实际 exe 路径**，在仓库根目录运行，保持 PowerShell 窗口打开：

```powershell
powershell.exe -NoProfile -STA -File .\desktop-bridge\windows\NaboBridge.ps1 `
  -Codex 'C:\path\to\Codex.exe' `
  -Claude 'C:\path\to\Claude.exe' `
  -GrokBot 'C:\path\to\Grok Bot.exe'
```

这是路径示例，不是安装位置。系统、应用权限或多进程窗口可能阻止自动聚焦；发生时手动点聊天框。关闭 PowerShell 窗口停止。尚未在 Windows 验证该程序的编译、启动、按键和焦点。

## 交互边界

此方案是“当前快捷键组中的一个按键呼出一个助手”，进入该组仍需使用现有导航；它不是从工牌任意页面全局一键唤出。既有 Typeless 组仍由原按键触发，电脑需要已登录并运行 Typeless。桥接仅接收三个注册热键，不会控制工牌配对、固件、账户或项目选择。长按 OK 暗屏时仅唤亮的原行为保持不变。
