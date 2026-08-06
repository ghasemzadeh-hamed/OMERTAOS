#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir '../../..')
Set-Location $repoRoot
& docker compose --project-directory . -f deploy/docker/compose/quickstart.yml up @args
exit $LASTEXITCODE
