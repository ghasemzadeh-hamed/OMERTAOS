Write-Host "[AIONOS] Windows install"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { winget install OpenJS.NodeJS --silent }
npm i -g pnpm
pnpm i
pnpm -C console build
Write-Host "Run: pnpm -C console start"
