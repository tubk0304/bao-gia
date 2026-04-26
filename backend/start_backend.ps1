$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path ".env")) {
    Write-Host "Chua co file .env. Hay tao bang lenh: Copy-Item .env.example .env"
    exit 1
}

$existing = Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -in @("python.exe", "py.exe") -and
        $_.CommandLine -match "uvicorn" -and
        $_.CommandLine -match "main:app" -and
        $_.CommandLine -match "Bao_gia_nhanh\\backend"
    } |
    Select-Object -First 1

if ($existing) {
    Write-Host ("Backend dang chay san, PID " + $existing.ProcessId)
    Write-Host "Admin:  http://127.0.0.1:8000/admin"
    Write-Host "Bao gia: http://127.0.0.1:8000/baogia"
    Write-Host "Docs:   http://127.0.0.1:8000/docs"
    exit 0
}

$pythonExe = $null

foreach ($candidate in @(".\.venv312\Scripts\python.exe", ".\.venv\Scripts\python.exe")) {
    if (Test-Path $candidate) {
        $resolved = (Resolve-Path $candidate).Path
        try {
            & $resolved --version *> $null
            if ($LASTEXITCODE -eq 0) {
                $pythonExe = $resolved
                break
            }
        } catch {
            continue
        }
    }
}

if (-not $pythonExe) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $pythonExe = $pythonCmd.Source
    }
}

if (-not $pythonExe) {
    Write-Host "Khong tim thay Python de chay backend."
    Write-Host "Hay tao .venv312 moi bang .\create_venv.ps1 hoac cai dat Python 3.12 roi chay lai."
    exit 1
}

Write-Host ("Dang chay backend bang: " + $pythonExe)
Write-Host "Admin:  http://127.0.0.1:8000/admin"
Write-Host "Bao gia: http://127.0.0.1:8000/baogia"
Write-Host "Docs:   http://127.0.0.1:8000/docs"

& $pythonExe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
