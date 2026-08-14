from sqlalchemy import create_engine

from control.app.network.migrate import apply_schema, missing_tables


def test_control_schema_migration_is_additive_and_idempotent(tmp_path) -> None:
    database = create_engine(f"sqlite:///{tmp_path / 'control-migration.db'}")

    assert missing_tables(database) == {"proxy_profiles"}
    apply_schema(database)
    apply_schema(database)
    assert missing_tables(database) == set()
