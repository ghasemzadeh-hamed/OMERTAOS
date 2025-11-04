Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location (Split-Path $MyInvocation.MyCommand.Path -Parent)
Set-Location ..

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .\shared\control

Set-Location .\shared\gateway
npm i
Write-Host "OK. Use: ..\scripts\run_windows.ps1"
