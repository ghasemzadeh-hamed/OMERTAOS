"""Installer routines invoked by the CLI."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", default="profiles/user/config.profile.yaml", help="Profile to install")
    parser.add_argument("--dry-run", action="store_true", help="Validate without applying changes")


def handle(args: argparse.Namespace) -> int:
    profile_path = Path(args.profile).resolve()
    repo_root = Path(__file__).resolve().parents[1]
    try:
        profile_path.relative_to(repo_root)
    except ValueError:
        print("profile path must reside within repository")
        return 1
    if not profile_path.exists():
        print(f"profile not found: {profile_path}")
        return 1
    if args.dry_run:
        print(f"validated profile: {profile_path}")
        return 0
    command = ["bash", "scripts/install_linux.sh"] if profile_path.suffix == ".yaml" else []
    if command:
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"install failed: {exc}")
            return exc.returncode
    print(f"installation profile applied: {profile_path}")
    return 0
