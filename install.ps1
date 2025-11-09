#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$quickSetup = Join-Path $scriptDir 'scripts/quicksetup.ps1'
if (-not (Test-Path $quickSetup)) {
    Write-Host "[ERROR] Unable to locate scripts/quicksetup.ps1" -ForegroundColor Red
    exit 1
}
& $quickSetup @args
