from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
NATIVE_SCRIPTS = REPO_ROOT / "deploy" / "native" / "scripts"
MIGRATE = NATIVE_SCRIPTS / "migrate-database.sh"
BOOTSTRAP = NATIVE_SCRIPTS / "bootstrap-admin.sh"


def test_n5_has_separate_migration_and_bootstrap_entrypoints() -> None:
    migration = MIGRATE.read_text(encoding="utf-8")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    assert "control.app.network.migrate" in migration
    assert "prisma migrate deploy" in migration
    assert "prisma migrate status" in migration
    assert "bootstrap-admin.js" in bootstrap
    assert "CONSOLE_BOOTSTRAP_CHECK" in bootstrap
    assert "--dry-run" in migration and "--check" in migration
    assert "--dry-run" in bootstrap and "--check" in bootstrap


def test_n5_never_sources_secrets_or_prints_database_urls() -> None:
    combined = MIGRATE.read_text(encoding="utf-8") + BOOTSTRAP.read_text(encoding="utf-8")
    assert "source \"$CONTROL_ENV\"" not in combined
    assert "source \"$CONSOLE_ENV\"" not in combined
    assert "source \"$INSTALLER_ENV\"" not in combined
    assert "<redacted>" in combined
    assert "admin123" in combined
    assert "!= admin123" in combined


def test_committed_migrations_are_additive() -> None:
    sql = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in sorted((REPO_ROOT / "console" / "prisma" / "migrations").glob("*/migration.sql"))
    )
    for forbidden in ("drop table", "drop database", "truncate table", "delete from"):
        assert forbidden not in sql


def test_control_schema_has_explicit_idempotent_migration() -> None:
    migration = (REPO_ROOT / "control" / "app" / "network" / "migrate.py").read_text(encoding="utf-8")
    assert "Base.metadata.create_all" in migration
    assert "--check" in migration
    assert "drop_all" not in migration


def test_bootstrap_requires_explicit_strong_credentials_and_never_rotates() -> None:
    source = (REPO_ROOT / "console" / "scripts" / "bootstrap-admin.ts").read_text(encoding="utf-8")
    assert "password.length < 16" in source
    assert "password === 'admin123'" in source
    assert "user.count()" in source
    assert "findUnique" in source
    assert "user.update" not in source
    assert "user.upsert" not in source


def test_first_boot_prepares_host_then_delegates_release_activation_to_n8() -> None:
    text = (NATIVE_SCRIPTS / "first-boot.sh").read_text(encoding="utf-8")
    assert "--version VERSION" in text
    assert "--backup PATH" in text
    assert text.index("install-os-packages.sh") < text.index("install-data-services.sh")
    assert text.index("install-data-services.sh") < text.index('"$SCRIPT_DIR/update.sh"')
    for duplicate in (
        "install-control.sh",
        "install-gateway.sh",
        "install-console.sh",
        "install-runtime.sh",
        "migrate-database.sh",
        "bootstrap-admin.sh",
        "install-systemd.sh",
    ):
        assert duplicate not in text

    wrapper = (REPO_ROOT / "deploy" / "CAPO" / "scripts" / "first-boot.sh").read_text(encoding="utf-8")
    assert "deploy/native/scripts/first-boot.sh" in wrapper
    assert len(wrapper.splitlines()) <= 7


def test_capo_n5_entrypoints_delegate_to_native_owner() -> None:
    for name in ("migrate-database.sh", "bootstrap-admin.sh"):
        wrapper = (REPO_ROOT / "deploy" / "CAPO" / "scripts" / name).read_text(encoding="utf-8")
        assert f"deploy/native/scripts/{name}" in wrapper
        assert len(wrapper.splitlines()) <= 7
