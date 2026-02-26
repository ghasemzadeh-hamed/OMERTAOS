from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_required_top_level_directories_exist() -> None:
    required = {
        "rust-runtime",
        "control-plane",
        "domain",
        "orchestration",
        "execution",
        "gateway",
        "registry",
        "database",
        "policies",
        "observability",
        "schemas",
        "agents",
        "models",
        "algorithms",
        "ui",
        "config",
        "tests",
    }
    existing = {p.name for p in REPO_ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")}
    missing = sorted(required - existing)
    assert not missing, f"missing required top-level directories: {missing}"


def test_rust_runtime_segmented_layout() -> None:
    expected = [
        "rust-runtime/kernel-adapter",
        "rust-runtime/sandbox",
        "rust-runtime/terminal-bridge",
        "rust-runtime/resource-isolation",
    ]
    missing = [p for p in expected if not (REPO_ROOT / p).exists()]
    assert not missing, f"missing rust runtime segmented components: {missing}"
