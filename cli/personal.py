from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from os.kernel.osci import linux_kernel_entry, windows_kernel_entry


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--platform", choices=["linux", "windows"], default="linux")
    parser.add_argument("--intent", default="hello")
    parser.add_argument("--payload", default="{}")


def handle(args: argparse.Namespace) -> int:
    bootstrap = linux_kernel_entry.bootstrap if args.platform == "linux" else windows_kernel_entry.bootstrap
    kernel = bootstrap()
    decision = kernel.dispatch(intent=args.intent, payload=json.loads(args.payload), user_id="cli-user")
    print(json.dumps(asdict(decision), indent=2))
    return 0 if decision.status == "accepted" else 1
