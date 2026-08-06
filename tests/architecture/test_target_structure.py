from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_required_top_level_directories_exist() -> None:
    required = {
        "console",
        "gateway",
        "control",
        "runtime-daemon",
        "registry",
        "data",
        "policies",
        "schemas",
        "shared",
        "deploy",
        "integrations",
        "tests",
    }
    existing = {p.name for p in REPO_ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")}
    missing = sorted(required - existing)
    assert not missing, f"missing required top-level directories: {missing}"


def test_canonical_runtime_security_layout() -> None:
    expected = [
        "runtime-daemon/Cargo.toml",
        "runtime-daemon/src/server.rs",
        "runtime-daemon/src/security/capability.rs",
        "runtime-daemon/src/sandbox/namespace.rs",
        "runtime-daemon/src/sandbox/seccomp.rs",
        "runtime-daemon/src/isolation/cpu.rs",
        "runtime-daemon/src/isolation/memory.rs",
    ]
    missing = [p for p in expected if not (REPO_ROOT / p).exists()]
    assert not missing, f"missing rust runtime segmented components: {missing}"
