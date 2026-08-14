[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-f]{40}$')]
    [string]$CommitSha,
    [Parameter(Mandatory = $true)]
    [string]$ImageArchive,
    [Parameter(Mandatory = $true)]
    [string]$SshPublicKey,
    [string]$VmName = 'OMERTAOS-N0',
    [string]$VmRoot = 'E:\Hyper-V\OMERTAOS-N0',
    [string]$SwitchName = 'Default Switch',
    [string]$RepositoryUrl = 'https://github.com/Hamedghz/OMERTAOS.git',
    [string]$ExpectedImageSha256 = '198e71366f7e54008f8c0ff3235cbf9fb0a86c8ea32bcfd534075e5e912ec78e',
    [ValidateRange(5, 60)]
    [int]$WaitMinutes = 20
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'N0 Hyper-V provisioning requires an elevated PowerShell session.'
}

foreach ($command in 'Get-VM', 'New-VM', 'New-VHD', 'Convert-VHD', 'Checkpoint-VM') {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Required Hyper-V command is unavailable: $command"
    }
}

$archivePath = (Resolve-Path -LiteralPath $ImageArchive).Path
$publicKeyPath = (Resolve-Path -LiteralPath $SshPublicKey).Path
$privateKeyPath = $publicKeyPath -replace '\.pub$', ''
if (-not (Test-Path -LiteralPath $privateKeyPath -PathType Leaf)) {
    throw "Matching SSH private key is missing: $privateKeyPath"
}

$actualImageSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $archivePath).Hash.ToLowerInvariant()
if ($actualImageSha256 -ne $ExpectedImageSha256.ToLowerInvariant()) {
    throw "Ubuntu image checksum mismatch: $actualImageSha256"
}
if (Get-VM -Name $VmName -ErrorAction SilentlyContinue) {
    throw "VM '$VmName' already exists. N0 will not replace or delete an existing VM."
}
if (-not (Get-VMSwitch -Name $SwitchName -ErrorAction SilentlyContinue)) {
    throw "Required restricted Hyper-V switch '$SwitchName' does not exist."
}

$sourceDir = Join-Path $VmRoot 'source'
$diskDir = Join-Path $VmRoot 'disks'
$seedDir = Join-Path $VmRoot 'seed'
$evidenceDir = Join-Path $VmRoot 'evidence'
foreach ($path in $VmRoot, $sourceDir, $diskDir, $seedDir, $evidenceDir) {
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

$sourceVhd = Get-ChildItem -LiteralPath $sourceDir -Filter '*.vhd' -File -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $sourceVhd) {
    & tar.exe -xzf $archivePath -C $sourceDir
    if ($LASTEXITCODE -ne 0) { throw "Ubuntu VHD extraction failed with exit code $LASTEXITCODE" }
    $sourceVhd = Get-ChildItem -LiteralPath $sourceDir -Filter '*.vhd' -File | Select-Object -First 1
}
if (-not $sourceVhd) { throw 'The verified Ubuntu archive did not contain a VHD.' }

$osDisk = Join-Path $diskDir 'omertaos-n0-os.vhdx'
if (Test-Path -LiteralPath $osDisk) {
    throw "Destination OS disk already exists and will not be overwritten: $osDisk"
}
Convert-VHD -Path $sourceVhd.FullName -DestinationPath $osDisk -VHDType Dynamic
Resize-VHD -Path $osDisk -SizeBytes 100GB

$publicKey = (Get-Content -Raw -LiteralPath $publicKeyPath).Trim()
if ($publicKey -notmatch '^ssh-(ed25519|rsa)\s+') { throw 'Unsupported SSH public key format.' }

$metaData = @"
instance-id: omertaos-n0-$($CommitSha.Substring(0, 12))
local-hostname: omertaos-n0
"@

$userData = @"
#cloud-config
hostname: omertaos-n0
manage_etc_hosts: true
ssh_pwauth: false
disable_root: true
users:
  - name: omerta
    gecos: OMERTAOS Acceptance Operator
    groups: [adm, sudo]
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    lock_passwd: true
    ssh_authorized_keys:
      - $publicKey
package_update: true
packages:
  - ca-certificates
  - git
  - openssh-server
  - ufw
write_files:
  - path: /usr/local/sbin/omertaos-n0-bootstrap
    owner: root:root
    permissions: '0755'
    content: |
      #!/usr/bin/env bash
      set -euo pipefail
      install -d -m 0750 -o root -g root /etc/omertaos
      install -d -m 0755 -o root -g root /srv/omertaos-source
      if [[ ! -d /srv/omertaos-source/.git ]]; then
        git clone --filter=blob:none --no-checkout '$RepositoryUrl' /srv/omertaos-source
      fi
      git -C /srv/omertaos-source fetch --depth=1 origin '$CommitSha'
      git -C /srv/omertaos-source checkout --detach '$CommitSha'
      test "`$(git -C /srv/omertaos-source rev-parse HEAD)" = '$CommitSha'
      printf '%s\n' '$CommitSha' >/var/lib/omertaos-n0-release-commit
      chmod 0644 /var/lib/omertaos-n0-release-commit
      ufw default deny incoming
      ufw default allow outgoing
      ufw limit OpenSSH
      ufw --force enable
      systemctl enable --now ssh
      install -d -m 0755 -o root -g root /var/lib/omertaos-n0
      date --iso-8601=seconds >/var/lib/omertaos-n0/ready
runcmd:
  - [bash, /usr/local/sbin/omertaos-n0-bootstrap]
final_message: OMERTAOS N0 cloud-init completed
"@

