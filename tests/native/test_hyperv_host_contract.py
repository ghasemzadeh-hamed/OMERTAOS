from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROVISIONER = ROOT / "deploy/native/host/New-OmertaN0Host.ps1"


def test_n0_provisioner_is_fail_closed_and_reproducible() -> None:
    text = PROVISIONER.read_text(encoding="utf-8")

    assert "requires an elevated PowerShell session" in text
    assert "already exists. N0 will not replace or delete" in text
    assert "Get-FileHash -Algorithm SHA256" in text
    assert "Ubuntu image checksum mismatch" in text
    assert "ExpectedImageSha256" in text
    assert "Remove-VM" not in text
    assert "Remove-VHD" not in text
    assert "Remove-Item" not in text


def test_n0_host_resource_and_network_contract() -> None:
    text = PROVISIONER.read_text(encoding="utf-8")

    assert "-Generation 2" in text
    assert "-MemoryStartupBytes 8GB" in text
    assert "-Count 4" in text
    assert "-SizeBytes 100GB" in text
    assert "DynamicMemoryEnabled $false" in text
    assert "Default Switch" in text
    assert "ufw default deny incoming" in text
    assert "ufw limit OpenSSH" in text
    assert "AutomaticCheckpointsEnabled $false" in text


def test_n0_cloud_init_and_acceptance_contract() -> None:
    text = PROVISIONER.read_text(encoding="utf-8")

    assert "ssh_pwauth: false" in text
    assert "lock_passwd: true" in text
    assert "NewFileSystemLabel 'cidata'" in text
    assert "install -d -m 0750 -o root -g root /etc/omertaos" in text
    assert "stat -fc %T /sys/fs/cgroup" in text
    assert "cgroup2fs" in text
    assert "cloud-init status --wait" in text
    assert "git -C /srv/omertaos-source rev-parse HEAD" in text
    assert "Checkpoint-VM" in text
    assert "N0-base-validated" in text
    assert "password:" not in text.lower()
