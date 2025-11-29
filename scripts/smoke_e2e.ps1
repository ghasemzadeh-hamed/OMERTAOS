#!/usr/bin/env pwsh
param(
  [string]$GatewayUrl = $env:NEXT_PUBLIC_GATEWAY_URL,
  [string]$ControlUrl = $env:NEXT_PUBLIC_CONTROL_URL,
  [string]$ConsoleUrl = $env:NEXTAUTH_URL
)

$gatewayPort = if ($env:AION_GATEWAY_PORT) { $env:AION_GATEWAY_PORT } else { '3000' }

if (-not $GatewayUrl) {
  $GatewayUrl = "http://localhost:$gatewayPort"
} elseif ($GatewayUrl -match '://(gateway|control|console|minio|postgres|redis|qdrant)(:|/|$)') {
  $GatewayUrl = "http://localhost:$gatewayPort"
}

if (-not $ControlUrl) { $ControlUrl = 'http://localhost:8000' }

if (-not $ConsoleUrl) { $ConsoleUrl = 'http://localhost:3000' }

$adminToken = if ($env:AION_GATEWAY_ADMIN_TOKEN) { $env:AION_GATEWAY_ADMIN_TOKEN } else { 'demo-admin-token' }

function Wait-ForService {
  param(
    [string]$Name,
    [string]$Url
  )
  Write-Host "Waiting for $Name at $Url"
  for ($i = 0; $i -lt 60; $i++) {
    try {
      $null = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
      Write-Host "$Name healthy"
      return
    } catch {
      Start-Sleep -Seconds 5
    }
  }
  throw "$Name did not become ready"
}


Wait-ForService -Name 'control' -Url "$ControlUrl/healthz"
Wait-ForService -Name 'gateway' -Url "$GatewayUrl/healthz"
Wait-ForService -Name 'console' -Url "$ConsoleUrl/healthz"
Invoke-WebRequest -Uri "$ConsoleUrl/dashboard/health/api" -UseBasicParsing -TimeoutSec 10 | Out-Null

if ($adminToken) {
  Invoke-WebRequest -Uri "$GatewayUrl/healthz/auth" -Headers @{ 'x-aion-admin-token' = $adminToken } -UseBasicParsing -TimeoutSec 10 | Out-Null
}

Write-Host 'Smoke test completed'
