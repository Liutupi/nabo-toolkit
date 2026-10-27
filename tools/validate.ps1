# Native Windows gate. Activate the project's ESP-IDF 6.0.2 environment first.
[CmdletBinding()]
param(
    [ValidateSet('F0','F1','F2','F3')][string]$Stage='F0',
    [switch]$Static,
    [switch]$FirmwareOnly
)
$ErrorActionPreference='Stop'
if ($Static -and $FirmwareOnly) { throw 'Choose either -Static or -FirmwareOnly.' }
$toolkitRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$toolkitBuild=Join-Path $toolkitRoot ('build/'+$Stage.ToLowerInvariant())
function Invoke-ToolkitCheck {
    param([string]$Program,[string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Program failed with exit code $LASTEXITCODE" }
}
Push-Location -LiteralPath $toolkitRoot
try {
    if (-not $Static) {
        $toolkitVersion=(& idf.py --version | Out-String).Trim()
        if ($toolkitVersion -ne 'ESP-IDF v6.0.2') { throw "Expected ESP-IDF v6.0.2; got $toolkitVersion" }
        New-Item -ItemType Directory -Path $toolkitBuild -Force | Out-Null
        foreach ($config in @('sdkconfig','sdkconfig.old')) {
            $configPath=Join-Path $toolkitBuild $config
            if (Test-Path -LiteralPath $configPath) { Remove-Item -LiteralPath $configPath }
        }
        $toolkitDefaults='sdkconfig.defaults'
        if ($Stage -ne 'F0') { $toolkitDefaults+=';sdkconfig.f1.defaults' }
        if ($Stage -in @('F2','F3')) { $toolkitDefaults+=';sdkconfig.f2.defaults' }
        if ($Stage -eq 'F3') { $toolkitDefaults+=';sdkconfig.f3.defaults' }
        $configPath=(Join-Path $toolkitBuild 'sdkconfig').Replace('\','/')
        Invoke-ToolkitCheck 'idf.py' @('-C','firmware','-B',$toolkitBuild,"-DSDKCONFIG=$configPath","-DSDKCONFIG_DEFAULTS=$toolkitDefaults",'reconfigure')
        # The component manager writes CRLF on Windows; tracked text is LF.
        $lockPath=Join-Path $toolkitRoot 'firmware/dependencies.lock'
        $lockText=[IO.File]::ReadAllText($lockPath).Replace("`r`n","`n")
        [IO.File]::WriteAllText($lockPath,$lockText,[Text.UTF8Encoding]::new($false))
        Get-ChildItem -LiteralPath 'firmware/managed_components' -Filter '._*' -File -Recurse | ForEach-Object { Remove-Item -LiteralPath $_.FullName }
    }
    if (-not $FirmwareOnly) {
        Invoke-ToolkitCheck 'python' @('tools/verify_assets.py')
        Invoke-ToolkitCheck 'node' @('--test','tests/tk_golden/model.test.js','tests/tk_golden/prototype.test.js','tests/tk_golden/config.test.js')
        Invoke-ToolkitCheck 'python' @('-m','unittest','discover','-s','tests','-p','test_*.py','-v')
        Invoke-ToolkitCheck 'python' @('tools/verify_golden.py')
        Invoke-ToolkitCheck 'git' @('diff','--check')
    }
    if (-not $Static) {
        Invoke-ToolkitCheck 'idf.py' @('-C','firmware','-B',$toolkitBuild,'build')
        Invoke-ToolkitCheck 'idf.py' @('-C','firmware','-B',$toolkitBuild,'merge-bin','-o','nabo-toolkit-merged.bin')
        Invoke-ToolkitCheck 'python' @('firmware/tools/verify_firmware.py',$toolkitBuild)
        Invoke-ToolkitCheck 'python' @('tools/archive_firmware.py',$toolkitBuild)
    }
} finally { Pop-Location }
