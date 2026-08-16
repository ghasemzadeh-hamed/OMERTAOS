from __future__ import annotations

import argparse

from sqlalchemy import Engine, inspect

import control.scheduling.models  # noqa: F401

from .models import Base, engine


def missing_tables(bind: Engine = engine) -> set[str]:
    existing = set(inspect(bind).get_table_names())
    return set(Base.metadata.tables) - existing


def apply_schema(bind: Engine = engine) -> None:
    Base.metadata.create_all(bind=bind)


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply or verify the additive Control schema.")
    parser.add_argument("--check", action="store_true", help="verify without changing schema")
    args = parser.parse_args()

    missing = missing_tables()
    if args.check:
        if missing:
            print(f"Control schema is missing tables: {', '.join(sorted(missing))}")
            return 1
        print("Control schema is current")
        return 0

    apply_schema()
    remaining = missing_tables()
    if remaining:
        print(f"Control schema migration incomplete: {', '.join(sorted(remaining))}")
        return 1
    print("Control schema migration completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
