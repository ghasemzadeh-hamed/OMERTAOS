#!/usr/bin/env pwsh
param(
    [string]$Profile,
    [switch]$Local,
    [switch]$NonInteractive,
    [string]$ComposeFile,
    [string]$Model = $env:AION_LOCAL_MODEL,
    [switch]$Update,
    [string]$Repo = $env:AION_REPO_URL,
    [string]$Branch = $env:AION_REPO_BRANCH,
    [string]$PolicyDir = $env:AION_POLICY_DIR,
    [string]$VolumeRoot = $env:AION_VOLUME_ROOT,
    [switch]$SkipSelfCheck
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:ComposeCommand = $null
$script:IsWindowsPlatform = $null

function Write-Info([string]$Message) { Write-Host "[INFO] $Message" }
function Write-Warn([string]$Message) { Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-ErrorAndExit([string]$Message) { Write-Host "[ERROR] $Message" -ForegroundColor Red; exit 1 }

function Resolve-PathSafe {
    param([string]$Path)
    try { return Resolve-Path $Path -ErrorAction Stop } catch { return $Path }
}

function Resolve-RepoRoot {
    param([string]$ScriptDir)

    $resolvedScriptDir = Resolve-PathSafe $ScriptDir
    $candidate = $resolvedScriptDir
    while ($candidate -and (Test-Path $candidate)) {
        if (Test-Path (Join-Path $candidate '.git')) { break }
        $parent = Split-Path $candidate -Parent
        if (-not $parent -or $parent -eq $candidate) { break }
        $candidate = $parent
    }

    if (-not (Test-Path (Join-Path $candidate '.git'))) {
        $candidate = Resolve-PathSafe (Join-Path $resolvedScriptDir '..')
    }

    $leaf = Split-Path $candidate -Leaf
    $parentLeaf = Split-Path (Split-Path $candidate -Parent) -Leaf
    if ($leaf -eq 'OMERTAOS' -and $parentLeaf -eq 'OMERTAOS') {
        $higher = Split-Path $candidate -Parent
        if (Test-Path (Join-Path $higher '.git')) {
            Write-Warn "Detected nested OMERTAOS directory. Using parent '$higher' as repository root."
            $candidate = $higher
        } else {
            Write-Warn "Detected nested OMERTAOS directory ($candidate). Continuing with current path."
        }
    }

    return Resolve-PathSafe $candidate
}

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
        $script:ComposeCommand = [PSCustomObject]@{ ExePath = $dockerCommand.Path; PreArgs = @('compose'); Display = 'docker compose' }
        return $script:ComposeCommand
    }

    if (-not (Test-DockerDaemon)) {
        Write-ErrorAndExit "Docker daemon not reachable. Ensure Docker Desktop is running and WSL integration is enabled.`n$composeCheck"
    }

    $dockerCompose = Get-Command docker-compose -ErrorAction SilentlyContinue
    if ($dockerCompose) {
        Write-Warn 'Docker Compose v2 not detected; using docker-compose fallback.'
        $script:ComposeCommand = [PSCustomObject]@{ ExePath = $dockerCompose.Path; PreArgs = @(); Display = 'docker-compose' }
        return $script:ComposeCommand
    }

    Write-ErrorAndExit "Docker Compose v2 (docker compose) is required."
}

function Assert-ComposeArgsContainsUp {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComposeArgsToValidate
    )

    if (-not $ComposeArgsToValidate -or $ComposeArgsToValidate.Count -eq 0) {
        $scope = $MyInvocation.MyCommand.Name
        $caller = if ($MyInvocation.InvocationName) { $MyInvocation.InvocationName } else { 'Assert-ComposeArgsContainsUp' }
        $joined = ($ComposeArgsToValidate -join ' ')
        throw "Compose arguments cannot be empty (scope=$scope, caller=$caller). Provided: '$joined'"
    }

    $hasUp = $false
    foreach ($arg in $ComposeArgsToValidate) {
        if ($arg -eq 'up') { $hasUp = $true; break }
        if (($arg -is [string]) -and ($arg -match '(?<!\S)up(?!\S)')) { $hasUp = $true; break }
    }

    if (-not $hasUp) {
        $joined = ($ComposeArgsToValidate -join ' ')
        throw "Invalid compose arguments; ComposeArgs must include the 'up' subcommand. Provided: '$joined'"
    }
}

