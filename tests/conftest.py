from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GRPC_DIR = ROOT / "control" / "app" / "grpc"
if str(GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(GRPC_DIR))

CLI_DIR = ROOT / "cli"
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))
