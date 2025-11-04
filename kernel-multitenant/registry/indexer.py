import json
import os
from pathlib import Path
from typing import List


def scan(base: str = "./registry/storage/experiments") -> List[dict]:
    out = []
    root = Path(base)
    if not root.exists():
        return out
    for meta_path in root.rglob("meta.json"):
        try:
            out.append(json.loads(meta_path.read_text()))
        except Exception:
            continue
    return out


if __name__ == "__main__":
    print(json.dumps(scan(), indent=2))
