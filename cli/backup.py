"""Backup utilities."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", default="artifacts", help="Directory to backup")
    parser.add_argument("--destination", default="backups/artifacts", help="Backup target")
    parser.add_argument("--restore", action="store_true", help="Restore from backup")


def handle(args: argparse.Namespace) -> int:
    src = Path(args.source)
    dst = Path(args.destination)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if args.restore:
        if not dst.exists():
            print(f"backup missing: {dst}")
            return 1
        if src.exists():
            shutil.rmtree(src)
        shutil.copytree(dst, src)
        print(f"restored backup from {dst} to {src}")
        return 0
    if not src.exists():
        print(f"source missing: {src}")
        return 1
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"backup stored at {dst}")
    return 0
