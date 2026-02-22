#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

param(
    [string]$ComposeFile = 'docker-compose.yml',
    [int]$Retries = 40,
    [int]$DelaySeconds = 5,
    [switch]$NoBuild
)

function Write-Info([string]$Message) { Write-Host "[INFO] $Message" }
function Write-Warn([string]$Message) { Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-ErrorAndExit([string]$Message) { Write-Host "[ERROR] $Message" -ForegroundColor Red; exit 1 }

function Test-DockerDaemon {
    param([switch]$ThrowOnFailure)

    $dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCommand) {
        if ($ThrowOnFailure) { Write-ErrorAndExit "Docker CLI not found. Install Docker Desktop with Compose v2." }
        return $false
    }

    try {
        $output = & $dockerCommand.Path info --format '{{.ServerVersion}}' 2>&1
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($output)) { return $true }
        if ($ThrowOnFailure) {
            Write-ErrorAndExit "Docker daemon not reachable. Ensure Docker Desktop is running and WSL integration is enabled.`n$output"
        }
    } catch {
        if ($ThrowOnFailure) {
            Write-ErrorAndExit "Docker daemon not reachable. Ensure Docker Desktop is running and WSL integration is enabled. $($_.Exception.Message)"
        }
    }

    return $false
}

function Resolve-ComposeCommand {
    $dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCommand) {
        Write-ErrorAndExit "Docker is required for smoke tests. Install Docker Desktop with Compose v2."
    }

    $composeCheck = & $dockerCommand.Path @('compose', 'version') 2>&1
    if ($LASTEXITCODE -eq 0) {
        return @{ Exe = $dockerCommand.Path; PreArgs = @('compose'); Display = 'docker compose' }
    }

    if (-not (Test-DockerDaemon)) {
        Write-ErrorAndExit "Docker daemon not reachable. Ensure Docker Desktop is running and WSL integration is enabled.`n$composeCheck"
    }

    $dockerCompose = Get-Command docker-compose -ErrorAction SilentlyContinue
    if ($dockerCompose) {
        Write-Warn "Docker Compose v2 not detected; using docker-compose fallback."
        return @{ Exe = $dockerCompose.Path; PreArgs = @(); Display = 'docker-compose' }
    }

    Write-ErrorAndExit "Docker Compose v2 (docker compose) is required."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Resolve-Path (Join-Path $scriptDir '..')
Set-Location -Path $rootDir

$compose = Resolve-ComposeCommand

$composePath = Join-Path $rootDir $ComposeFile
if (-not (Test-Path $composePath)) {
    Write-ErrorAndExit "Compose file '$ComposeFile' not found in $rootDir."
}

$controlHealth = if ($env:CONTROL_HEALTH_URL) { $env:CONTROL_HEALTH_URL } else { 'http://localhost:8000/healthz' }
$gatewayHealth = if ($env:GATEWAY_HEALTH_URL) { $env:GATEWAY_HEALTH_URL } else { 'http://localhost:8080/health' }
$consoleHealth = if ($env:CONSOLE_HEALTH_URL) { $env:CONSOLE_HEALTH_URL } else { 'http://localhost:3000/health' }

function Invoke-Compose {
    param([string[]]$Args)

    $allArgs = @()
    if ($compose.PreArgs) { $allArgs += $compose.PreArgs }
    if ($Args) { $allArgs += $Args }
    $commandLine = "$($compose.Exe) " + ($allArgs -join ' ')

    Write-Info "Executing compose command: $commandLine"
    $output = & $compose.Exe @allArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        $lines = $output -split "`n" | Select-Object -First 80
        Write-Host "[ERROR] Compose command failed: $commandLine" -ForegroundColor Red
        if ($lines) { Write-Host ($lines -join "`n") -ForegroundColor Red }
        throw "Compose command failed with exit code $LASTEXITCODE"
    }

    return $output
}

function Start-Stack {
    $args = @('-f', $ComposeFile, 'up', '-d')
    if (-not $NoBuild) {
        $args += '--build'
    }

    Write-Info "Starting services with $($compose.Display) -f $ComposeFile"
    Invoke-Compose -Args $args
}

function Show-Diagnostics {
    Write-Warn 'Collecting diagnostics'
    try { Invoke-Compose -Args @('-f', $ComposeFile, 'ps') } catch { Write-Warn "compose ps failed: $($_.Exception.Message)" }
    try { Invoke-Compose -Args @('-f', $ComposeFile, 'logs', '--tail', '200') } catch { Write-Warn "compose logs failed: $($_.Exception.Message)" }
}

function Wait-ForHealth {
    param(
        [string]$Url,
        [string]$Label
    )

    for ($i = 1; $i -le $Retries; $i++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 10
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
                Write-Info "[$Label] healthy at $Url"
                return
            }
        } catch {
            Start-Sleep -Seconds $DelaySeconds
            continue
        }
        Start-Sleep -Seconds $DelaySeconds
    }

    Write-ErrorAndExit "[$Label] did not become healthy at $Url after $Retries attempts"
}

Start-Stack

try {
    Wait-ForHealth -Url $controlHealth -Label 'control'
    Wait-ForHealth -Url $gatewayHealth -Label 'gateway'
    if ($env:SKIP_CONSOLE_HEALTH -ne 'true') {
        Wait-ForHealth -Url $consoleHealth -Label 'console'
    } else {
        Write-Warn 'Skipping console health check because SKIP_CONSOLE_HEALTH=true'
    }

    Write-Host ''
    Write-Info 'Smoke checks passed.'
    Write-Info "Control : $controlHealth"
    Write-Info "Gateway : $gatewayHealth"
    Write-Info "Console : $consoleHealth"
} catch {
    Show-Diagnostics
    throw
}
