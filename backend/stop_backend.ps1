$ErrorActionPreference = "SilentlyContinue"

$targets = Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -in @("python.exe", "py.exe") -and
        $_.CommandLine -match "uvicorn" -and
        $_.CommandLine -match "main:app" -and
        $_.CommandLine -match "Bao_gia_nhanh\\backend"
    }

if (-not $targets) {
    Write-Host "Khong tim thay backend uvicorn dang chay."
    exit 0
}

$targets | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
    Write-Host ("Da dung process ID " + $_.ProcessId)
}
