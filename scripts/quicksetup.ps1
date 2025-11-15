#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

param(
    [string]$Profile,
    [switch]$Local,
    [switch]$NonInteractive,
    [string]$ComposeFile,
    [string]$Model = $env:AIONOS_LOCAL_MODEL,
    [switch]$Update,
    [string]$Repo = $env:AIONOS_REPO_URL,
    [string]$Branch = $env:AIONOS_REPO_BRANCH,
    [string]$PolicyDir = $env:AION_POLICY_DIR,
    [string]$VolumeRoot = $env:AION_VOLUME_ROOT
)

if (-not $Model) { $Model = 'llama3.2:3b' }
if (-not $Repo) { $Repo = 'https://github.com/Hamedghz/OMERTAOS.git' }
if (-not $Branch) { $Branch = 'main' }
if (-not $PolicyDir) { $PolicyDir = './policies' }
if (-not $VolumeRoot) { $VolumeRoot = './volumes' }

function Write-Info([string]$Message) { Write-Host "[INFO] $Message" }
function Write-Warn([string]$Message) { Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-ErrorAndExit([string]$Message) { Write-Host "[ERROR] $Message" -ForegroundColor Red; exit 1 }

function Require-Command {
    param([string]$Name, [string]$Hint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        if ($Hint) {
            Write-ErrorAndExit "Required command '$Name' not found. $Hint"
        } else {
            Write-ErrorAndExit "Required command '$Name' not found."
        }
    }
}

Require-Command git "Install Git from https://git-scm.com/downloads"
Require-Command docker "Install Docker Desktop or Engine with Compose support"
if (-not (Get-Command curl -ErrorAction SilentlyContinue) -and -not (Get-Command wget -ErrorAction SilentlyContinue)) {
    Write-ErrorAndExit "Either 'curl' or 'wget' must be available."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Resolve-Path (Join-Path $scriptDir '..')
$envPath = Join-Path $rootDir '.env'
$configDir = Join-Path $rootDir 'config'
$configFile = Join-Path $configDir 'aionos.config.yaml'
$profileDir = Join-Path $rootDir '.aionos'
$resolveUnderRoot = {
    param([string]$Root, [string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $Root }
    if ([System.IO.Path]::IsPathRooted($Path)) { return $Path }
    $trimmed = $Path -replace '^[.][\\/]', ''
    return Join-Path $Root $trimmed
}
$policyPath = & $resolveUnderRoot $rootDir $PolicyDir
$volumePath = & $resolveUnderRoot $rootDir $VolumeRoot
$telemetryRaw = if ($env:AION_TELEMETRY_OPT_IN) { $env:AION_TELEMETRY_OPT_IN } else { 'false' }
$telemetryEndpoint = if ($env:AION_TELEMETRY_ENDPOINT) { $env:AION_TELEMETRY_ENDPOINT } else { 'http://localhost:4317' }

if ((Test-Path (Join-Path $rootDir '.git')) -and $Update.IsPresent) {
    Write-Info "Updating repository ($Branch)"
    Push-Location $rootDir
    git fetch --all | Out-Null
    git checkout $Branch | Out-Null
    git pull --ff-only origin $Branch | Out-Null
    Pop-Location
}

if (-not (Test-Path (Join-Path $rootDir '.git'))) {
    Write-Warn "Git metadata not found at $rootDir."
    $parent = Split-Path $rootDir -Parent
    $target = Join-Path $parent 'OMERTAOS'
    if ($target -ne $rootDir) {
        Write-Info "Cloning repository into $target"
        git clone --branch $Branch --single-branch $Repo $target | Out-Null
        $rootDir = Resolve-Path $target
        $envPath = Join-Path $rootDir '.env'
        $configDir = Join-Path $rootDir 'config'
        $configFile = Join-Path $configDir 'aionos.config.yaml'
        $profileDir = Join-Path $rootDir '.aionos'
    } else {
        Write-Warn "Running from archive snapshot; skipping clone."
    }
}

if (-not (Test-Path $configDir)) { New-Item -ItemType Directory -Force -Path $configDir | Out-Null }
if (-not (Test-Path $profileDir)) { New-Item -ItemType Directory -Force -Path $profileDir | Out-Null }
if (-not (Test-Path $policyPath)) { New-Item -ItemType Directory -Force -Path $policyPath | Out-Null; Write-Info "Created policy directory at $policyPath" }
if (-not (Test-Path $volumePath)) { New-Item -ItemType Directory -Force -Path $volumePath | Out-Null; Write-Info "Created volume root at $volumePath" }
Write-Info "Policy directory: $policyPath"
Write-Info "Volume root: $volumePath"

$envTemplates = @(
    (Join-Path $rootDir '.env.example'),
    (Join-Path $rootDir 'config/templates/.env.example'),
    (Join-Path $rootDir 'config/.env.example')
)
if (-not (Test-Path $envPath)) {
    $template = $null
    foreach ($candidate in $envTemplates) {
        if (Test-Path $candidate) {
            $template = $candidate
            break
        }
    }

    if ($template) {
        try {
            $relative = [System.IO.Path]::GetRelativePath($rootDir, $template)
        } catch {
            $relative = Split-Path $template -Leaf
        }
        Write-Info "Creating .env from template $relative"
        Copy-Item $template $envPath
    } else {
        Write-Warn "No .env template found; creating empty .env"
        New-Item -ItemType File -Path $envPath | Out-Null
    }
}

function Normalize-Profile([string]$Value) {
    switch ($Value.ToLowerInvariant()) {
        'user' { return 'user' }
        'basic' { return 'user' }
        'professional' { return 'professional' }
        'pro' { return 'professional' }
        'enterprise' { return 'enterprise-vip' }
        'enterprise-vip' { return 'enterprise-vip' }
        'enterprise_vip' { return 'enterprise-vip' }
        'enterprisevip' { return 'enterprise-vip' }
        default { Write-ErrorAndExit "Unknown profile '$Value'." }
    }
}

if (-not $Profile) {
    if ($NonInteractive) {
        if ($env:AION_PROFILE) {
            $Profile = Normalize-Profile $env:AION_PROFILE
        } elseif ($env:AION_PROFILE_CHOICE) {
            switch ($env:AION_PROFILE_CHOICE) {
                '2' { $Profile = 'professional' }
                '3' { $Profile = 'enterprise-vip' }
                default { $Profile = 'user' }
            }
        } else {
            $Profile = 'user'
        }
    } else {
        Write-Host ''
        Write-Host 'Select AION-OS profile:'
        Write-Host '  1) user           - Quickstart, local-only, minimal resources'
        Write-Host '  2) professional   - Explorer + Terminal + IoT-ready'
        Write-Host '  3) enterprise-vip - SEAL, GPU, advanced routing'
        $choice = Read-Host 'Enter 1-3 [1]'
        switch ($choice) {
            '2' { $Profile = 'professional' }
            '3' { $Profile = 'enterprise-vip' }
            default { $Profile = 'user' }
        }
    }
} else {
    $Profile = Normalize-Profile $Profile
}

Write-Info "Selected profile: $Profile"

if (-not $ComposeFile) {
    if ($Local) {
        $ComposeFile = 'docker-compose.local.yml'
    } else {
        $ComposeFile = 'docker-compose.yml'
    }
}

function Set-EnvValues {
    param([string]$Path, [hashtable]$Values)
    $existing = @()
    if (Test-Path $Path) {
        $existing = Get-Content $Path
    }
    $output = New-Object System.Collections.Generic.List[string]
    foreach ($line in $existing) {
        if (-not $line -or $line.TrimStart().StartsWith('#') -or -not $line.Contains('=')) {
            $output.Add($line)
            continue
        }
        $key = $line.Split('=')[0]
        if (-not $Values.ContainsKey($key)) {
            $output.Add($line)
        }
    }
    foreach ($key in $Values.Keys) {
        $output.Add("$key=$($Values[$key])")
    }
    $output.Add('')
    Set-Content -Path $Path -Value $output -Encoding UTF8
}

$telemetryEnabled = @('1','true','y','yes').Contains($telemetryRaw.ToLowerInvariant())
$envUpdates = @{}
$envUpdates['AION_PROFILE'] = $Profile
$envUpdates['FEATURE_SEAL'] = if ($Profile -eq 'enterprise-vip') { '1' } else { '0' }
$envUpdates['AION_TELEMETRY_OPT_IN'] = if ($telemetryEnabled) { 'true' } else { 'false' }
$envUpdates['AION_TELEMETRY_ENDPOINT'] = $telemetryEndpoint
$envUpdates['AION_POLICY_DIR'] = $PolicyDir
$envUpdates['AION_VOLUME_ROOT'] = $VolumeRoot
Set-EnvValues -Path $envPath -Values $envUpdates

$profileFile = Join-Path $profileDir 'profile.json'
$profileObject = [ordered]@{
    profile = $Profile
    setupDone = $true
    updatedAt = (Get-Date -AsUTC).ToString('yyyy-MM-ddTHH:mm:ssZ')
}
$profileJson = $profileObject | ConvertTo-Json -Depth 4
Set-Content -Path $profileFile -Value $profileJson -Encoding UTF8

if (-not (Test-Path $configFile)) {
    @"
version: 1
locale: en-US
console:
  port: 3000
  baseUrl: http://localhost:3000
gateway:
  port: 8080
  apiKeys:
    - demo-key:admin|manager
control:
  httpPort: 8000
  grpcPort: 50051
storage:
  postgres:
    host: postgres
    port: 5432
    user: aion
    password: aion
    database: aion
  redis:
    host: redis
    port: 6379
  qdrant:
    host: qdrant
    port: 6333
  minio:
    endpoint: http://minio:9000
    accessKey: minio
    secretKey: miniosecret
    bucket: aion-raw
policies:
  dir: "$PolicyDir"
volumes:
  root: "$VolumeRoot"
telemetry:
  otelEnabled: $($envUpdates['AION_TELEMETRY_OPT_IN'])
  endpoint: "$telemetryEndpoint"
"@ | Set-Content -Path $configFile -Encoding UTF8
}

function Invoke-Compose {
    param([string[]]$ComposeArgs)
    $composev2 = $false
    try {
        & docker compose version *> $null
        if ($LASTEXITCODE -eq 0) { $composev2 = $true }
    } catch { $composev2 = $false }
    if ($composev2) {
        & docker compose @ComposeArgs
        return
    }
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        & docker-compose @ComposeArgs
        return
    }
    Write-ErrorAndExit 'Docker Compose v2 or docker-compose is required.'
}

$composePath = Join-Path $rootDir $ComposeFile
if (-not (Test-Path $composePath)) {
    Write-ErrorAndExit "Compose file '$ComposeFile' not found in $rootDir."
}

Write-Info "Starting services with compose file $ComposeFile"
$attempt = 1
while ($attempt -le 3) {
    try {
        Push-Location $rootDir
        Invoke-Compose -ComposeArgs @('-f', $ComposeFile, 'up', '-d', '--build')
        Pop-Location
        break
    } catch {
        Pop-Location
        if ($attempt -ge 3) { throw }
        Write-Warn "docker compose attempt $attempt failed; retrying"
        Start-Sleep -Seconds ($attempt * 5)
        $attempt += 1
    }
}

if ($Model) {
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        try {
            $models = ollama list 2>$null
            if (-not ($models -match [regex]::Escape($Model))) {
                Write-Info "Pulling Ollama model $Model"
                ollama pull $Model | Out-Null
            }
        } catch {
            Write-Warn "Ollama pull for $Model failed: $($_.Exception.Message)"
        }
    } else {
        Write-Warn "Ollama CLI not found; skipping local model pull"
    }
}

Write-Host ''
Write-Host '[AION-OS] QuickSetup completed.'
Write-Host "Profile: $Profile"
Write-Host "Compose file: $ComposeFile"
if ($Local) {
    Write-Host 'Services:'
    Write-Host '  Kernel API:       http://localhost:8010'
    Write-Host '  Gateway (REST):   http://localhost:8080'
    Write-Host '  Console UI:       http://localhost:3000'
} else {
    Write-Host 'Next steps:'
    Write-Host "  - Monitor stack: docker compose -f $ComposeFile ps"
    Write-Host '  - Smoke test: scripts/smoke_e2e.ps1'
}
