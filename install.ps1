$ErrorActionPreference = "Stop"

function Require-Cmd {
  param([string]$name)
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ابزار '$name' پیدا نشد. لطفاً نصبش کن و دوباره اجرا کن." -ForegroundColor Red
    exit 1
  }
}

Write-Host "🚀 AION-OS – Windows Installer (AIONOS branch)" -ForegroundColor Cyan

Require-Cmd git
Require-Cmd docker

try {
  $wslv = wsl -l -v 2>$null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "ℹ️  WSL وضعیت:"; $wslv
  }
} catch {
  Write-Host "ℹ️  WSL موجود نیست (اختیاری است)."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $scriptDir ".git")) {
  $targetDir = $scriptDir
  Set-Location $targetDir
  Write-Host "ℹ️  مخزن OMERTAOS در $targetDir پیدا شد؛ همان را استفاده می‌کنیم." -ForegroundColor Yellow
  try {
    $defaultRepoUrl = git remote get-url origin
  } catch {
    $defaultRepoUrl = "https://github.com/ghasemzadeh-hamed/OMERTAOS.git"
  }
} else {
  $targetDir = Join-Path (Get-Location) "OMERTAOS"
  $defaultRepoUrl = "https://github.com/ghasemzadeh-hamed/OMERTAOS.git"
}

$repoUrl = Read-Host "🔗 Repo URL (enter برای پیشفرض)"
if ([string]::IsNullOrWhiteSpace($repoUrl)) { $repoUrl = $defaultRepoUrl }
$branch  = Read-Host "🌿 Branch (enter برای AIONOS)"
if ([string]::IsNullOrWhiteSpace($branch)) { $branch = "AIONOS" }

$adminUser = Read-Host "👤 نام کاربر ادمین اولیه (مثلاً admin)"
$adminPass = Read-Host "🔑 پسورد ادمین (حداقل 8 کاراکتر)"
$uiPort    = Read-Host "🖥️  پورت UI (console) (enter=3000)"
if ([string]::IsNullOrWhiteSpace($uiPort)) { $uiPort = "3000" }
$gwPort    = Read-Host "🌐 پورت Gateway (enter=8080)"
if ([string]::IsNullOrWhiteSpace($gwPort)) { $gwPort = "8080" }
$apiPort   = Read-Host "⚙️  پورت FastAPI (enter=8000)"
if ([string]::IsNullOrWhiteSpace($apiPort)) { $apiPort = "8000" }

$pgUser = Read-Host "🗄️  Postgres user (enter=postgres)"
if ([string]::IsNullOrWhiteSpace($pgUser)) { $pgUser = "postgres" }
$pgPass = Read-Host "🔐 Postgres password (enter=postgres)"
if ([string]::IsNullOrWhiteSpace($pgPass)) { $pgPass = "postgres" }
$pgDb   = Read-Host "📚 Postgres DB name (enter=aionos)"
if ([string]::IsNullOrWhiteSpace($pgDb)) { $pgDb = "aionos" }

$redisUrl = Read-Host "🧠 Redis URL (enter=redis://redis:6379)"
if ([string]::IsNullOrWhiteSpace($redisUrl)) { $redisUrl = "redis://redis:6379" }
$minioUrl = Read-Host "🗂️  MinIO Console URL (enter=http://localhost:9001)"
if ([string]::IsNullOrWhiteSpace($minioUrl)) { $minioUrl = "http://localhost:9001" }

$useBigData = Read-Host "📊 فعال‌سازی BigData overlay؟ (y/N)"
$useBigData = $useBigData.ToLower() -eq "y"

if ($targetDir -ne $scriptDir) {
  if (Test-Path (Join-Path $targetDir ".git")) {
    Write-Host "ℹ️  پوشه OMERTAOS موجود است؛ pull آخرین تغییرات…" -ForegroundColor Yellow
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

function Write-EnvFile {
  param([string]$path, [string]$content)
  $dir = Split-Path $path -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $content | Out-File -FilePath $path -Encoding UTF8 -Force
  Write-Host "✅ wrote $path"
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

if ($useBigData -and (Test-Path "docker-compose.bigdata.yml")) {
  Write-Host "🟣 Starting with BigData overlay…" -ForegroundColor Magenta
  docker compose -f docker-compose.yml -f docker-compose.bigdata.yml up -d --build
} elseif ($useBigData -and (Test-Path "bigdata/docker-compose.bigdata.yml")) {
  Write-Host "🟣 Starting with BigData overlay (bigdata/docker-compose.bigdata.yml)…" -ForegroundColor Magenta
  docker compose -f docker-compose.yml -f bigdata/docker-compose.bigdata.yml up -d --build
} elseif ($useBigData) {
  Write-Host "⚠️  فایل BigData overlay پیدا نشد؛ حالت اصلی اجرا می‌شود." -ForegroundColor Yellow
  docker compose up -d --build
} else {
  Write-Host "🟢 Starting core stack…" -ForegroundColor Green
  docker compose up -d --build
}

Start-Sleep -Seconds 5
Write-Host "`n📡 Containers:" -ForegroundColor Cyan
docker ps --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"

Write-Host "`n🌐 URLs:"
Write-Host "UI (console):     http://localhost:$uiPort"
Write-Host "Gateway:          http://localhost:$gwPort"
Write-Host "FastAPI (docs):   http://localhost:$apiPort/docs"
Write-Host "MinIO Console:    $minioUrl (اگر BigData فعال است)"

Write-Host "`n✅ نصب تمام شد. اگر اولین باره، چند ثانیه صبر کن تا DB seed کامل شود."
