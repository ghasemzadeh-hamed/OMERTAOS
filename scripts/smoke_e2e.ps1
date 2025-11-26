#!/usr/bin/env pwsh
param(
  [string]$GatewayUrl = $env:NEXT_PUBLIC_GATEWAY_URL,
  [string]$ControlUrl = $env:AION_CONTROL_BASE_URL,
  [string]$ConsoleUrl = $env:NEXTAUTH_URL
)

$gatewayPort = if ($env:AION_GATEWAY_PORT) { $env:AION_GATEWAY_PORT } else { '8080' }

if (-not $GatewayUrl) {
  $GatewayUrl = "http://localhost:$gatewayPort"
} elseif ($GatewayUrl -match '://(gateway|control|console|minio|postgres|redis|qdrant)(:|/|$)') {
  $GatewayUrl = "http://localhost:$gatewayPort"
}

if (-not $ControlUrl) {
  if ($env:NEXT_PUBLIC_CONTROL_URL) {
    $ControlUrl = $env:NEXT_PUBLIC_CONTROL_URL
  } else {
    $ControlUrl = 'http://localhost:8000'
  }
}

if (-not $ConsoleUrl) { $ConsoleUrl = 'http://localhost:3000' }

$apiKeyPair = if ($env:AION_GATEWAY_API_KEYS) { $env:AION_GATEWAY_API_KEYS } else { 'demo-key:admin|manager' }
$apiKey = $apiKeyPair.Split(':')[0]

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

$payload = '{"intent":"diagnostics","input":{"prompt":"ping"}}'
$response = Invoke-WebRequest -Uri "$GatewayUrl/v1/tasks" -Method Post -Headers @{ 'content-type' = 'application/json'; 'x-api-key' = $apiKey } -Body $payload -UseBasicParsing
$taskId = ($response.Content | ConvertFrom-Json).taskId
if (-not $taskId) { throw 'Failed to create task via gateway' }
Write-Host "Task created: $taskId"

for ($i = 0; $i -lt 60; $i++) {
  $statusResponse = Invoke-WebRequest -Uri "$GatewayUrl/v1/tasks/$taskId" -Headers @{ 'x-api-key' = $apiKey } -UseBasicParsing
  $statusJson = $statusResponse.Content | ConvertFrom-Json
  Write-Host ("status: {0}" -f $statusJson.status)
  if ($statusJson.status -in @('completed','failed')) { break }
  Start-Sleep -Seconds 5
}

try {
  $stream = Invoke-WebRequest -Uri "$GatewayUrl/v1/stream/$taskId" -Headers @{ 'x-api-key' = $apiKey } -UseBasicParsing
  if (-not $stream.Content) { throw 'Stream returned no content' }
  Write-Host ($stream.Content.Split("`n") | Select-Object -First 5)
} catch {
  Write-Warning "Failed to read stream: $($_.Exception.Message)"
}

Write-Host 'Smoke test completed'
