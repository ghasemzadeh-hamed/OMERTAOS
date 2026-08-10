from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "deploy/native/host-sim"


def read(name: str) -> str:
    return (SIM / name).read_text(encoding="utf-8")


def test_simulation_runs_systemd_and_preserves_native_boundaries() -> None:
    dockerfile = read("Dockerfile")
    compose = read("compose.yml")
    check = read("check.sh")

    assert 'FROM ubuntu:24.04' in dockerfile
    assert 'CMD ["/sbin/init"]' in dockerfile
    assert "privileged: true" in compose
    assert "cgroup: host" in compose
    assert "/sys/fs/cgroup:/sys/fs/cgroup:rw" in compose
    assert "stat -fc %T /sys/fs/cgroup" in check
    assert "cgroup2fs" in check
    assert "ps -p 1 -o comm=" in check


def test_simulation_network_and_secret_contract() -> None:
    compose = read("compose.yml")
    bootstrap = read("bootstrap.sh")

    assert "127.0.0.1:${N0_SSH_PORT:-2222}:2222" in compose
    assert "internal: true" in compose
    assert "ssh-relay:" in compose
    assert "no-new-privileges:true" in compose
    assert "cap_drop:" in compose
    assert "/srv/omertaos-source:ro" in compose
    assert "/run/n0/authorized_key:ro" in compose
    assert "install -d -m 0750 -o root -g root /etc/omertaos" in bootstrap
    assert "install -d -m 0755 -o root -g root /run/sshd" in bootstrap
    assert "passwd -d" not in read("Dockerfile")
    assert "password:" not in (compose + bootstrap).lower()


def test_simulation_is_validated_over_ssh_and_remains_running() -> None:
    invoke = read("Invoke-N0Simulation.ps1")

    assert "docker.exe @composeArgs config --quiet" in invoke
    assert "up --build --detach --wait" in invoke
    assert "omerta@127.0.0.1" in invoke
    assert "sudo -n systemctl is-active ssh.service" in invoke
    assert "status = 'passed-simulated'" in invoke
    assert "hyperv_acceptance = 'not-run'" in invoke
    assert "reboot_acceptance = 'not-run'" in invoke
    assert "down" not in invoke.lower()
    assert "Remove-" not in invoke
