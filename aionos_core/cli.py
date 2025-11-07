"""CLI entrypoint for administering AION-OS installations."""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from core.installer import (
    AVAILABLE_PROFILES,
    apply_profile,
    ensure_config_dirs,
    get_config_root,
)

DEFAULT_UNITS = (
    "aionos-gateway.service",
    "aionos-control.service",
    "aionos-console.service",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aionos", description="AION-OS unified CLI")
    subparsers = parser.add_subparsers(dest="command")

    info_parser = subparsers.add_parser("info", help="Print repository metadata")
    info_parser.set_defaults(func=_cmd_info)

    doctor_parser = subparsers.add_parser("doctor", help="Run environment diagnostics")
    doctor_parser.set_defaults(func=_cmd_doctor)

    config_parser = subparsers.add_parser("config", help="Configuration helpers")
    config_sub = config_parser.add_subparsers(dest="config_cmd")

    config_path = config_sub.add_parser("path", help="Show configuration root")
    config_path.add_argument("--root", type=Path, default=Path.cwd())
    config_path.set_defaults(func=_cmd_config_path)

    config_ensure = config_sub.add_parser("ensure", help="Create configuration directories")
    config_ensure.add_argument("--root", type=Path, default=Path.cwd())
    config_ensure.set_defaults(func=_cmd_config_ensure)

    profile_parser = subparsers.add_parser("profile", help="Manage profile state")
    profile_sub = profile_parser.add_subparsers(dest="profile_cmd")

    profile_list = profile_sub.add_parser("list", help="List available profiles")
    profile_list.set_defaults(func=_cmd_profile_list)

    profile_apply = profile_sub.add_parser("apply", help="Render the .env for a profile")
    profile_apply.add_argument("name", help="Profile name to apply")
    profile_apply.add_argument("--env-file", type=Path, default=Path(".env"))
    profile_apply.add_argument("--root", type=Path, default=Path.cwd())
    profile_apply.add_argument("--set", action="append", default=[], help="Override KEY=VALUE entries")
    profile_apply.set_defaults(func=_cmd_profile_apply)

    services_parser = subparsers.add_parser("services", help="Manage systemd units")
    services_parser.add_argument("action", nargs="?", default="status", help="systemctl verb (start/stop/status)")
    services_parser.add_argument("--unit", action="append", default=[], help="Service unit override")
    services_parser.set_defaults(func=_cmd_services_manage)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return func(args)


def _cmd_info(_: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    print(f"AION-OS CLI version: {get_version()}")
    print(f"Python executable: {sys.executable}")
    print(f"Repository root: {repo_root}")
    print(f"Config root: {get_config_root(repo_root)}")
    return 0


def _cmd_doctor(_: argparse.Namespace) -> int:
    print("Collecting environment information...")
    print()
    print(f"Python version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    for tool in ("node", "npm", "git", "systemctl"):
        location = shutil.which(tool)
        status = location if location else "not found"
        print(f"{tool}: {status}")
    return 0


def _cmd_config_path(args: argparse.Namespace) -> int:
    print(get_config_root(args.root))
    return 0


def _cmd_config_ensure(args: argparse.Namespace) -> int:
    ensure_config_dirs(args.root)
    print(f"Ensured configuration directories under {get_config_root(args.root)}")
    return 0


def _cmd_profile_list(_: argparse.Namespace) -> int:
    for profile in AVAILABLE_PROFILES:
        print(profile)
    return 0


def _cmd_profile_apply(args: argparse.Namespace) -> int:
    try:
        extra = _parse_key_values(args.set)
    except argparse.ArgumentTypeError as exc:
        print(exc)
        return 2
    target = apply_profile(args.name, root=args.root, env_path=args.env_file, extra_env=extra)
    print(f"Rendered {target} for profile '{args.name}'.")
    return 0


def _cmd_services_manage(args: argparse.Namespace) -> int:
    if not shutil.which("systemctl"):
        print("systemctl is not available on this host")
        return 1
    units = tuple(args.unit) if args.unit else DEFAULT_UNITS
    for unit in units:
        cmd = ["systemctl", args.action, unit]
        print("$", " ".join(cmd))
        subprocess.run(cmd, check=False)
    return 0


def _parse_key_values(pairs: Iterable[str]) -> dict[str, str]:
    data: dict[str, str] = {}
    for item in pairs:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"Invalid KEY=VALUE pair: {item}")
        key, value = item.split("=", 1)
        data[key.strip()] = value
    return data


def get_version() -> str:
    try:
        from . import __version__

        return __version__
    except Exception:  # pragma: no cover
        return "unknown"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
