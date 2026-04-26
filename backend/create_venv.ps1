$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$pythonExe = $null
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue

foreach ($candidate in @(
    "C:\Users\Tubk\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Program Files\Python312\python.exe"
)) {
    if (Test-Path $candidate) {
        $pythonExe = $candidate
        break
    }
}

if (-not $pythonExe -and $pyLauncher) {
    try {
        & $pyLauncher.Source -3.12 --version *> $null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $pyLauncher.Source
        }
    } catch {
    }
}

if (-not $pythonExe) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        try {
            $versionOutput = & $pythonCmd.Source --version 2>&1
            if ($versionOutput -match "Python 3\.12") {
                $pythonExe = $pythonCmd.Source
            }
        } catch {
        }
    }
}

if (-not $pythonExe) {
    Write-Host "Khong tim thay Python 3.12 de tao moi truong."
    Write-Host "Can cai Python 3.12 hoac sua lai duong dan trong backend\\create_venv.ps1."
    exit 1
}

if (Test-Path ".\.venv312") {
    Write-Host "Da co san backend/.venv312"
    Write-Host "Neu muon tao lai, hay dung backend truoc va xoa thu muc .venv312 roi chay lai script nay."
    exit 0
}

if ($pyLauncher -and $pythonExe -eq $pyLauncher.Source) {
    & $pythonExe -3.12 -m venv .venv312
} else {
    & $pythonExe -m venv .venv312
}

Write-Host "Da tao virtualenv tai backend/.venv312"
Write-Host "Kich hoat bang lenh: .\.venv312\Scripts\Activate.ps1"
Write-Host "Cai goi bang lenh: .\.venv312\Scripts\python.exe -m pip install -r requirements.txt"
