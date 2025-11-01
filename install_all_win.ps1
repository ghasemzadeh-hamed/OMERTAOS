#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Admin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $p  = New-Object Security.Principal.WindowsPrincipal($id)
  if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Run this script as Administrator."
  }
}
Require-Admin

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

function Have($name){ Get-Command $name -ErrorAction SilentlyContinue | Out-Null }
function Retry($n, [ScriptBlock]$block) { for($i=1;$i -le $n;$i++){ try{& $block;return}catch{Start-Sleep -Seconds ([Math]::Min(5,$i*2))} } throw }
function Ensure-Dir($p){ if(-not (Test-Path $p)){ New-Item -ItemType Directory -Path $p | Out-Null } }

$UseWinget = $false
if (Have winget) { $UseWinget = $true } else {
  Write-Warning "winget not found. Installing Chocolatey as fallback..."
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
  Retry 3 { Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')) }
}

function Install-Pkg($idWinget, $idChoco, [switch]$Force) {
  if ($UseWinget) {
    $args = @("install","--id",$idWinget,"-e","--accept-source-agreements","--accept-package-agreements")
    if($Force){ $args += "--force" }
    Retry 2 { & winget @args }
  } else {
    $args = @("install",$idChoco,"-y","--no-progress")
    Retry 2 { & choco @args }
  }
}

Write-Host "[*] Enabling Windows Optional Features (WSL, VirtualMachinePlatform) ..."
dism /Online /Enable-Feature /FeatureName:Microsoft-Windows-Subsystem-Linux /All /NoRestart | Out-Null
dism /Online /Enable-Feature /FeatureName:VirtualMachinePlatform /All /NoRestart | Out-Null

Write-Host "[*] Installing core developer tools ..."
Install-Pkg -idWinget "Git.Git"                -idChoco "git"
Install-Pkg -idWinget "Python.Python.3"        -idChoco "python"
Install-Pkg -idWinget "7zip.7zip"              -idChoco "7zip"
Install-Pkg -idWinget "Microsoft.VisualStudio.2022.BuildTools" -idChoco "visualstudio2022buildtools"
Install-Pkg -idWinget "Docker.DockerDesktop"   -idChoco "docker-desktop"
Install-Pkg -idWinget "OpenJS.NodeJS.LTS"      -idChoco "nodejs-lts"
Install-Pkg -idWinget "Ollama.Ollama"          -idChoco "ollama"

if (-not (wsl -l -q 2>$null)) {
  Write-Host "[*] Installing WSL Ubuntu ..."
  try { & wsl --install -d Ubuntu } catch { Write-Warning "wsl --install failed or needs reboot." }
}

Write-Host "[*] Starting Docker Desktop (best effort) ..."
$dockerDesktop = "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerDesktop) {
  Start-Process -FilePath $dockerDesktop -WindowStyle Minimized | Out-Null
  for($i=1;$i -le 60;$i++){
    if (Have docker) { try { docker version | Out-Null; break } catch {} }
    Start-Sleep -Seconds 3
  }
} else {
  Write-Warning "Docker Desktop not found yet."
}

Ensure-Dir "$ROOT\config"
if (-not (Test-Path "$ROOT\.env") -and (Test-Path "$ROOT\.env.example")) {
  Copy-Item "$ROOT\.env.example" "$ROOT\.env" -Force
}
$cfg = @"
version: 1
onboardingComplete: false
admin:
  email: "admin@localhost"
  password: "admin"
console:
  port: 3000
  baseUrl: "http://localhost:3000"
  locale: "en"
gateway:
  port: 8080
  apiKey: ""
control:
  httpPort: 8000
  grpcPort: 50051
data:
  postgres: { host: "postgres", port: 5432, user: "aionos", password: "aionos", db: "aionos" }
  redis:    { host: "redis", port: 6379 }
  qdrant:   { host: "qdrant", port: 6333 }
  minio:    { endpoint: "http://minio:9000", accessKey: "minioadmin", secretKey: "minioadmin", bucket: "aionos" }
models:
  provider: "local"
  local:
    engine: "ollama"
    model: "llama3.2:3b"
    ctx: 4096
    temperature: 0.2
    num_gpu: 0
  routing:
    mode: "local-first"
    budget_ms: 18000
    allow_remote: false
