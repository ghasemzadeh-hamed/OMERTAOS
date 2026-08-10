from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "deploy/native/scripts/validate-environment.sh"
INVOKER = ROOT / "deploy/native/host-sim/Invoke-N1Simulation.ps1"


def test_n1_host_validator_is_read_only() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")

    for forbidden in ("apt-get", "useradd", "mkdir ", "install -d", "systemctl enable", "systemctl start"):
        assert forbidden not in text
    assert "--mode native|simulation" in text
    assert "expected commit must be a full Git SHA" in text


def test_n1_validates_current_host_boundaries() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")

    assert "systemd must be PID 1" in text
    assert "cgroups v2 is required" in text
    assert "750:root:root" in text
    assert "acceptance release clone is dirty" in text
    assert "3000 5432 6379 8000 8080 50051" in text
    assert "canonical pre-install port is already occupied" in text
    assert "Node 22 LTS is required" in text
    assert "3.11|3.12" in text


def test_n1_defers_later_phase_ownership_explicitly() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    invoker = INVOKER.read_text(encoding="utf-8")

    assert "service-user-to-N2" in text
    assert "python-3.11-or-3.12-to-N2" in text
    assert "node-22-to-N2" in text
    assert "rust-stable-to-N2/N4" in text
    assert "package_installation = 'deferred-to-N2'" in invoker
    assert "runtime_build = 'deferred-to-N4'" in invoker
    assert "hyperv_acceptance = 'not-run'" in invoker
