[简体中文](README.zh_CN.md) · **English**

# NABO desktop shortcut bridge (experimental)

The existing badge sends Bluetooth keyboard keys. The desktop bridge registers F13/F14/F15 to open Codex, Claude and Grok Bot, respectively, and tries to focus an editable input. **Check that it is the chat input, then trigger your own Typeless shortcut manually.** It does not start recording, submit text, or read input contents. An editable input is not necessarily the chat composer.

On Mac, the user confirmed all three assistant launches, one Typeless result in a chat input, and switching back using this exact firmware and the retained personal configuration. Windows has not been run. App versions, OS permissions, foreground focus and accessibility support affect behavior. Click the chat field manually when the bridge cannot unambiguously focus it.

## Badge configuration

1. Open the [configurator](https://liutupi.github.io/nabo-toolkit/) in desktop Chrome or Edge. If the public page has not been updated yet, run `python3 -m http.server 8770 --bind 127.0.0.1 --directory game-art/toolkit` from the repository root and open `http://localhost:8770/prototype/config.html`.
2. Connect the badge, read its current configuration, and click “加入 AI 助手快捷键组”. Six groups are supported; if all are used, decide which to remove yourself. A duplicate is rejected.
3. The preset sets UP `Codex` → F13, DOWN `Claude` → F14, OK `Grok Bot` → F15 for both desktop families. This helper does not support phones.
4. Check the other groups and cards, then explicitly write and verify the configuration. The helper does not read or write the badge. The preset is placed immediately before Typeless: while lit, hold OK to move to Typeless, then use its existing voice-input key. When finished, hold DOWN to return to AI助手.

The new default shortcuts include AI助手; installing the bridge does not replace saved personal settings. F13–F15 must be free; registration reports a conflict at startup.

## macOS

Install Xcode Command Line Tools and the three desktop apps. From the repository root:

```sh
mkdir -p build/desktop-bridge
swiftc desktop-bridge/macos/NaboBridge.swift -o build/desktop-bridge/nabo-bridge
./build/desktop-bridge/nabo-bridge
```

Keep the terminal open. Grant Accessibility access to the terminal or compiled program as requested in System Settings → Privacy & Security, and restart it after granting access. Codex and Claude are found by bundle ID; Grok Bot is found at `/Applications/Grok Bot.app` or `~/Applications/Grok Bot.app`. Stop with Ctrl+C.

## Windows

Use Windows PowerShell 5.1. Replace each example path with the installed application's actual executable path, run from the repository root, and keep the window open:

```powershell
powershell.exe -NoProfile -STA -File .\desktop-bridge\windows\NaboBridge.ps1 `
  -Codex 'C:\path\to\Codex.exe' `
  -Claude 'C:\path\to\Claude.exe' `
  -GrokBot 'C:\path\to\Grok Bot.exe'
```

These are placeholders, not asserted installation paths. System restrictions, privileges, or multi-process windows may prevent automatic focus; click the chat input manually if needed. Close PowerShell to stop. Windows compilation, launch, keyboard and focus have not yet been tested.

## Interaction scope

One button opens one assistant **while the new shortcut group is selected**; navigation into that group still uses existing badge controls. The existing Typeless group remains separate, and Typeless must already be running and signed in. The bridge only registers three hotkeys; it does not change pairing, firmware, accounts, or project selection. Existing dark-screen long-OK behavior is unchanged.
