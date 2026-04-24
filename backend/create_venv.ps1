$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$pythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonExe) {
    Write-Host "Khong tim thay lenh python tren PATH."
    Write-Host "Hay cai dat Python ban desktop hoac sua lai virtualenv local roi thu lai."
    exit 1
}

& $pythonExe.Source -m venv .venv
Write-Host "Da tao virtualenv tai backend/.venv"
Write-Host "Kich hoat bang lenh: .\.venv\Scripts\Activate.ps1"
