$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $scriptDir "docker-compose.yml")) {
  Set-Location $scriptDir
} elseif (Test-Path (Join-Path (Split-Path $scriptDir -Parent) "docker-compose.yml")) {
  Set-Location (Split-Path $scriptDir -Parent)
} else {
  Write-Host "docker-compose.yml پیدا نشد. لطفاً این اسکریپت را از کنار مخزن اجرا کن." -ForegroundColor Red
  exit 1
}

Write-Host "Stopping and removing AION-OS Docker stack…" -ForegroundColor Yellow
docker compose down -v
Write-Host "✅ stack down & volumes removed." -ForegroundColor Green