function Invoke-Compose {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComposeCommandArgs
    )

    if (-not $ComposeCommandArgs -or $ComposeCommandArgs.Count -eq 0) {
        $joined = ($ComposeCommandArgs -join ' ')
        throw "Compose arguments cannot be empty. Provided: '$joined'"
    }

    $command = Resolve-ComposeCommand

    $allArgs = @()
    if ($command.PreArgs) { $allArgs += $command.PreArgs }
    $allArgs += $ComposeCommandArgs

    $commandLine = "$($command.ExePath) " + ($allArgs -join ' ')
    Write-Info "Executing compose: $commandLine"
    Write-Debug "Compose executable: $($command.ExePath)"
    Write-Debug "Compose pre-args: $($command.PreArgs -join ' ')"
    Write-Debug "Compose command args: $($ComposeCommandArgs -join ' ')"

    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
      $output = & $command.ExePath @allArgs 2>&1 | Out-String
      $exit = $LASTEXITCODE
    } finally {
      $ErrorActionPreference = $prevEAP
    }

    if ($exit -ne 0) {
      Write-Error "docker compose failed (exit=$exit). Output:`n$output"
      throw "docker compose failed with exit code $exit"
    }

    return $output

}

function Convert-ComposePsOutput {
    param([string[]]$Output)

    if (-not $Output) { return @() }
    if ($Output -is [string]) { $Output = $Output -split "`r?`n" }

    $joined = ($Output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join "`n"

    try {
        $raw = @($joined | ConvertFrom-Json)
        $parsed = @()
        foreach ($entry in $raw) {
            $state = $entry.State
            $health = $entry.Health
            if (-not $health -and $state -and ($state -match 'health:\s*(?<status>\w+)')) {
                $health = $Matches.status
                $state = ($state -replace "\s*\(health:.*", '').Trim()
            }
            if (-not $health -and $entry.Status -and ($entry.Status -match 'health:\s*(?<status>\w+)')) {
                $health = $Matches.status
            }
            $serviceName = if ($entry.Service) { $entry.Service } elseif ($entry.Name) { $entry.Name } else { $null }
            $parsed += [PSCustomObject]@{
                Service = $serviceName
                Name    = if ($entry.Name) { $entry.Name } else { $serviceName }
                State   = $state
                Health  = $health
            }
        }
        return $parsed
    } catch {
        $parsed = @()
        foreach ($line in $Output) {
            if ($line -match "^(?<name>[^\s]+)\s+(?<maybeCommand>\S+\s+)?(?<service>[^\s]+)\s+(?<state>running|exited|restarting|paused|created)(?:\s+\(health:\s*(?<health>\w+)\))?") {
                $parsed += [PSCustomObject]@{
                    Service = $Matches.service
                    Name    = $Matches.name
                    State   = $Matches.state
                    Health  = $Matches.health
                }
            } elseif ($line -match "^(?<name>[^\s]+)\s+(?<state>running|exited|restarting)(?:\s+\(health:\s*(?<health>\w+)\))?") {
                $parsed += [PSCustomObject]@{
                    Service = $Matches.name
                    Name    = $Matches.name
                    State   = $Matches.state
                    Health  = $Matches.health
                }
            }
        }
        return $parsed
    }
}

function Test-ComposeServicesRunning {
    param([array]$Services, [string[]]$Required)

    foreach ($name in $Required) {
        $candidate = $Services | Where-Object { $_.Service -eq $name -or $_.Name -like "*_${name}_*" -or $_.Name -like "*${name}*" }
        if (-not $candidate) { return $false }
        $stateText = ($candidate | Select-Object -First 1).State
        if (-not $stateText -or ($stateText -notmatch 'running')) { return $false }
    }
    return $true
}

function Get-ComposeServices {
    param(
        [string]$ComposeFile
    )

    $psArgs = @('-f', $ComposeFile, 'ps', '--format', 'json')
    try {
        $output = Invoke-Compose -ComposeCommandArgs $psArgs
        $parsed = Convert-ComposePsOutput -Output $output
        if ($parsed -and $parsed.Count -gt 0) { return $parsed }
    } catch {
        Write-Warn "compose ps --format json failed; falling back to text parse ($($_.Exception.Message))"
    }

    $fallbackOutput = Invoke-Compose -ComposeCommandArgs @('-f', $ComposeFile, 'ps')
    return Convert-ComposePsOutput -Output $fallbackOutput
}

function Get-RequiredServices {
    param([string]$Profile)

    $services = @('postgres', 'redis', 'minio', 'qdrant', 'control', 'gateway', 'console')
    if ($Profile -eq 'enterprise-vip') { $services += 'vault' }
    return $services
}

function Wait-ComposeReady {
    param(
        [string]$ComposeFile,
        [string]$Profile,
        [int]$TimeoutSeconds = 180,
        [int]$DelaySeconds = 3
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $required = Get-RequiredServices -Profile $Profile

    while ((Get-Date) -lt $deadline) {
        $services = Get-ComposeServices -ComposeFile $ComposeFile
        $allReady = $true

        foreach ($name in $required) {
            $candidate = $services | Where-Object { $_.Service -eq $name -or $_.Name -like "*_${name}_*" -or $_.Name -like "*${name}*" }
            if (-not $candidate) { $allReady = $false; break }
            $entry = $candidate | Select-Object -First 1
            $state = $entry.State
            $health = $entry.Health

            if ($state -match 'exited|dead') {
                throw "Service '$name' exited (state=$state)."
            }

            if ($health -and ($health -match 'unhealthy')) {
                throw "Service '$name' reported unhealthy."
            }

            if (-not ($state -match 'running')) {
                $allReady = $false
                break
            }

            if ($health -and ($health -match 'starting')) {
                $allReady = $false
                break
            }
        }

        if ($allReady) { return $true }
        Start-Sleep -Seconds $DelaySeconds
    }

    Write-Warn "Compose stack did not become ready within ${TimeoutSeconds}s. Dumping compose status and recent logs."
    Invoke-Compose -ComposeCommandArgs @('-f', $ComposeFile, 'ps') | ForEach-Object { Write-Host $_ }
    Invoke-Compose -ComposeCommandArgs @('-f', $ComposeFile, 'logs', '--tail', '200') | ForEach-Object { Write-Host $_ }
    throw "Compose services were not ready before timeout."
}

function Wait-HttpReady {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 120,
        [int]$DelaySeconds = 2
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -MaximumRedirection 3 -TimeoutSec 15
            if ($response.StatusCode -in 200, 302) { return $true }
        } catch {
            Start-Sleep -Seconds $DelaySeconds
            continue
        }
        Start-Sleep -Seconds $DelaySeconds
    }

    return $false
}

