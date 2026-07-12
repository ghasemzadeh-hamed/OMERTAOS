from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_legacy_runtime_binary_delegates_to_canonical_crate() -> None:
    manifest = _read("rust-runtime/Cargo.toml")
    main = _read("rust-runtime/src/main.rs")

    assert 'runtime-daemon = { path = "../runtime-daemon" }' in manifest
    assert "runtime_daemon::run().await" in main
    assert "ctrl_c" not in main


def test_canonical_runtime_build_uses_vendored_protoc() -> None:
    manifest = _read("runtime-daemon/Cargo.toml")
    build = _read("runtime-daemon/build.rs")

    assert 'protoc-bin-vendored = "3"' in manifest
    assert "protoc_bin_vendored::protoc_bin_path" in build
    assert 'std::env::set_var("PROTOC", protoc)' in build


def test_incomplete_sandbox_sources_fail_closed() -> None:
    sources = {
        "runtime-daemon/src/sandbox/namespace.rs": "namespace isolation backend is not implemented",
        "runtime-daemon/src/sandbox/mount.rs": "mount isolation backend is not implemented",
        "runtime-daemon/src/sandbox/seccomp.rs": "seccomp backend is not implemented",
        "runtime-daemon/src/sandbox/process.rs": "isolated process backend is not implemented",
    }

    for path, error in sources.items():
        source = _read(path)
        assert "anyhow::bail!" in source
        assert error in source

    assert "Pid::from_raw(1)" not in _read("runtime-daemon/src/sandbox/process.rs")


def test_canonical_runtime_exposes_one_shared_run_function() -> None:
    library = _read("runtime-daemon/src/lib.rs")
    binary = _read("runtime-daemon/src/main.rs")

    assert "pub async fn run()" in library
    assert "runtime_daemon::run().await" in binary


def test_execution_runtime_contract_is_compatibility_only() -> None:
    source = _read("execution/runtime_contract.py")

    assert "from control.clients.runtime import RuntimeEnvelope, RuntimeExecutor" in source
    assert "RuntimeCommand = RuntimeEnvelope" in source
    assert "class RuntimeCommand" not in source
    assert "subprocess" not in source

    python_sources = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "execution").rglob("*.py")
    )
    assert python_sources == ["execution/runtime_contract.py"]
