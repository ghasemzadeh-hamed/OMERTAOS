from pathlib import Path

import fastavro

SCHEMA_DIR = Path("bigdata/schemas")


def test_avro_schemas_are_valid() -> None:
    for schema_file in SCHEMA_DIR.glob("*.avsc"):
        schema = fastavro.schema.load_schema(str(schema_file))
        parsed = fastavro.parse_schema(schema)
        assert parsed["type"] == "record"