agent:
  enabled: true
  allow_ui_tool: false
  policy:
    allowed_paths:
      - "/api/*"
    allowed_ui_actions:
      - "click"
      - "fill"
      - "press"
security:
  agent_api_token: ""
telemetry:
  otelEnabled: true
  serviceName: "aionos"
"@
$cfgFile = "$ROOT\config\aionos.config.yaml"
if (-not (Test-Path $cfgFile)) { Set-Content -Path $cfgFile -Value $cfg -Encoding UTF8 }
$env:AIONOS_CONFIG_PATH = $cfgFile

function New-Hex { param([int]$bytes=32)
  $buf = New-Object byte[] $bytes
  [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($buf)
  ($buf | ForEach-Object { $_.ToString("x2") }) -join ''
}
$envFile = "$ROOT\.env"
$agentToken = $null
if (Test-Path $envFile -and (Select-String -Path $envFile -Pattern '^AGENT_API_TOKEN=' -SimpleMatch -Quiet)) {
  $agentToken = (Get-Content $envFile | Where-Object { $_ -match '^AGENT_API_TOKEN=' } | Select-Object -Last 1).Split('=')[1]
} else {
  if (-not (Test-Path $envFile)) { New-Item -ItemType File -Path $envFile | Out-Null }
  $agentToken = New-Hex 32
  Add-Content -Path $envFile -Value "AGENT_API_TOKEN=$agentToken"
}
$env:AGENT_API_TOKEN = $agentToken

$ranBash = $false
$installSh = Join-Path $ROOT "install.sh"
if (Test-Path $installSh) {
  if (Have bash) {
    Write-Host "[*] Running install.sh via Git Bash ..."
    try { & bash "$installSh"; $ranBash = $true } catch { Write-Warning "Git Bash run failed: $($_.Exception.Message)" }
  }
  if (-not $ranBash) {
    Write-Host "[*] Trying WSL ..."
    try {
      $wslPath = "/mnt/" + $ROOT.Substring(0,1).ToLower() + $ROOT.Substring(1).Replace('\\','/')
      & wsl bash -lc "cd '$wslPath' && bash './install.sh'"
      $ranBash = $true
    } catch { Write-Warning "WSL run failed: $($_.Exception.Message)" }
  }
}

if (-not $ranBash) {
  Write-Warning "Falling back to native PowerShell steps."
  if (Have docker) { try { docker compose up -d --build } catch { Write-Warning "docker compose failed: $($_.Exception.Message)" } }
  if (Have ollama) { try { & ollama pull "llama3.2:3b" } catch { Write-Warning "ollama pull failed: $($_.Exception.Message)" } }
}

$consoleUrl = "http://localhost:3000"
Write-Host "[*] Waiting for console ($consoleUrl) ..."
for($i=1;$i -le 90;$i++){ try { $r = Invoke-WebRequest -Uri $consoleUrl -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500){ break } } catch { Start-Sleep -Seconds 2 } }
try { Start-Process $consoleUrl | Out-Null } catch {}

$InstallFaIR = $true
if ($InstallFaIR) {
  Write-Host "[*] Installing Persian language capabilities (optional) ..."
  try {
    dism /Online /Add-Capability /CapabilityName:Language.Basic~~~fa-IR~0.0.1 /NoRestart | Out-Null
    dism /Online /Add-Capability /CapabilityName:Language.Fonts.Persian~~~und-IR~0.0.1 /NoRestart | Out-Null  2>$null
  } catch { Write-Warning "Language pack install failed or not supported: $($_.Exception.Message)" }
}

Write-Host ""
Write-Host "====================================================="
Write-Host "AION-OS Quick-Start on Windows is ready (best effort)."
Write-Host "Console: $consoleUrl"
Write-Host "Ollama:  http://127.0.0.1:11434"
Write-Host "Agent Token (saved in .env): AGENT_API_TOKEN=$($env:AGENT_API_TOKEN)"
Write-Host "If Docker Desktop requested a reboot or login, please do it and re-run this script once."
Write-Host "====================================================="
