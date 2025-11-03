from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--path", default="policies/training.yaml", help="Policy definition path")
    parser.add_argument("--export", help="Export path for compiled policy", default=None)


def handle(args: argparse.Namespace) -> int:
    policy_path = Path(args.path).resolve()
    if not policy_path.exists():
        print(f"policy file not found: {policy_path}")
        return 1
    content = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    payload = {"path": str(policy_path), "hash": hash(json.dumps(content, sort_keys=True))}
    if args.export:
        export_path = Path(args.export).resolve()
        export_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"policy exported to {export_path}")
    else:
        print(json.dumps(payload))
    return 0