$metaPath = Join-Path $seedDir 'meta-data'
$userPath = Join-Path $seedDir 'user-data'
[IO.File]::WriteAllText($metaPath, $metaData, [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($userPath, $userData, [Text.UTF8Encoding]::new($false))

$seedDisk = Join-Path $diskDir 'omertaos-n0-cidata.vhdx'
if (Test-Path -LiteralPath $seedDisk) {
    throw "Destination seed disk already exists and will not be overwritten: $seedDisk"
}
New-VHD -Path $seedDisk -Dynamic -SizeBytes 128MB | Out-Null
$mounted = $false
try {
    $disk = Mount-VHD -Path $seedDisk -Passthru | Get-Disk
    $mounted = $true
    Initialize-Disk -Number $disk.Number -PartitionStyle MBR | Out-Null
    $partition = New-Partition -DiskNumber $disk.Number -UseMaximumSize -AssignDriveLetter
    Format-Volume -Partition $partition -FileSystem FAT32 -NewFileSystemLabel 'cidata' -Confirm:$false | Out-Null
    $seedRoot = "$($partition.DriveLetter):\"
    Copy-Item -LiteralPath $metaPath, $userPath -Destination $seedRoot
}
finally {
    if ($mounted) { Dismount-VHD -Path $seedDisk }
}

$vm = New-VM -Name $VmName -Generation 2 -MemoryStartupBytes 8GB -VHDPath $osDisk -Path $VmRoot -SwitchName $SwitchName
Set-VMProcessor -VMName $VmName -Count 4
Set-VMMemory -VMName $VmName -DynamicMemoryEnabled $false -StartupBytes 8GB
Set-VM -VMName $VmName -AutomaticCheckpointsEnabled $false -AutomaticStartAction Nothing -AutomaticStopAction ShutDown
Set-VMFirmware -VMName $VmName -EnableSecureBoot On -SecureBootTemplate MicrosoftUEFICertificateAuthority
Add-VMHardDiskDrive -VMName $VmName -ControllerType SCSI -Path $seedDisk | Out-Null
Start-VM -Name $VmName | Out-Null

$deadline = (Get-Date).AddMinutes($WaitMinutes)
$ipAddress = $null
while ((Get-Date) -lt $deadline) {
    $ipAddress = Get-VMNetworkAdapter -VMName $VmName | ForEach-Object IPAddresses |
        Where-Object { $_ -match '^\d{1,3}(\.\d{1,3}){3}$' -and $_ -notmatch '^169\.254\.' } |
        Select-Object -First 1
    if ($ipAddress -and (Test-NetConnection -ComputerName $ipAddress -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue)) { break }
    Start-Sleep -Seconds 10
}
if (-not $ipAddress) { throw "VM did not expose an IPv4 address within $WaitMinutes minutes." }

$sshCommon = @(
    '-i', $privateKeyPath,
    '-o', 'BatchMode=yes',
    '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=NUL',
    '-o', 'ConnectTimeout=10',
    "omerta@$ipAddress"
)
& ssh.exe @sshCommon 'cloud-init status --wait'
if ($LASTEXITCODE -ne 0) { throw "cloud-init failed or SSH was unavailable (exit $LASTEXITCODE)." }

$remoteCheck = @'
set -euo pipefail
. /etc/os-release
test "$VERSION_ID" = "24.04"
test "$(ps -p 1 -o comm=)" = "systemd"
test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs"
systemctl is-active --quiet ssh
test "$(git -C /srv/omertaos-source rev-parse HEAD)" = "__COMMIT__"
test "$(stat -c '%a:%U:%G' /etc/omertaos)" = "750:root:root"
test -f /var/lib/omertaos-n0/ready
echo "os=$PRETTY_NAME"
echo "pid1=$(ps -p 1 -o comm=)"
echo "cgroup=$(stat -fc %T /sys/fs/cgroup)"
echo "ssh=$(systemctl is-active ssh)"
echo "firewall=$(sudo ufw status | sed -n '1p')"
echo "repo_sha=$(git -C /srv/omertaos-source rev-parse HEAD)"
echo "secret_dir=$(stat -c '%a:%U:%G' /etc/omertaos)"
echo "root_bytes=$(df -B1 --output=size / | tail -1 | tr -d ' ')"
echo "addresses=$(hostname -I | xargs)"
'@.Replace('__COMMIT__', $CommitSha)
$remoteEvidence = & ssh.exe @sshCommon $remoteCheck
if ($LASTEXITCODE -ne 0) { throw "N0 remote validation failed with exit code $LASTEXITCODE." }

$checkpointName = "N0-base-validated-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Checkpoint-VM -Name $VmName -SnapshotName $checkpointName

$vhd = Get-VHD -Path $osDisk
$network = Get-VMNetworkAdapter -VMName $VmName
$result = [ordered]@{
    phase = 'N0'
    status = 'passed'
    validated_at = (Get-Date).ToString('o')
    vm_name = $VmName
    vm_generation = $vm.Generation
    processors = (Get-VMProcessor -VMName $VmName).Count
    memory_bytes = (Get-VMMemory -VMName $VmName).Startup
    disk_maximum_bytes = $vhd.Size
    disk_type = $vhd.VhdType.ToString()
    switch = $network.SwitchName
    ipv4 = $ipAddress
    checkpoint = $checkpointName
    ubuntu_archive_sha256 = $actualImageSha256
    repository_commit = $CommitSha
    ssh_private_key = $privateKeyPath
    remote_evidence = @($remoteEvidence)
}
$evidencePath = Join-Path $evidenceDir 'n0-result.json'
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $evidencePath -Encoding utf8
$result | ConvertTo-Json -Depth 5
