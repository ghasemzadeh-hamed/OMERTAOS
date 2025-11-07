$ErrorActionPreference = "Stop"

param(
  [switch]$Local = $false
)

function Require-Cmd {
  param([string]$name)
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Required command '$name' was not found. Please install it and re-run this script." -ForegroundColor Red
    exit 1
  }
}

if ($Local) {
  Write-Host "AION-OS Windows Installer (Personal Mode)" -ForegroundColor Cyan
} else {
  Write-Host "AION-OS Windows Installer (AIONOS branch)" -ForegroundColor Cyan
}

Require-Cmd git
Require-Cmd docker

try {
  $wslv = wsl -l -v 2>$null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "WSL status:"; $wslv
  }
} catch {
  Write-Host "WSL not detected (optional)."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $scriptDir ".git")) {
  $targetDir = $scriptDir
  Set-Location $targetDir
  Write-Host "Detected OMERTAOS repository at $targetDir; using it." -ForegroundColor Yellow
  try {
    $defaultRepoUrl = git remote get-url origin
  } catch {
    $defaultRepoUrl = "https://github.com/ghasemzadeh-hamed/OMERTAOS.git"
  }
} else {
  $targetDir = Join-Path (Get-Location) "OMERTAOS"
  $defaultRepoUrl = "https://github.com/ghasemzadeh-hamed/OMERTAOS.git"
}

$repoUrl = Read-Host "Repository URL (press enter for default)"
if ([string]::IsNullOrWhiteSpace($repoUrl)) { $repoUrl = $defaultRepoUrl }
$branch  = Read-Host "Branch name (press enter for AIONOS)"
if ([string]::IsNullOrWhiteSpace($branch)) { $branch = "AIONOS" }

$adminUser = Read-Host "Initial admin username (example: admin)"
$adminPass = Read-Host "Initial admin password (min 8 characters)"
$uiPort    = Read-Host "Console port (enter=3000)"
if ([string]::IsNullOrWhiteSpace($uiPort)) { $uiPort = "3000" }
$gwPort    = Read-Host "Gateway port (enter=8080)"
if ([string]::IsNullOrWhiteSpace($gwPort)) { $gwPort = "8080" }
$apiPort   = Read-Host "FastAPI port (enter=8000)"
if ([string]::IsNullOrWhiteSpace($apiPort)) { $apiPort = "8000" }

$pgUser = Read-Host "Postgres user (enter=postgres)"
if ([string]::IsNullOrWhiteSpace($pgUser)) { $pgUser = "postgres" }
$pgPass = Read-Host "Postgres password (enter=postgres)"
if ([string]::IsNullOrWhiteSpace($pgPass)) { $pgPass = "postgres" }
$pgDb   = Read-Host "Postgres database name (enter=aionos)"
if ([string]::IsNullOrWhiteSpace($pgDb)) { $pgDb = "aionos" }

$redisUrl = Read-Host "Redis URL (enter=redis://redis:6379)"
if ([string]::IsNullOrWhiteSpace($redisUrl)) { $redisUrl = "redis://redis:6379" }
$minioUrl = Read-Host "MinIO Console URL (enter=http://localhost:9001)"
if ([string]::IsNullOrWhiteSpace($minioUrl)) { $minioUrl = "http://localhost:9001" }

$useBigData = $false
if (-not $Local) {
  $useBigData = Read-Host "Enable BigData overlay? (y/N)"
  $useBigData = $useBigData.ToLower() -eq "y"
}

if ($targetDir -ne $scriptDir) {
  if (Test-Path (Join-Path $targetDir ".git")) {
    Write-Host "Found existing OMERTAOS folder; pulling latest changes." -ForegroundColor Yellow
    Set-Location $targetDir
    git fetch origin $branch
    git checkout $branch
    git pull origin $branch
  } else {
    git clone -b $branch --single-branch $repoUrl OMERTAOS
    Set-Location $targetDir
  }
} else {
  try { git fetch origin $branch | Out-Null } catch {}
  git checkout $branch
  try { git pull origin $branch | Out-Null } catch {}
}

Write-Host ""
Write-Host "Select AION-OS kernel profile:"
Write-Host "  1) user           - Quickstart, local-only, minimal"
Write-Host "  2) professional   - Explorer + Terminal + IoT"
Write-Host "  3) enterprise-vip - SEAL, GPU, advanced routing"
$choice = Read-Host "Enter 1-3 [1]"

switch ($choice) {
  "2" { $profile = "professional" }
  "3" { $profile = "enterprise-vip" }
  default { $profile = "user" }
}

