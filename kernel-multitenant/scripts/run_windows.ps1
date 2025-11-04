Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $MyInvocation.MyCommand.Path -Parent | Split-Path
$profile = $env:PROFILE
if ([string]::IsNullOrEmpty($profile)) { $profile = "user" }

$gatewayEnv = Join-Path $root "shared/gateway/.env"
$controlEnv = Join-Path $root "shared/control/.env"
if (-not (Test-Path $gatewayEnv)) { Copy-Item (Join-Path $root "shared/gateway/.env.example") $gatewayEnv }
if (-not (Test-Path $controlEnv)) { Copy-Item (Join-Path $root "shared/control/.env.example") $controlEnv }

$content = Get-Content $controlEnv
$found = $false
for ($i = 0; $i -lt $content.Length; $i++) {
  if ($content[$i].StartsWith("PROFILE=")) {
    $content[$i] = "PROFILE=$profile"
    $found = $true
  }
}
if (-not $found) { $content += "PROFILE=$profile" }
Set-Content $controlEnv $content

if ($profile -eq "ent") {
  (Get-Content $gatewayEnv) | ForEach-Object { $_ -replace 'FEATURE_SEAL=0', 'FEATURE_SEAL=1' } | Set-Content $gatewayEnv
} else {
  (Get-Content $gatewayEnv) | ForEach-Object { $_ -replace 'FEATURE_SEAL=1', 'FEATURE_SEAL=0' } | Set-Content $gatewayEnv
}

Start-Process -NoNewWindow powershell -ArgumentList "-NoProfile","-Command","cd '$root/shared/control'; ..\.venv\Scripts\Activate.ps1; uvicorn core.chatops:app --factory --port 8010 --reload"
Start-Sleep -Seconds 1
Set-Location "$root/shared/gateway"
node --loader ts-node/esm src/server.ts
