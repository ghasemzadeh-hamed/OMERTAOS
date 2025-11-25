$ErrorActionPreference = 'Stop'

$ControlUrl = $env:CONTROL_HEALTH_URL
if (-not $ControlUrl) { $ControlUrl = 'http://localhost:8000/health' }
$GatewayUrl = $env:GATEWAY_HEALTH_URL
if (-not $GatewayUrl) { $GatewayUrl = 'http://localhost:3000/health' }
$ConsoleUrl = $env:CONSOLE_HEALTH_URL
if (-not $ConsoleUrl) { $ConsoleUrl = 'http://localhost:3001/health' }

Write-Host "Checking control plane health at $ControlUrl"
Invoke-WebRequest -UseBasicParsing $ControlUrl | Out-Null

Write-Host "Checking gateway health at $GatewayUrl"
Invoke-WebRequest -UseBasicParsing $GatewayUrl | Out-Null

if ($env:SKIP_CONSOLE_HEALTH -ne 'true') {
    Write-Host "Checking console availability at $ConsoleUrl"
    Invoke-WebRequest -UseBasicParsing $ConsoleUrl | Out-Null
}

Write-Host 'Smoke OK'
