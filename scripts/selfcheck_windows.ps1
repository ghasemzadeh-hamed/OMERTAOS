#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:ComposeCommand = $null

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
    if ($script:ComposeCommand) { return $script:ComposeCommand }

    $dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCommand) {
        Write-ErrorAndExit "Docker CLI not found. Install Docker Desktop with Compose v2."
    }

    $composeCheck = & $dockerCommand.Path @('compose', 'version') 2>&1
    if ($LASTEXITCODE -eq 0) {
        $script:ComposeCommand = @{ Exe = $dockerCommand.Path; PreArgs = @('compose'); Display = 'docker compose' }
        return $script:ComposeCommand
    }

    if (-not (Test-DockerDaemon)) {
        Write-ErrorAndExit "Docker daemon not reachable. Ensure Docker Desktop is running and WSL integration is enabled.`n$composeCheck"
    }

    $dockerCompose = Get-Command docker-compose -ErrorAction SilentlyContinue
    if ($dockerCompose) {
        Write-Warn 'Docker Compose v2 not detected; using docker-compose fallback.'
        $script:ComposeCommand = @{ Exe = $dockerCompose.Path; PreArgs = @(); Display = 'docker-compose' }
        return $script:ComposeCommand
    }

    Write-ErrorAndExit "Docker Compose v2 (docker compose) is required."
}

$psMajor = $PSVersionTable.PSVersion.Major
if ($psMajor -lt 5) {
    Write-ErrorAndExit "PowerShell 5.1 or newer is required. Current: $psMajor"
}
Write-Info "PowerShell version: $($PSVersionTable.PSVersion)"

if (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Info 'WSL detected (optional).'
} else {
    Write-Warn 'WSL not detected. Enable WSL and Docker Desktop integration for best results on Windows.'
}

$dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCommand) {
    Write-ErrorAndExit 'Docker CLI not found. Install Docker Desktop with Compose v2.'
}
Write-Info "Docker CLI detected: $($dockerCommand.Path)"

Test-DockerDaemon -ThrowOnFailure | Out-Null
Write-Info 'Docker daemon reachable.'

$compose = Resolve-ComposeCommand
Write-Info "Compose available via: $($compose.Display)"
