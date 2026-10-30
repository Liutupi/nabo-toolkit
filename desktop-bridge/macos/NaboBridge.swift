import AppKit
import ApplicationServices
import Carbon

// F13/F14/F15 are ordinary configurable BLE keyboard usages. No microphone,
// keystroke contents, application text, or network data is read by this helper.
let targets = ["com.openai.codex", "com.anthropic.claudefordesktop", "com.anysphere.sand"]
let names = ["Codex", "Claude", "Grok Bot"]
let macKeys: [UInt32] = [UInt32(kVK_F13), UInt32(kVK_F14), UInt32(kVK_F15)]
var pending = 0
var hotkeys: [EventHotKeyRef?] = [nil, nil, nil]

func attribute(_ object: AXUIElement, _ name: CFString) -> CFTypeRef? {
    var value: CFTypeRef?
    return AXUIElementCopyAttributeValue(object, name, &value) == .success ? value : nil
}

func editable(_ object: AXUIElement) -> Bool {
    guard let role = attribute(object, kAXRoleAttribute as CFString) as? String,
          role == kAXTextFieldRole as String || role == kAXTextAreaRole as String else { return false }
    var writable: DarwinBoolean = false
    return AXUIElementIsAttributeSettable(object, kAXValueAttribute as CFString, &writable) == .success && writable.boolValue
}

func focusComposer(_ application: NSRunningApplication) -> Bool {
    guard application.isActive else { return false }
    let axApp = AXUIElementCreateApplication(application.processIdentifier)
    if let current = attribute(axApp, kAXFocusedUIElementAttribute as CFString),
       CFGetTypeID(current) == AXUIElementGetTypeID(), editable(current as! AXUIElement) { return true }
    guard let window = attribute(axApp, kAXFocusedWindowAttribute as CFString),
          CFGetTypeID(window) == AXUIElementGetTypeID() else { return false }
    var queue = [window as! AXUIElement]
    var matches: [AXUIElement] = []
    var index = 0
    while index < queue.count && index < 700 {
        let element = queue[index]; index += 1
        if editable(element) { matches.append(element) }
        if let children = attribute(element, kAXChildrenAttribute as CFString) as? [AXUIElement] {
            queue.append(contentsOf: children.prefix(max(0, 700 - queue.count)))
        }
    }
    guard index == queue.count, matches.count == 1 else { return false }
    guard AXUIElementSetAttributeValue(matches[0], kAXFocusedAttribute as CFString, kCFBooleanTrue) == .success else { return false }
    guard let current = attribute(axApp, kAXFocusedUIElementAttribute as CFString),
          CFGetTypeID(current) == AXUIElementGetTypeID() else { return false }
    return CFEqual(current, matches[0])
}

func launch(_ index: Int) {
    pending += 1
    let token = pending
    guard AXIsProcessTrusted() else {
        print("无法准备输入框：请在 macOS 隐私与安全性中授权本程序的辅助功能。")
        return
    }
    let grokPaths = ["/Applications/Grok Bot.app", NSHomeDirectory() + "/Applications/Grok Bot.app"]
    let url = index == 2
        ? grokPaths.first(where: { FileManager.default.fileExists(atPath: $0) }).map { URL(fileURLWithPath: $0) }
        : NSWorkspace.shared.urlForApplication(withBundleIdentifier: targets[index])
    guard let url else {
        print("找不到 \(names[index])，请先安装对应桌面应用。")
        return
    }
    let config = NSWorkspace.OpenConfiguration()
    config.activates = true
    NSWorkspace.shared.openApplication(at: url, configuration: config) { application, error in
        DispatchQueue.main.async {
            guard token == pending else { return }
            guard error == nil, let application = application else {
                print("无法打开 \(names[index])：\(error?.localizedDescription ?? "未知错误")")
                return
            }
            func attempt(_ remaining: Int) {
                guard token == pending else { return }
                if focusComposer(application) {
                    print("\(names[index]) 的可编辑输入框已聚焦；请确认它是聊天框后手动按 Typeless。")
                } else if remaining > 0 && application.isActive {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { attempt(remaining - 1) }
                } else if remaining > 0 && remaining > 37 {
                    // Allow a short activation delay, but do not steal focus back.
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { attempt(remaining - 1) }
                } else {
                    print("\(names[index]) 已打开，但未能确认唯一输入框；请点击输入框后再按 Typeless。")
                }
            }
            attempt(40)
        }
    }
}

let handler: EventHandlerUPP = { _, event, _ in
    guard let event = event else { return noErr }
    var id = EventHotKeyID()
    let status = GetEventParameter(event, EventParamName(kEventParamDirectObject),
                                   EventParamType(typeEventHotKeyID), nil,
                                   MemoryLayout<EventHotKeyID>.size, nil, &id)
    if status == noErr && id.signature == 0x4e41424f && id.id >= 1 && id.id <= 3 {
        launch(Int(id.id - 1))
    }
    return noErr
}

setbuf(stdout, nil)
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
var spec = EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyPressed))
guard InstallEventHandler(GetApplicationEventTarget(), handler, 1, &spec, nil, nil) == noErr else {
    fputs("无法注册热键处理器。\n", stderr); exit(1)
}
for index in macKeys.indices {
    let id = EventHotKeyID(signature: 0x4e41424f, id: UInt32(index + 1))
    guard RegisterEventHotKey(macKeys[index], 0, id, GetApplicationEventTarget(), 0, &hotkeys[index]) == noErr else {
        fputs("F\(13 + index) 已被占用，无法启动；请释放快捷键。\n", stderr); exit(1)
    }
}
print("NABO 桥接运行中：F13 Codex、F14 Claude、F15 Grok Bot。Ctrl+C 退出。")
if !AXIsProcessTrusted() { print("请在系统设置中授予本程序辅助功能权限，然后重新启动。") }
app.run()
