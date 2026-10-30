param(
    [Parameter(Mandatory=$true)][string]$Codex,
    [Parameter(Mandatory=$true)][string]$Claude,
    [Parameter(Mandatory=$true)][string]$GrokBot
)
$ErrorActionPreference = 'Stop'
foreach ($path in @($Codex, $Claude, $GrokBot)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or [IO.Path]::GetExtension($path) -ine '.exe') {
        throw "需要已安装应用的 .exe 完整路径：$path"
    }
}
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -TypeDefinition @'
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Windows.Automation;
using System.Windows.Forms;

public sealed class NaboBridge : Form {
    [DllImport("user32.dll", SetLastError=true)] static extern bool RegisterHotKey(IntPtr h, int id, uint mods, uint key);
    [DllImport("user32.dll")] static extern bool UnregisterHotKey(IntPtr h, int id);
    [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint process);
    readonly string[] paths, names = {"Codex", "Claude", "Grok Bot"};
    readonly Timer timer = new Timer();
    Process selected;
    int target, attempts;
    bool activated;

    public NaboBridge(string[] paths) {
        this.paths = paths;
        ShowInTaskbar = false;
        WindowState = FormWindowState.Minimized;
        for (int i = 0; i < 3; ++i) {
            if (!RegisterHotKey(Handle, i + 1, 0x4000, (uint)(0x7c + i))) {
                for (int j = 0; j < i; ++j) UnregisterHotKey(Handle, j + 1);
                throw new InvalidOperationException("F" + (13 + i) + " 已被占用，无法启动。");
            }
        }
        timer.Interval = 300;
        timer.Tick += CheckFocus;
        Console.WriteLine("NABO 桥接运行中：F13 Codex、F14 Claude、F15 Grok Bot。关闭窗口退出。");
    }
    protected override void SetVisibleCore(bool value) { base.SetVisibleCore(false); }
    protected override void WndProc(ref Message m) {
        if (m.Msg == 0x0312 && m.WParam.ToInt32() >= 1 && m.WParam.ToInt32() <= 3)
            Launch(m.WParam.ToInt32() - 1);
        base.WndProc(ref m);
    }
    void Launch(int i) {
        timer.Stop(); target = i; attempts = 0; selected = null; activated = false;
        try {
            var name = Path.GetFileNameWithoutExtension(paths[i]);
            selected = Process.GetProcessesByName(name).FirstOrDefault(p => p.MainWindowHandle != IntPtr.Zero);
            if (selected == null) selected = Process.Start(new ProcessStartInfo(paths[i]) { UseShellExecute = true });
            if (selected == null) throw new InvalidOperationException("未取得应用进程");
            timer.Start();
        } catch (Exception e) { Console.WriteLine("无法打开 " + names[i] + ": " + e.Message); }
    }
    void CheckFocus(object sender, EventArgs args) {
        try {
            ++attempts;
            selected.Refresh();
            IntPtr window = selected.MainWindowHandle;
            if (window == IntPtr.Zero) {
                var name = Path.GetFileNameWithoutExtension(paths[target]);
                var actual = Process.GetProcessesByName(name).FirstOrDefault(p => p.MainWindowHandle != IntPtr.Zero);
                if (actual != null) { selected = actual; window = actual.MainWindowHandle; }
            }
            if (window != IntPtr.Zero) {
                if (!activated) { SetForegroundWindow(window); activated = true; }
                uint foregroundPid; GetWindowThreadProcessId(GetForegroundWindow(), out foregroundPid);
                if (foregroundPid == selected.Id) {
                    AutomationElement focused = AutomationElement.FocusedElement;
                    if (focused != null && focused.Current.ProcessId == selected.Id && IsEditable(focused)) {
                        Console.WriteLine(names[target] + " 的可编辑输入框已聚焦；请确认它是聊天框后手动按 Typeless。"); timer.Stop(); return;
                    }
                    AutomationElement root = AutomationElement.FromHandle(window);
                    var found = root.FindAll(TreeScope.Descendants, new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Edit));
                    var candidates = found.Cast<AutomationElement>().Where(IsEditable).Take(2).ToArray();
                    if (candidates.Length == 1) {
                        candidates[0].SetFocus();
                        focused = AutomationElement.FocusedElement;
                        if (focused != null && Automation.Compare(focused, candidates[0])) {
                            Console.WriteLine(names[target] + " 的可编辑输入框已聚焦；请确认它是聊天框后手动按 Typeless。"); timer.Stop(); return;
                        }
                    }
                } else if (attempts > 2) { timer.Stop(); Console.WriteLine(names[target] + " 未获得前台，请手动选择输入框。"); return; }
            }
        } catch (Exception e) { timer.Stop(); Console.WriteLine("无法确认输入框：" + e.Message); return; }
        if (attempts >= 40) { timer.Stop(); Console.WriteLine(names[target] + " 已打开，但无法确认唯一输入框；请手动点击。 "); }
    }
    static bool IsEditable(AutomationElement e) {
        try {
            object pattern;
            return e.Current.ControlType == ControlType.Edit && e.Current.IsEnabled && e.Current.IsKeyboardFocusable &&
                   e.TryGetCurrentPattern(ValuePattern.Pattern, out pattern) && !((ValuePattern)pattern).Current.IsReadOnly;
        } catch (ElementNotAvailableException) { return false; }
    }
    protected override void Dispose(bool disposing) {
        timer.Stop(); for (int i = 1; i <= 3; ++i) UnregisterHotKey(Handle, i);
        if (disposing) timer.Dispose(); base.Dispose(disposing);
    }
    public static void Run(string[] paths) { Application.Run(new NaboBridge(paths)); }
}
'@ -ReferencedAssemblies @('System.Core', 'System.Windows.Forms', 'UIAutomationClient', 'UIAutomationTypes', 'WindowsBase')
[NaboBridge]::Run(@($Codex, $Claude, $GrokBot))
