$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path ".env")) {
    Write-Host "Chua co file .env. Hay tao bang lenh: Copy-Item .env.example .env"
    exit 1
}

$pythonExe = $null

foreach ($candidate in @(".\.venv\Scripts\python.exe", ".\.venv312\Scripts\python.exe")) {
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
    Write-Host "Hay tao .venv moi bang .\create_venv.ps1 hoac cai dat Python roi chay lai."
    exit 1
}

& $pythonExe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
