"""Status inspection commands."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--artifacts", default="artifacts/metrics.json", help="Metrics artifact path")


def handle(args: argparse.Namespace) -> int:
    path = Path(args.artifacts)
    if not path.exists():
        print(json.dumps({"status": "missing", "path": str(path)}))
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps({"status": "ok", "metrics": data}, indent=2))
    return 0