function Invoke-SelfCheck {
    param([string]$ScriptDir)

    $selfCheckPath = Join-Path $ScriptDir 'selfcheck_windows.ps1'
    if (-not (Test-Path $selfCheckPath)) { return }

    Write-Info 'Running environment self-checks'
    & $selfCheckPath
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Resolve-RepoRoot -ScriptDir $scriptDir

if (-not $Model) { $Model = 'llama3.2:3b' }
if (-not $Repo) { $Repo = 'https://github.com/Hamedghz/OMERTAOS.git' }
if (-not $Branch) { $Branch = 'main' }
if (-not $PolicyDir) { $PolicyDir = './policies' }
if (-not $VolumeRoot) { $VolumeRoot = './volumes' }

if (-not $SkipSelfCheck) { Invoke-SelfCheck -ScriptDir $scriptDir }

Require-Command git "Install Git from https://git-scm.com/downloads"
Require-Command docker "Install Docker Desktop or Engine with Compose support"
if (-not (Get-Command curl -ErrorAction SilentlyContinue) -and -not (Get-Command wget -ErrorAction SilentlyContinue)) {
    Write-ErrorAndExit "Either 'curl' or 'wget' must be available."
}

Test-DockerDaemon -ThrowOnFailure | Out-Null

$envPath = Join-Path $rootDir '.env'
$configDir = Join-Path $rootDir 'config'
$configFile = Join-Path $configDir 'aion.config.yaml'
$profileDir = Join-Path $rootDir '.aion'
$resolveUnderRoot = {
    param([string]$Root, [string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $Root }
    if ([System.IO.Path]::IsPathRooted($Path)) { return $Path }
    $trimmed = $Path -replace '^[.][\\/]', ''
    return Join-Path $Root $trimmed
}
function New-RandomSecret {
    param([int]$Bytes = 32)
    $buffer = New-Object byte[] $Bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($buffer)
    return [System.Convert]::ToBase64String($buffer)
}

$defaultDbUser = 'aion'
$defaultDbPassword = 'password'
$defaultDbName = 'omerta_db'
$defaultDbUrl = "postgresql://${defaultDbUser}:${defaultDbPassword}@postgres:5432/${defaultDbName}?schema=public"
$telemetryEndpoint = if ($env:AION_TELEMETRY_ENDPOINT) { $env:AION_TELEMETRY_ENDPOINT } else { 'http://localhost:4317' }

function Test-ProjectRootPath {
    param([string]$Path)
    return (Test-Path (Join-Path $Path 'docker-compose.yml')) -and (Test-Path (Join-Path $Path 'control')) -and (Test-Path (Join-Path $Path 'gateway')) -and (Test-Path (Join-Path $Path 'console'))
}

$hasProjectStructure = Test-ProjectRootPath -Path $rootDir

if ((Test-Path (Join-Path $rootDir '.git')) -and $Update.IsPresent) {
    Write-Info "Updating repository ($Branch)"
    Push-Location $rootDir
    git fetch --all | Out-Null
    git checkout $Branch | Out-Null
    git pull --ff-only origin $Branch | Out-Null
    Pop-Location
}

if ((-not (Test-Path (Join-Path $rootDir '.git'))) -and (-not $hasProjectStructure)) {
    Write-Warn "Git metadata not found at $rootDir."
    $parent = Split-Path $rootDir -Parent
    $target = Join-Path $parent 'OMERTAOS'
    if ($target -ne $rootDir) {
        Write-Info "Cloning repository into $target"
        git clone --branch $Branch --single-branch $Repo $target | Out-Null
        $rootDir = Resolve-PathSafe $target
    } else {
        Write-Warn "Running from archive snapshot; skipping clone."
    }
}

# Refresh derived paths after any clone or detection update
$envPath = Join-Path $rootDir '.env'
$configDir = Join-Path $rootDir 'config'
$configFile = Join-Path $configDir 'aion.config.yaml'
$profileDir = Join-Path $rootDir '.aion'
$hasProjectStructure = Test-ProjectRootPath -Path $rootDir
Set-Location -Path $rootDir

$policyPath = & $resolveUnderRoot $rootDir $PolicyDir
$volumePath = & $resolveUnderRoot $rootDir $VolumeRoot

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
        $ComposeFile = 'deploy/compose/docker-compose.local.yml'
    } else {
        $ComposeFile = 'docker-compose.yml'
    }
}

