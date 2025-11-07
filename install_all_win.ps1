#Requires -Version 5.1
[CmdletBinding()]
param(
  [switch]$NonInteractive
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Admin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal  = New-Object Security.Principal.WindowsPrincipal($id)
  if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this script from an elevated PowerShell session."
  }
}

Require-Admin
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Have($name) { Get-Command $name -ErrorAction SilentlyContinue | Out-Null }
function Retry($count, [ScriptBlock]$block) {
  for ($i = 1; $i -le $count; $i++) {
    try {
      & $block
      return
    } catch {
      Start-Sleep -Seconds ([Math]::Min(10, $i * 3))
    }
  }
  throw "Operation failed after $count attempts."
}

$useWinget = $false
if (Have 'winget') {
  $useWinget = $true
} else {
  Write-Warning 'winget not available. Falling back to Chocolatey.'
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
  Retry 3 { Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')) }
}

function Install-PackageId($wingetId, $chocoId) {
  if ($useWinget) {
    $arguments = @('install', '--id', $wingetId, '-e', '--accept-source-agreements', '--accept-package-agreements')
    Retry 2 { & winget @arguments }
  } else {
    $arguments = @('install', $chocoId, '-y', '--no-progress')
    Retry 2 { & choco @arguments }
  }
}

Write-Host '[*] Enabling required Windows features (WSL, VirtualMachinePlatform)'
dism /Online /Enable-Feature /FeatureName:Microsoft-Windows-Subsystem-Linux /All /NoRestart | Out-Null
dism /Online /Enable-Feature /FeatureName:VirtualMachinePlatform /All /NoRestart | Out-Null

Write-Host '[*] Installing core prerequisites'
Install-PackageId 'Git.Git' 'git'
Install-PackageId 'Python.Python.3' 'python'
Install-PackageId 'OpenJS.NodeJS.LTS' 'nodejs-lts'
Install-PackageId 'Docker.DockerDesktop' 'docker-desktop'
Install-PackageId 'Ollama.Ollama' 'ollama'

$hasUbuntu = (wsl -l -q) -contains 'Ubuntu'
if (-not $hasUbuntu) {
  wsl --install -d Ubuntu
} else {
  Write-Host "[*] WSL Ubuntu already exists, skipping install."
}

Write-Host '[*] Starting Docker Desktop'
$dockerDesktop = "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerDesktop) {
  Start-Process -FilePath $dockerDesktop -WindowStyle Minimized | Out-Null
  for ($i = 0; $i -lt 60; $i++) {
    try {
      docker version | Out-Null
      break
    } catch {
      Start-Sleep -Seconds 3
    }
  }
} else {
  Write-Warning 'Docker Desktop executable not found yet.'
}

$configDir = Join-Path $Root 'config'
if (-not (Test-Path $configDir)) { New-Item -ItemType Directory -Path $configDir | Out-Null }

$preflight = Join-Path $Root 'tools\preflight.ps1'
if (Test-Path $preflight) {
  if ($NonInteractive) {
    & $preflight -NonInteractive
  } else {
    & $preflight
  }
  if ($LASTEXITCODE -ne 0) { throw "Preflight checks failed." }
}

$envFile = Join-Path $Root '.env'
$envExample = Join-Path $Root 'config/templates/.env.example'
if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
  Copy-Item $envExample $envFile -Force
}

$configFile = Join-Path $configDir 'aionos.config.yaml'
if (-not (Test-Path $configFile)) {
  $config = @"
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
telemetry:
  otelEnabled: false
  endpoint: http://localhost:4317
"@
  Set-Content -Path $configFile -Value $config -Encoding UTF8
}

$installScript = Join-Path $Root 'install.sh'
$ranUnixBootstrap = $false
if (Test-Path $installScript) {
  if (Have 'bash') {
    Write-Host '[*] Running install.sh via Git Bash'
    try {
      & bash $installScript --noninteractive
      $ranUnixBootstrap = $true
    } catch {
      Write-Warning "Git Bash bootstrap failed: $($_.Exception.Message)"
    }
  }
  if (-not $ranUnixBootstrap -and (Have 'wsl')) {
    Write-Host '[*] Running install.sh inside WSL'
    $wslPath = "/mnt/" + $Root.Substring(0,1).ToLower() + $Root.Substring(1).Replace('\\','/')
    try {
      & wsl bash -lc "cd '$wslPath' && bash './install.sh' --noninteractive"
      $ranUnixBootstrap = $true
    } catch {
      Write-Warning "WSL bootstrap failed: $($_.Exception.Message)"
    }
  }
}

if (-not $ranUnixBootstrap) {
  Write-Warning 'Falling back to native docker compose setup.'
  if (Have 'docker') {
    try {
      Retry 3 { docker compose up -d --build }
    } catch {
      Write-Warning "docker compose failed: $($_.Exception.Message)"
    }
  }
  if (Have 'ollama') {
    try { & ollama pull 'llama3.2:3b' } catch { Write-Warning "ollama pull failed: $($_.Exception.Message)" }
  }
}

Write-Host ''
Write-Host '====================================================='
Write-Host 'OMERTAOS Windows bootstrap complete.'
Write-Host 'Run scripts\smoke_e2e.ps1 once services are healthy.'
Write-Host '====================================================='
