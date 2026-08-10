[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-f]{40}$')]
    [string]$CommitSha,
    [string]$RuntimeRoot = 'E:\Hyper-V\OMERTAOS-N0-SIM',
    [string]$SshKeyPath = "$HOME\.ssh\omertaos_n0_sim_ed25519",
    [ValidateRange(1024, 65535)]
    [int]$SshPort = 2222
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$localSha = (& git.exe -C $repoRoot rev-parse HEAD).Trim()
if ($localSha -ne $CommitSha) { throw "Local checkout is $localSha, expected $CommitSha." }
if (& git.exe -C $repoRoot status --porcelain) { throw 'N1 requires a clean local checkout.' }

& python.exe (Join-Path $repoRoot 'deploy/native/env/validate.py')
if ($LASTEXITCODE -ne 0) { throw 'Committed N1 environment templates failed validation.' }

$sshArgs = @(
    '-i', $SshKeyPath,
    '-p', $SshPort,
    '-o', 'BatchMode=yes',
    '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=NUL',
    '-o', 'ConnectTimeout=10',
    'omerta@127.0.0.1'
)
$validator = '/srv/omertaos-source/deploy/native/scripts/validate-environment.sh'
$remoteCommand = "sudo -n bash '$validator' --mode simulation --expected-commit '$CommitSha'"
$remoteEvidence = & ssh.exe @sshArgs $remoteCommand
if ($LASTEXITCODE -ne 0) { throw 'N1 simulated host validation failed.' }

$evidenceDir = Join-Path $RuntimeRoot 'evidence'
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
$result = [ordered]@{
    phase = 'N1-simulation'
    status = 'passed-contract-simulated'
    validated_at = (Get-Date).ToString('o')
    commit = $CommitSha
    ssh_endpoint = "127.0.0.1:$SshPort"
    hyperv_acceptance = 'not-run'
    package_installation = 'deferred-to-N2'
    runtime_build = 'deferred-to-N4'
    evidence = @($remoteEvidence)
}
$evidencePath = Join-Path $evidenceDir "n1-simulation-$CommitSha.json"
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $evidencePath -Encoding utf8
$result | ConvertTo-Json -Depth 5