$gatewayApiKeys = if ($env:AION_GATEWAY_API_KEYS) { $env:AION_GATEWAY_API_KEYS } else { 'local-key:admin|manager' }
$gatewayAdminToken = if ($env:AION_GATEWAY_ADMIN_TOKEN) { $env:AION_GATEWAY_ADMIN_TOKEN } else { '' }
$adminToken = if ($env:AION_ADMIN_TOKEN) { $env:AION_ADMIN_TOKEN } else { '' }
$nextAuthSecret = if ($env:NEXTAUTH_SECRET) { $env:NEXTAUTH_SECRET } else { '' }
$consoleAdminEmail = if ($env:CONSOLE_ADMIN_EMAIL) { $env:CONSOLE_ADMIN_EMAIL } else { 'admin@local' }
$consoleAdminPassword = if ($env:CONSOLE_ADMIN_PASSWORD) { $env:CONSOLE_ADMIN_PASSWORD } else { 'admin123' }
$telemetryChoice = if ($env:AION_TELEMETRY_OPT_IN) { $env:AION_TELEMETRY_OPT_IN } else { 'false' }
$databaseUrl = if ($env:DATABASE_URL) { $env:DATABASE_URL } else { $defaultDbUrl }

if (-not $NonInteractive) {
    $inputAdminToken = Read-Host 'Enter AION_GATEWAY_ADMIN_TOKEN (leave empty to auto-generate)'
    if ([string]::IsNullOrWhiteSpace($inputAdminToken)) { $gatewayAdminToken = New-RandomSecret 32 } else { $gatewayAdminToken = $inputAdminToken }
    $adminToken = $gatewayAdminToken

    $inputApiKeys = Read-Host 'Enter AION_GATEWAY_API_KEYS (format: key:role1|role2, default: local-key:admin|manager)'
    if (-not [string]::IsNullOrWhiteSpace($inputApiKeys)) { $gatewayApiKeys = $inputApiKeys }

    $inputNextAuthSecret = Read-Host 'Enter NEXTAUTH_SECRET (leave empty to auto-generate)'
    if ([string]::IsNullOrWhiteSpace($inputNextAuthSecret)) { $nextAuthSecret = New-RandomSecret 48 } else { $nextAuthSecret = $inputNextAuthSecret }

    $telemetryAnswer = Read-Host 'Allow anonymous telemetry? (y/N)'
    $telemetryChoice = $telemetryAnswer

    $inputAdminEmail = Read-Host 'Console admin email (default: admin@local)'
    if (-not [string]::IsNullOrWhiteSpace($inputAdminEmail)) { $consoleAdminEmail = $inputAdminEmail }
    $inputAdminPassword = Read-Host 'Console admin password (default: admin123)'
    if (-not [string]::IsNullOrWhiteSpace($inputAdminPassword)) { $consoleAdminPassword = $inputAdminPassword }
} else {
    if (-not $gatewayAdminToken) { $gatewayAdminToken = New-RandomSecret 32 }
    $adminToken = if ($adminToken) { $adminToken } else { $gatewayAdminToken }
    if (-not $nextAuthSecret) { $nextAuthSecret = New-RandomSecret 48 }
    if (-not $gatewayApiKeys) { $gatewayApiKeys = 'local-key:admin|manager' }
    $telemetryChoice = 'false'
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

$telemetryEnabled = @('1','true','y','yes').Contains($telemetryChoice.ToLowerInvariant())
$envUpdates = @{}
$envUpdates['AION_PROFILE'] = $Profile
$envUpdates['FEATURE_SEAL'] = if ($Profile -eq 'enterprise-vip') { '1' } else { '0' }
$envUpdates['AION_TELEMETRY_OPT_IN'] = if ($telemetryEnabled) { 'true' } else { 'false' }
$envUpdates['AION_TELEMETRY_ENDPOINT'] = $telemetryEndpoint
$envUpdates['AION_POLICY_DIR'] = $PolicyDir
$envUpdates['AION_VOLUME_ROOT'] = $VolumeRoot
$envUpdates['AION_GATEWAY_PORT'] = if ($env:AION_GATEWAY_PORT) { $env:AION_GATEWAY_PORT } else { '3000' }
$envUpdates['AION_GATEWAY_HOST'] = if ($env:AION_GATEWAY_HOST) { $env:AION_GATEWAY_HOST } else { '0.0.0.0' }
$envUpdates['AION_ENABLE_PRISMA'] = if ($env:AION_ENABLE_PRISMA) { $env:AION_ENABLE_PRISMA } else { '1' }
$envUpdates['AION_DB_USER'] = $defaultDbUser
$envUpdates['AION_DB_PASSWORD'] = $defaultDbPassword
$envUpdates['AION_DB_NAME'] = $defaultDbName
$envUpdates['DATABASE_URL'] = $databaseUrl
$envUpdates['AION_CONTROL_POSTGRES_DSN'] = $databaseUrl
$envUpdates['AION_REDIS_URL'] = if ($env:AION_REDIS_URL) { $env:AION_REDIS_URL } else { 'redis://redis:6379/0' }
$envUpdates['AION_CONTROL_BASE_URL'] = if ($env:AION_CONTROL_BASE_URL) { $env:AION_CONTROL_BASE_URL } else { 'http://control:8000' }
$envUpdates['AION_CONTROL_API_PREFIX'] = if ($env:AION_CONTROL_API_PREFIX) { $env:AION_CONTROL_API_PREFIX } else { '/api' }
$envUpdates['AION_CONTROL_GRPC'] = if ($env:AION_CONTROL_GRPC) { $env:AION_CONTROL_GRPC } else { 'http://control:50051' }
$envUpdates['NEXT_PUBLIC_GATEWAY_URL'] = 'http://gateway:3000'
$envUpdates['CONTROL_BASE_URL'] = 'http://localhost:8000'
$envUpdates['GATEWAY_BASE_URL'] = 'http://localhost:3000'
$envUpdates['CONSOLE_BASE_URL'] = 'http://localhost:3001'
$envUpdates['NEXTAUTH_URL'] = 'http://localhost:3001'
$envUpdates['NEXTAUTH_SECRET'] = $nextAuthSecret
$envUpdates['AION_GATEWAY_API_KEYS'] = $gatewayApiKeys
$envUpdates['AION_GATEWAY_API_KEYS_SECRET_PATH'] = if ($env:AION_GATEWAY_API_KEYS_SECRET_PATH) { $env:AION_GATEWAY_API_KEYS_SECRET_PATH } else { '' }
$envUpdates['AION_GATEWAY_ADMIN_TOKEN'] = $gatewayAdminToken
$envUpdates['AION_GATEWAY_ADMIN_TOKEN_SECRET_PATH'] = if ($env:AION_GATEWAY_ADMIN_TOKEN_SECRET_PATH) { $env:AION_GATEWAY_ADMIN_TOKEN_SECRET_PATH } else { '' }
$envUpdates['AION_ADMIN_TOKEN'] = $adminToken
$envUpdates['AION_ADMIN_TOKEN_SECRET_PATH'] = if ($env:AION_ADMIN_TOKEN_SECRET_PATH) { $env:AION_ADMIN_TOKEN_SECRET_PATH } else { '' }
$envUpdates['AION_JWT_SECRET_PATH'] = if ($env:AION_JWT_SECRET_PATH) { $env:AION_JWT_SECRET_PATH } else { '' }
$envUpdates['SECRET_PROVIDER_MODE'] = if ($env:SECRET_PROVIDER_MODE) { $env:SECRET_PROVIDER_MODE } else { 'local' }
$envUpdates['CONSOLE_ADMIN_EMAIL'] = $consoleAdminEmail
$envUpdates['CONSOLE_ADMIN_PASSWORD'] = $consoleAdminPassword
$envUpdates['ORCH_PROVIDER'] = if ($env:ORCH_PROVIDER) { $env:ORCH_PROVIDER } else { '' }
$envUpdates['ORCH_MODEL'] = if ($env:ORCH_MODEL) { $env:ORCH_MODEL } else { '' }
$envUpdates['ORCH_ENDPOINT'] = if ($env:ORCH_ENDPOINT) { $env:ORCH_ENDPOINT } else { '' }
$envUpdates['ORCH_API_KEY'] = if ($env:ORCH_API_KEY) { $env:ORCH_API_KEY } else { '' }
$envUpdates['CODER_PROVIDER'] = if ($env:CODER_PROVIDER) { $env:CODER_PROVIDER } else { '' }
$envUpdates['CODER_MODEL'] = if ($env:CODER_MODEL) { $env:CODER_MODEL } else { '' }
$envUpdates['CODER_ENDPOINT'] = if ($env:CODER_ENDPOINT) { $env:CODER_ENDPOINT } else { '' }
$envUpdates['CODER_API_KEY'] = if ($env:CODER_API_KEY) { $env:CODER_API_KEY } else { '' }
if (-not $env:SKIP_CONSOLE_SEED) { $envUpdates['SKIP_CONSOLE_SEED'] = 'false' }
Set-EnvValues -Path $envPath -Values $envUpdates

$profileFile = Join-Path $profileDir 'profile.json'
$profileObject = [ordered]@{
    profile = $Profile
    setupDone = $true
    updatedAt = ([DateTimeOffset]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss'Z'"))
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
  port: 3000
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

$composePath = Join-Path $rootDir $ComposeFile
if (-not (Test-Path $composePath)) {
    Write-ErrorAndExit "Compose file '$ComposeFile' not found in $rootDir."
}

Resolve-ComposeCommand | Out-Null
if ($script:ComposeCommand) {
    Write-Info "Using $($script:ComposeCommand.Display)"
}
Write-Info "Starting services with compose file $ComposeFile"
$composeProfileMap = @{
    'enterprise-vip' = 'vault'
}
$isWindowsHost = $null
try {
    $isWindowsHost = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Windows)
} catch {
    $isWindowsHost = $IsWindows -or ($env:OS -like 'Windows*')
}
$script:IsWindowsPlatform = $isWindowsHost

$attempt = 1
while ($attempt -le 3) {
    try {
        $localComposeArgs = [string[]]@('-f', $ComposeFile)
        if ($composeProfileMap.ContainsKey($Profile) -and $composeProfileMap[$Profile]) {
            $localComposeArgs += @('--profile', [string]$composeProfileMap[$Profile])
        }
        if ($script:IsWindowsPlatform) {
            $localComposeArgs += @('--profile', 'windows')
        }
        $localComposeArgs += @('up', '-d', '--remove-orphans')
        Write-Info ("ComposeArgs (count={0}): {1}" -f $localComposeArgs.Count, ($localComposeArgs -join ' '))
        Assert-ComposeArgsContainsUp -ComposeArgsToValidate $localComposeArgs
        Write-Info "Compose arguments: $($localComposeArgs -join ' ')"
        Push-Location $rootDir
        Invoke-Compose -ComposeCommandArgs $localComposeArgs
        Pop-Location
        break
    } catch {
        Pop-Location
        if ($attempt -ge 3) { throw }
        Write-Warn "compose attempt $attempt failed; retrying"
        Start-Sleep -Seconds ($attempt * 5)
        $attempt += 1
    }
}

$requiredServices = Get-RequiredServices -Profile $Profile
$psOutput = Invoke-Compose -ComposeCommandArgs @('-f', $ComposeFile, 'ps', '--format', 'json')
$psObjects = Convert-ComposePsOutput -Output $psOutput
if (-not $psObjects -or $psObjects.Count -eq 0 -or -not (Test-ComposeServicesRunning -Services $psObjects -Required $requiredServices)) {
    Write-Warn 'compose ps reported issues; waiting for services to become ready.'
}

Wait-ComposeReady -ComposeFile $ComposeFile -Profile $Profile -TimeoutSeconds 180 -DelaySeconds 3

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

Write-Info "AION_GATEWAY_ADMIN_TOKEN=$gatewayAdminToken"
Write-Info "AION_GATEWAY_API_KEYS=$gatewayApiKeys"
Write-Info "NEXTAUTH_URL=http://localhost:3001"
Write-Info "NEXTAUTH_SECRET=$nextAuthSecret"
Write-Info "Console admin user: $consoleAdminEmail / $consoleAdminPassword"

$consoleLoginUrl = 'http://localhost:3001/login'
$consoleRootUrl = 'http://localhost:3001/'
$consoleReady = $false
if (Wait-HttpReady -Url $consoleLoginUrl) {
    $consoleReady = $true
} elseif (Wait-HttpReady -Url $consoleRootUrl) {
    $consoleReady = $true
    $consoleLoginUrl = $consoleRootUrl
}

if ($consoleReady) {
    Write-Info "Console is reachable at $consoleLoginUrl"
    try {
        Start-Process $consoleLoginUrl | Out-Null
        Write-Info "Opened browser: $consoleLoginUrl"
    } catch {
        Write-Warn "Failed to automatically open the browser: $($_.Exception.Message)"
    }
} else {
    Write-Warn "Console endpoint did not become ready within the timeout. Visit $consoleRootUrl manually to verify."
}

Write-Host ''
Write-Host '[AION-OS] QuickSetup completed.'
Write-Host "Profile: $Profile"
Write-Host "Compose file: $ComposeFile"
Write-Host 'Services:'
Write-Host '  Control API:      http://localhost:8000'
Write-Host '  Gateway (REST):   http://localhost:3000'
Write-Host '  Console UI:       http://localhost:3001'
Write-Host ''
Write-Host "Credentials: Console admin $consoleAdminEmail / $consoleAdminPassword"
Write-Host "Gateway admin token: $gatewayAdminToken"
Write-Host "Gateway API keys: $gatewayApiKeys"
Write-Host ''
Write-Host "Monitor stack: $($script:ComposeCommand.Display) -f $ComposeFile ps"
Write-Host "View logs:    $($script:ComposeCommand.Display) -f $ComposeFile logs --tail=200"
Write-Host 'Smoke test:   scripts/smoke_e2e.ps1'
