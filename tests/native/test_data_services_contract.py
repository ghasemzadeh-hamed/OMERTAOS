import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
NATIVE = REPO_ROOT / "deploy" / "native"
ENV_DIR = NATIVE / "env"
INSTALLER = NATIVE / "scripts" / "install-data-services.sh"
SPEC = importlib.util.spec_from_file_location("native_data_validator", ENV_DIR / "validate_data_env.py")
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def _render_environment(tmp_path: Path, control_password: str, console_password: str) -> tuple[Path, Path, Path]:
    installer = tmp_path / "installer.env"
    control = tmp_path / "control.env"
    console = tmp_path / "console.env"
    installer.write_text(
        (ENV_DIR / "installer.env.example").read_text(encoding="utf-8")
        .replace("OMERTAOS_POSTGRES_PASSWORD=CHANGE_ME", f"OMERTAOS_POSTGRES_PASSWORD={control_password}")
        .replace("OMERTAOS_CONSOLE_POSTGRES_PASSWORD=CHANGE_ME", f"OMERTAOS_CONSOLE_POSTGRES_PASSWORD={console_password}"),
        encoding="utf-8",
    )
    control.write_text(
        (ENV_DIR / "control.env.example").read_text(encoding="utf-8")
        .replace("postgresql://omertaos:CHANGE_ME@", f"postgresql://omertaos:{control_password}@"),
        encoding="utf-8",
    )
    console.write_text(
        (ENV_DIR / "console.env.example").read_text(encoding="utf-8")
        .replace("postgresql://omertaos_console:CHANGE_ME@", f"postgresql://omertaos_console:{console_password}@"),
        encoding="utf-8",
    )
    return installer, control, console


def test_example_data_credentials_match_service_dsns() -> None:
    assert VALIDATOR.validate_data_environment(
        ENV_DIR / "installer.env.example",
        ENV_DIR / "control.env.example",
        ENV_DIR / "console.env.example",
        examples=True,
    ) == []


def test_rendered_credentials_are_distinct_and_match_dsns(tmp_path: Path) -> None:
    paths = _render_environment(tmp_path, "control-secret-1234", "console-secret-5678")
    assert VALIDATOR.validate_data_environment(*paths, check_permissions=False) == []


def test_data_validator_rejects_weak_or_mismatched_credentials(tmp_path: Path) -> None:
    paths = _render_environment(tmp_path, "short", "console-secret-5678")
    errors = VALIDATOR.validate_data_environment(*paths, check_permissions=False)
    assert any("at least 16" in error for error in errors)

    installer, control, console = _render_environment(tmp_path, "control-secret-1234", "console-secret-5678")
    console.write_text(console.read_text(encoding="utf-8").replace("omertaos_console", "wrong_database", 1), encoding="utf-8")
    errors = VALIDATOR.validate_data_environment(installer, control, console, check_permissions=False)
    assert any("Console PostgreSQL DSN does not match" in error for error in errors)


def test_installer_uses_split_secret_contract_without_sourcing_it() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    assert "/etc/omertaos/installer.env" in text
    assert "validate_data_env.py" in text
    assert "source \"$INSTALLER_ENV\"" not in text
    assert "CONFIG[\"$key\"]" in text
    assert "run as root" in text


def test_installer_provisions_distinct_roles_idempotently() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    assert "OMERTAOS_POSTGRES_ROLE" in text
    assert "OMERTAOS_CONSOLE_POSTGRES_ROLE" in text
    assert "WHERE NOT EXISTS (SELECT 1 FROM pg_roles" in text
    assert "WHERE NOT EXISTS (SELECT 1 FROM pg_database" in text
    assert text.count("PGPASSWORD=\"$password\"") == 2
    assert "ALTER ROLE" not in text
    assert "ALTER DATABASE" not in text
    assert "\\getenv" not in text
    assert "--set=role_password" not in text


def test_n3_has_read_only_check_and_no_schema_or_destructive_sql() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    assert "--check" in text
    assert "check_database" in text
    lowered = text.lower()
    for forbidden in ("drop ", "truncate ", "delete from", "create table", "prisma migrate", "alembic"):
        assert forbidden not in lowered


def test_data_services_are_loopback_health_checked_and_persistent() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    for marker in ("127.0.0.1", "pg_isready", "redis-cli", "CONFIG GET save", "check_loopback_listener"):
        assert marker in text
    assert "systemctl enable --now postgresql.service" in text
    assert "systemctl enable --now redis-server.service" in text


def test_package_install_cannot_auto_start_unvalidated_services() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    assert "OMERTAOS N3 temporary no-start policy" in text
    assert "exit 101" in text
    assert "validate_postgres_bind" in text
    assert "validate_redis_bind" in text
    assert "protected-mode" in text
    assert text.index("\nvalidate_postgres_bind\nvalidate_redis_bind\n") < text.rindex("systemctl enable --now postgresql.service")


def test_capo_data_entrypoint_delegates_to_native_owner() -> None:
    wrapper = (REPO_ROOT / "deploy" / "CAPO" / "scripts" / "install-data-services.sh").read_text(encoding="utf-8")
    assert "deploy/native/scripts/install-data-services.sh" in wrapper
    assert len(wrapper.splitlines()) <= 8
