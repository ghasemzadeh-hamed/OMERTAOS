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
$composeFile = Join-Path $PSScriptRoot 'compose.yml'
$releasePath = Join-Path $RuntimeRoot "releases\$CommitSha"
$runtimeDir = Join-Path $RuntimeRoot 'runtime'
$evidenceDir = Join-Path $RuntimeRoot 'evidence'
foreach ($path in $RuntimeRoot, (Split-Path $releasePath), $runtimeDir, $evidenceDir, (Split-Path $SshKeyPath)) {
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

if (-not (Test-Path -LiteralPath $SshKeyPath)) {
    & ssh-keygen.exe -q -t ed25519 -N '' -C 'omertaos-n0-simulation' -f $SshKeyPath
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create the external N0 SSH key.' }
}
$publicKeyPath = "$SshKeyPath.pub"
if (-not (Test-Path -LiteralPath $publicKeyPath)) { throw 'N0 SSH public key is missing.' }

if (-not (Test-Path -LiteralPath $releasePath)) {
    & git clone --quiet --no-hardlinks --no-checkout $repoRoot $releasePath
    if ($LASTEXITCODE -ne 0) { throw 'Failed to clone the release snapshot.' }
    & git -C $releasePath checkout --quiet --detach $CommitSha
    if ($LASTEXITCODE -ne 0) { throw 'Failed to check out the requested release commit.' }
}
$releaseSha = (& git -C $releasePath rev-parse HEAD).Trim()
$releaseDirty = & git -C $releasePath status --porcelain
if ($releaseSha -ne $CommitSha -or $releaseDirty) {
    throw "Existing release snapshot is not a clean checkout of $CommitSha."
}

$guestEnv = Join-Path $runtimeDir "n0-$CommitSha.env"
[IO.File]::WriteAllText($guestEnv, "OMERTAOS_COMMIT_SHA=$CommitSha`n", [Text.UTF8Encoding]::new($false))

function Convert-ToComposePath([string]$Path) {
    return $Path.Replace('\', '/')
}

$composeEnv = Join-Path $runtimeDir "compose-$CommitSha.env"
$composeValues = @(
    "N0_IMAGE_TAG=$($CommitSha.Substring(0, 12))"
    "N0_RELEASE_PATH=$(Convert-ToComposePath $releasePath)"
    "N0_SSH_PUBLIC_KEY_FILE=$(Convert-ToComposePath $publicKeyPath)"
    "N0_GUEST_ENV_FILE=$(Convert-ToComposePath $guestEnv)"
    "N0_SSH_PORT=$SshPort"
)
[IO.File]::WriteAllLines($composeEnv, $composeValues, [Text.UTF8Encoding]::new($false))

$composeArgs = @('compose', '--env-file', $composeEnv, '-f', $composeFile)
& docker.exe @composeArgs config --quiet
if ($LASTEXITCODE -ne 0) { throw 'N0 simulation Compose configuration is invalid.' }
& docker.exe @composeArgs up --build --detach --wait --wait-timeout 300
if ($LASTEXITCODE -ne 0) { throw 'N0 simulation failed to become healthy.' }

& docker.exe @composeArgs exec -T acceptance-host /usr/local/sbin/omertaos-n0-sim-check
if ($LASTEXITCODE -ne 0) { throw 'N0 in-container acceptance check failed.' }

$sshArgs = @(
    '-i', $SshKeyPath,
    '-p', $SshPort,
    '-o', 'BatchMode=yes',
    '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=NUL',
    '-o', 'ConnectTimeout=10',
    'omerta@127.0.0.1'
)
$remoteCommand = @'
set -euo pipefail
. /etc/os-release
echo "os=$PRETTY_NAME"
echo "pid1=$(ps -p 1 -o comm=)"
echo "cgroup=$(stat -fc %T /sys/fs/cgroup)"
echo "ssh=$(sudo -n systemctl is-active ssh.service)"
echo "repo_sha=$(cat /var/lib/omertaos-n0/release-commit)"
echo "secret_dir=$(stat -c '%a:%U:%G' /etc/omertaos)"
echo "addresses=$(hostname -I | xargs)"
'@
$remoteEvidence = & ssh.exe @sshArgs $remoteCommand
if ($LASTEXITCODE -ne 0) { throw 'N0 SSH acceptance check failed.' }

$containerId = (& docker.exe @composeArgs ps -q acceptance-host).Trim()
$inspect = (& docker.exe inspect $containerId | ConvertFrom-Json)[0]
$result = [ordered]@{
    phase = 'N0-simulation'
    status = 'passed-simulated'
    validated_at = (Get-Date).ToString('o')
    commit = $CommitSha
    container_id = $containerId
    image = $inspect.Config.Image
    image_id = $inspect.Image
    ssh_endpoint = "127.0.0.1:$SshPort"
    ssh_private_key = $SshKeyPath
    network_internal = $true
    repo_read_only = $true
    hyperv_acceptance = 'not-run'
    reboot_acceptance = 'not-run'
    remote_evidence = @($remoteEvidence)
}
$evidencePath = Join-Path $evidenceDir "n0-simulation-$CommitSha.json"
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $evidencePath -Encoding utf8
$result | ConvertTo-Json -Depth 5