$envPath = Join-Path $targetDir ".env"
if (-not (Test-Path $envPath)) {
  if (Test-Path (Join-Path $targetDir ".env.example")) {
    Copy-Item (Join-Path $targetDir ".env.example") $envPath
  } else {
    New-Item -ItemType File -Path $envPath | Out-Null
  }
}

(Get-Content $envPath) |
  Where-Object {$_ -notmatch '^AION_PROFILE=' -and $_ -notmatch '^FEATURE_SEAL='} |
  Set-Content $envPath

Add-Content $envPath "AION_PROFILE=$profile"
if ($profile -eq "enterprise-vip") {
  Add-Content $envPath "FEATURE_SEAL=1"
} else {
  Add-Content $envPath "FEATURE_SEAL=0"
}

$profileDir = Join-Path $targetDir ".aionos"
if (-not (Test-Path $profileDir)) {
  New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
}
$profileFile = Join-Path $profileDir "profile.json"
$profileObject = @{ profile = $profile; setupDone = $true; updatedAt = [DateTime]::UtcNow.ToString("o") }
$profileObject | ConvertTo-Json | Set-Content -Path $profileFile

Write-Host "Selected kernel profile: $profile"

function Write-EnvFile {
  param([string]$path, [string]$content)
  $dir = Split-Path $path -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $content | Out-File -FilePath $path -Encoding UTF8 -Force
  Write-Host "Wrote $path"
}

$FASTAPI_URL = "http://control:$apiPort"
$GATEWAY_URL = "http://gateway:$gwPort"

$consoleEnv = @"
NEXT_PUBLIC_API_BASE=$GATEWAY_URL
NEXTAUTH_SECRET=$([Guid]::NewGuid().ToString("N"))
NEXTAUTH_URL=http://localhost:$uiPort
DATABASE_URL=postgresql://$pgUser:$pgPass@postgres:5432/$pgDb
REDIS_URL=$redisUrl
ADMIN_SEED_USER=$adminUser
ADMIN_SEED_PASS=$adminPass
FASTAPI_URL=$FASTAPI_URL
"@
Write-EnvFile "console/.env" $consoleEnv

$gatewayEnv = @"
PORT=$gwPort
CONTROL_BASE_URL=$FASTAPI_URL
REDIS_URL=$redisUrl
ALLOW_ORIGIN=*
"@
Write-EnvFile "gateway/.env" $gatewayEnv

$controlEnv = @"
PORT=$apiPort
POSTGRES_DSN=postgresql://$pgUser:$pgPass@postgres:5432/$pgDb
REDIS_URL=$redisUrl
MINIO_ENDPOINT=http://minio:9000
"@
Write-EnvFile "control/.env" $controlEnv

if ($Local) {
  $composeArgs = @('-f', 'docker-compose.local.yml')
  Write-Host "Starting personal mode stack (docker-compose.local.yml)..." -ForegroundColor Green
  docker compose @composeArgs up -d --build
} elseif ($useBigData -and (Test-Path "docker-compose.bigdata.yml")) {
  Write-Host "Starting with BigData overlay (docker-compose.bigdata.yml)..." -ForegroundColor Magenta
  docker compose -f docker-compose.yml -f docker-compose.bigdata.yml up -d --build
} elseif ($useBigData -and (Test-Path "bigdata/docker-compose.bigdata.yml")) {
  Write-Host "Starting with BigData overlay (bigdata/docker-compose.bigdata.yml)..." -ForegroundColor Magenta
  docker compose -f docker-compose.yml -f bigdata/docker-compose.bigdata.yml up -d --build
} elseif ($useBigData) {
  Write-Host "WARNING: BigData overlay file not found; running base stack." -ForegroundColor Yellow
  docker compose up -d --build
} else {
  Write-Host "Starting core stack..." -ForegroundColor Green
  docker compose up -d --build
}

Start-Sleep -Seconds 5
Write-Host "`nContainers:" -ForegroundColor Cyan
docker ps --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"

Write-Host "`nService URLs:"
Write-Host "UI (console):     http://localhost:$uiPort"
Write-Host "Gateway:          http://localhost:$gwPort"
Write-Host "FastAPI (docs):   http://localhost:$apiPort/docs"
if ($Local) {
  Write-Host "Kernel API:       http://localhost:8010"
}
Write-Host "MinIO Console:    $minioUrl (only if BigData overlay is enabled)"

Write-Host "`nSetup complete. If this is the first run, allow the database seed to finish."
