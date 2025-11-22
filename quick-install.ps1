$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

if (-Not (Test-Path "dev.env")) {
    Write-Error "dev.env missing; aborting."
}

if (-Not (Test-Path ".env")) {
    Copy-Item dev.env .env
    Write-Output "Created .env from dev.env"
} else {
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    Copy-Item .env ".env.bak.$timestamp"
    Write-Output "Backed up existing .env"
}

Write-Output "Generating self-signed certificates (dev only)..."
New-Item -ItemType Directory -Force -Path "config/certs/dev" | Out-Null
New-Item -ItemType Directory -Force -Path "config/keys" | Out-Null

openssl req -x509 -newkey rsa:2048 -nodes -keyout config/certs/dev/dev.key -out config/certs/dev/dev.crt -days 365 -subj "/CN=localhost"
openssl genrsa -out config/keys/dev-jwt.key 2048
openssl rsa -in config/keys/dev-jwt.key -pubout -out config/keys/dev-jwt.pub

Write-Warning "The generated certificates and placeholder secrets are for development only. Rotate before production."

Write-Output "Starting stack with docker compose..."
docker compose -f docker-compose.quickstart.yml up --build -d

Write-Output "Quick install completed. Services: control:8000, gateway:8080, console:3000"
