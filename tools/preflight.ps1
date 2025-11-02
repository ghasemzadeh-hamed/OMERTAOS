#!/usr/bin/env pwsh
param(
  [switch]$NonInteractive
)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$arguments = @()
if ($NonInteractive) {
  $arguments += "--noninteractive"
}
& $python "$scriptDir/preflight.py" @arguments
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
