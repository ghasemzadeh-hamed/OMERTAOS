from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "deploy" / "native" / "scripts"


def _script(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def test_n8_update_builds_an_immutable_versioned_release() -> None:
    text = _script("update.sh")
    for marker in (
        "--version VERSION",
        "--source PATH",
        "--backup PATH",
        "/opt/omertaos/releases",
        "/opt/omertaos/current",
        "/opt/omertaos/previous",
        "release.manifest.sha256",
        "sha256sum",
        "flock",
        "install-control.sh",
        "install-gateway.sh",
        "install-console.sh",
        "install-runtime.sh",
        '--venv "$staging/.venv/control"',
        '--dest "$staging/bin"',
        "release version or staging path already exists",
        "source worktree must be clean",
        "source_commit",
        "source_branch",
        "backup_manifest_sha256",
        "python3 --version",
        "node --version",
        "rustc --version",
    ):
        assert marker in text


def test_n8_update_requires_external_backup_before_forward_migrations() -> None:
    text = _script("update.sh")
    assert "backup must be external" in text
    assert text.index("verified external backup") < text.index("migrate-database.sh")
    assert "bootstrap-admin.sh" in text
    assert "Database changes remain forward-only" in text


def test_n8_activation_is_atomic_and_runs_post_switch_smoke() -> None:
    text = _script("update.sh")
    assert 'ln -s "$target" "$temporary"' in text
    assert 'mv -Tf "$temporary" "$link"' in text
    assert "systemctl stop omertaos.target" in text
    assert "systemctl start omertaos.target" in text
    assert "smoke-test.sh" in text
    assert "restore_previous" in text
    assert "systemctl disable" not in text


def test_n8_manifest_covers_every_release_file_and_is_checked_before_activation() -> None:
    text = _script("update.sh")
    assert "find . -type f" in text
    assert "sort -z | xargs -0 sha256sum" in text
    assert "sha256sum --check release.manifest.sha256" in text
    assert text.index("sha256sum --check release.manifest.sha256") < text.index("migrate-database.sh")


def test_n8_rollback_verifies_release_and_never_reverses_data() -> None:
    text = _script("rollback.sh")
    for marker in (
        "--check",
        "/opt/omertaos/releases",
        "/opt/omertaos/current",
        "/opt/omertaos/previous",
        "sha256sum --check",
        "flock",
        "mv -Tf",
        "restore_current",
        "no database downgrade was attempted",
    ):
        assert marker in text
    forbidden = (
        "systemctl disable",
        "prisma migrate reset",
        "prisma migrate down",
        "drop database",
        "drop table",
        "truncate table",
        "rm -rf",
    )
    assert not [marker for marker in forbidden if marker in text.lower()]


def test_n8_capo_entrypoints_are_thin_native_wrappers() -> None:
    for name in ("update.sh", "rollback.sh"):
        text = (REPO_ROOT / "deploy" / "CAPO" / "scripts" / name).read_text(encoding="utf-8")
        assert f"deploy/native/scripts/{name}" in text
        assert len(text.splitlines()) <= 7


def test_n8_systemd_consumes_only_the_active_release() -> None:
    systemd = REPO_ROOT / "deploy" / "native" / "systemd"
    combined = "\n".join(path.read_text(encoding="utf-8") for path in systemd.glob("*.service"))
    assert "/opt/omertaos/current" in combined
    assert "/opt/omertaos/OMERTAOS" not in combined
    assert "/var/lib/omertaos/bin/runtime-daemon" not in combined


def test_n4_n5_default_roots_match_the_active_release() -> None:
    for name in (
        "install-control.sh",
        "install-gateway.sh",
        "install-console.sh",
        "install-runtime.sh",
        "migrate-database.sh",
        "bootstrap-admin.sh",
    ):
        text = _script(name)
        assert "OMERTAOS_ROOT:-/opt/omertaos/current" in text
        assert "/opt/omertaos/OMERTAOS" not in text
