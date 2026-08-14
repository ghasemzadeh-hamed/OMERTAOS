from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "deploy" / "native" / "scripts"


def test_backup_is_external_versioned_and_manifest_verified() -> None:
    text = (SCRIPTS / "backup.sh").read_text(encoding="utf-8")
    for marker in ("--dest", "pg_dump --format=custom", "redis.rdb", "config.tar.gz", "backup.metadata", "backup.manifest.sha256", "sha256sum --check"):
        assert marker in text
    for forbidden in ("rm -rf", "drop database", "truncate table"):
        assert forbidden not in text.lower()


def test_restore_defaults_to_read_only_verification() -> None:
    text = (SCRIPTS / "restore.sh").read_text(encoding="utf-8")
    for marker in ("sha256sum --check", "pg_restore --list", "Redis backup header", "tar --list", "--apply"):
        assert marker in text
    assert "no restore was applied" in text
    assert "no destructive replacement was attempted" in text
    assert "drop database" not in text.lower()


def test_update_requires_canonical_restore_verification() -> None:
    text = (SCRIPTS / "update.sh").read_text(encoding="utf-8")
    assert 'restore.sh" --backup "$BACKUP"' in text
    assert text.index('restore.sh" --backup "$BACKUP"') < text.index("migrate-database.sh")


def test_capo_backup_restore_are_thin_wrappers() -> None:
    for name in ("backup.sh", "restore.sh"):
        text = (ROOT / "deploy" / "CAPO" / "scripts" / name).read_text(encoding="utf-8")
        assert f"deploy/native/scripts/{name}" in text
        assert len(text.splitlines()) <= 7
