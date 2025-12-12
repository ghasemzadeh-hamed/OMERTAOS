"""Validate the UI registry against its schema."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_ROOT = ROOT / "packages" / "ui-core" / "registry"


def main() -> None:
    schema = json.loads((REGISTRY_ROOT / "registry.schema.json").read_text())
    document = {
        "navigation": json.loads((REGISTRY_ROOT / "navigation.json").read_text()),
        "capabilities": json.loads((REGISTRY_ROOT / "capabilities.json").read_text()),
        "pages": {
            "dashboard": json.loads((REGISTRY_ROOT / "pages" / "dashboard.page.json").read_text()),
        },
    }
    validate(instance=document, schema=schema)
    print("registry validation ok")


if __name__ == "__main__":
    main()
