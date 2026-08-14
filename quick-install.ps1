#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $scriptDir 'deploy/docker/scripts/install.ps1'
if (-not (Test-Path $target)) {
    Write-Host "[ERROR] Unable to locate deploy/docker/scripts/install.ps1" -ForegroundColor Red
    exit 1
}
& $target @args
