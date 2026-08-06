#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$installer = Join-Path $scriptDir 'deploy/docker/scripts/install.ps1'
if (-not (Test-Path $installer)) {
    Write-Host "[ERROR] Unable to locate deploy/docker/scripts/install.ps1" -ForegroundColor Red
    exit 1
}
& $installer @args
exit $LASTEXITCODE
