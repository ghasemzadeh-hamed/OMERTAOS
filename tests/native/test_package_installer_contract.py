from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
NATIVE = REPO_ROOT / "deploy" / "native"
INSTALLER = NATIVE / "scripts" / "install-os-packages.sh"
PREFLIGHT = NATIVE / "scripts" / "preflight.sh"
MANIFEST = NATIVE / "packages" / "apt-build-packages.txt"


def _packages() -> set[str]:
    return {
        line.split("#", 1)[0].strip()
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.split("#", 1)[0].strip()
    }


def test_manifest_has_build_clients_but_no_n3_servers() -> None:
    packages = _packages()
    assert {
        "python3",
        "nodejs",
        "cargo",
        "rustc",
        "postgresql-client",
        "redis-tools",
        "rsync",
        "util-linux",
    } <= packages
    assert not ({"postgresql", "redis-server", "docker.io", "podman"} & packages)


def test_preflight_is_read_only_and_enforces_native_baseline() -> None:
    text = PREFLIGHT.read_text(encoding="utf-8")
    for marker in ("debian:12", "ubuntu:22.04", "ubuntu:24.04", "x86_64|aarch64", "cgroup.controllers", "systemd", "5 GiB"):
        assert marker in text
    for mutation in ("apt-get install", "useradd ", "systemctl ", "service "):
        assert mutation not in text


def test_installer_is_idempotent_previewable_and_version_gated() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    for marker in ("set -euo pipefail", "--dry-run", "--check", "dpkg-query", "apt-cache policy", "apt-get install", "Python", "Node 22", "corepack"):
        assert marker in text
    assert "${missing[@]}" in text
    assert "systemctl" not in text
    assert "service start" not in text
    assert "rsync flock" in text


def test_installer_preserves_state_and_creates_n1_paths() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    for path in ("/etc/omertaos", "/var/lib/omertaos", "/var/log/omertaos", "/var/lib/omertaos/backups"):
        assert path in text
    lowered = text.lower()
    for destructive in ("rm -rf", "drop ", "truncate ", "mkfs", "wipefs"):
        assert destructive not in lowered


def test_capo_package_entrypoint_delegates_to_native_owner() -> None:
    wrapper = (REPO_ROOT / "deploy" / "CAPO" / "scripts" / "install-os-packages.sh").read_text(encoding="utf-8")
    assert "deploy/native/scripts/install-os-packages.sh" in wrapper
    assert len(wrapper.splitlines()) <= 8
