from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = Path(__file__).with_name("fixtures") / "retired_roots.json"


def _contract() -> dict[str, list[str]]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


LEGACY_ROOTS = tuple(_contract()["retired_roots"])
LEGACY_IMPORT_PREFIXES = tuple(_contract()["retired_import_prefixes"])
HISTORICAL_EVIDENCE_ROOTS = tuple(_contract()["historical_evidence_roots"])
