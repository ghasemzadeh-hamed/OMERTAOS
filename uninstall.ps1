Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$composeFile = Join-Path $scriptDir 'deploy/docker/compose/full.yml'
Set-Location $scriptDir
& docker compose --project-directory . -f $composeFile down -v @args
exit $LASTEXITCODE
