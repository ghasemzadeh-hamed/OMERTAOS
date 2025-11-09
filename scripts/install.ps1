# DEPRECATED: use scripts/quicksetup.ps1 instead of this installer.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host '[WARN] scripts/install.ps1 is deprecated. Redirecting to scripts/quicksetup.ps1.' -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Resolve-Path (Join-Path $scriptDir '..')
$quickSetup = Join-Path $rootDir 'scripts/quicksetup.ps1'
if (-not (Test-Path $quickSetup)) {
    Write-Host '[ERROR] Unable to locate scripts/quicksetup.ps1' -ForegroundColor Red
    exit 1
}
& $quickSetup @args
