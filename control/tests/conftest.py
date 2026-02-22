from __future__ import annotations

import sys
from pathlib import Path

pytest_plugins = ("pytest_asyncio",)

REPO_ROOT = Path(__file__).resolve().parents[2]
repo_root_str = str(REPO_ROOT)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)
