from __future__ import annotations

import sys
from pathlib import Path

CONTROL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]

for path in (str(REPO_ROOT), str(CONTROL_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)
