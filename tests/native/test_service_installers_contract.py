import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "deploy" / "native" / "scripts"
INSTALLERS = {
    name: SCRIPTS / f"install-{name}.sh"
    for name in ("control", "gateway", "console", "runtime")
}


def test_n4_has_four_independent_installers() -> None:
    assert all(path.is_file() for path in INSTALLERS.values())
    for name, path in INSTALLERS.items():
        text = path.read_text(encoding="utf-8")
        assert "set -euo pipefail" in text
        assert "--dry-run" in text and "--check" in text
        assert "no service" in text.lower() or "never started" in text.lower() or "no migration" in text.lower()
        assert name.title() in text or name.capitalize() in text


def test_build_tools_execute_as_non_root_service_account() -> None:
    helper = (SCRIPTS / "_install-lib.sh").read_text(encoding="utf-8")
    assert "runuser -u omertaos" in helper
    assert "omertaos must not be root" in helper
    assert "HOME=/var/lib/omertaos" in helper
    for name in INSTALLERS:
        assert "native_prepare_runner" in INSTALLERS[name].read_text(encoding="utf-8")


def test_gateway_and_console_require_committed_locks() -> None:
    gateway = INSTALLERS["gateway"].read_text(encoding="utf-8")
    console = INSTALLERS["console"].read_text(encoding="utf-8")
    assert "package-lock.json is required" in gateway
    assert "npm ci" in gateway and "npm install" not in gateway
    assert "--frozen-lockfile" in console
    assert (REPO_ROOT / "gateway" / "package-lock.json").is_file()
    lock = json.loads((REPO_ROOT / "gateway" / "package-lock.json").read_text(encoding="utf-8"))
    assert lock["lockfileVersion"] == 3
    assert lock["packages"][""]["name"] == "aion-gateway"
    console_package = json.loads((REPO_ROOT / "console" / "package.json").read_text(encoding="utf-8"))
    assert console_package["packageManager"] == "pnpm@11.13.1"
    build_policy = (REPO_ROOT / "console" / "pnpm-workspace.yaml").read_text(encoding="utf-8")
    for dependency in ("@prisma/client", "@prisma/engines", "bcrypt", "esbuild", "prisma", "unrs-resolver"):
        assert dependency in build_policy


def test_control_does_not_run_database_install_phase() -> None:
    text = INSTALLERS["control"].read_text(encoding="utf-8").lower()
    assert "pip check" in text
    for forbidden in ("prisma migrate", "alembic", "create table", "bootstrap-admin", "systemctl"):
        assert forbidden not in text


def test_runtime_requires_locked_release_build_outside_source_tree() -> None:
    text = INSTALLERS["runtime"].read_text(encoding="utf-8")
    lock_path = REPO_ROOT / "runtime-daemon" / "Cargo.lock"
    assert lock_path.is_file()
    lock = lock_path.read_text(encoding="utf-8")
    assert "version = 4" in lock
    assert "registry+https://github.com/rust-lang/crates.io-index" in lock
    assert "source = \"git+" not in lock
    assert "Cargo.lock is required" in text
    assert "cargo build --locked --release" in text
    assert "CARGO_TARGET_DIR" in text
    assert "/var/lib/omertaos/build/runtime" in text
    assert "systemctl" not in text


def test_installers_verify_expected_artifacts() -> None:
    expected = {
        "control": ("bin/uvicorn", "control.app.main"),
        "gateway": ("dist/server.js", "npm ls"),
        "console": (".next/BUILD_ID", "node_modules/.bin/next", "scripts/dist/bootstrap-admin.js"),
        "runtime": ("release/runtime-daemon", "DEST/runtime-daemon"),
    }
    for name, markers in expected.items():
        text = INSTALLERS[name].read_text(encoding="utf-8")
        assert all(marker in text for marker in markers)


def test_legacy_and_capo_entrypoints_are_thin_wrappers() -> None:
    legacy = {
        "install-python-control.sh": "install-control.sh",
        "install-node-services.sh": "install-gateway.sh",
        "install-rust-runtime.sh": "install-runtime.sh",
    }
    for wrapper, target in legacy.items():
        text = (SCRIPTS / wrapper).read_text(encoding="utf-8")
        assert target in text
        assert len(text.splitlines()) <= 7
    for name in INSTALLERS:
        text = (REPO_ROOT / "deploy" / "CAPO" / "scripts" / f"install-{name}.sh").read_text(encoding="utf-8")
        assert f"deploy/native/scripts/install-{name}.sh" in text
        assert len(text.splitlines()) <= 7


def test_n4_installers_never_start_services_or_touch_schema() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in INSTALLERS.values())
    for forbidden in (
        "prisma migrate",
        "alembic upgrade",
        "create table",
        "drop table",
        "truncate table",
    ):
        assert forbidden not in combined
    assert not re.search(r"(?m)^\s*systemctl\s+(start|enable|restart)\b", combined)
    assert not re.search(r"(?m)^\s*service\s+\S+\s+(start|restart)\b", combined)
