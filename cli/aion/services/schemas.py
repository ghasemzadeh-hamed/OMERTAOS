"""JSON schema loading utilities shared by CLI services."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore

try:
    from jsonschema import Draft7Validator
except ImportError:  # pragma: no cover - optional dependency for validation
    class Draft7Validator:  # type: ignore[override]
        """Fallback validator that skips schema checks when jsonschema is absent."""

        def __init__(self, schema):  # pragma: no cover - trivial wrapper
            self.schema = schema

        def iter_errors(self, data):  # pragma: no cover - always succeeds
            return []

SCHEMA_DIR = Path(__file__).resolve().parents[3] / "config-schemas"


class BundleValidator:
    """Validate bundle configuration files using JSON schema definitions."""

    def __init__(self) -> None:
        self.schemas = {
            "providers": self._load_schema("providers.schema.json"),
            "router": self._load_schema("router.policy.schema.json"),
            "datasources": self._load_schema("data-sources.schema.json"),
            "module": self._load_schema("module.aip.schema.json"),
        }

    def validate_bundle(self, directory: Path) -> List[str]:
        report: List[str] = []
        for filename, schema_name in (
            ("providers.yaml", "providers"),
            ("router.policy.yaml", "router"),
            ("data-sources.yaml", "datasources"),
        ):
            file_path = directory / filename
            if file_path.exists():
                report.extend(self._validate(file_path, self.schemas[schema_name]))
        modules_dir = directory / "modules"
        if modules_dir.exists():
            for manifest in modules_dir.glob("**/aip.yaml"):
                report.extend(self._validate(manifest, self.schemas["module"]))
        if not report:
            report.append("No configuration files detected; nothing to validate.")
        return report

    def _validate(self, file_path: Path, schema: Dict) -> List[str]:
        data = self._load_file(file_path)
        validator = Draft7Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda err: err.path)
        if errors:
            return [f"{file_path.name}: {error.message}" for error in errors]
        return [f"{file_path.name}: ok"]

    def _load_file(self, file_path: Path):
        if file_path.suffix in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError("pyyaml is required to parse YAML configuration")
            with file_path.open("r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
        with file_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _load_schema(self, filename: str) -> Dict:
        with (SCHEMA_DIR / filename).open("r", encoding="utf-8") as fh:
            return json.load(fh)
