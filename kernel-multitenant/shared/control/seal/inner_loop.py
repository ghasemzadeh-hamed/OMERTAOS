import asyncio
import json
import time
from pathlib import Path


async def apply_updates(model_id, edits, strategy, budget):
    await asyncio.sleep(1.2)
    out = f"{model_id}-lora-snap"
    base_dir = Path("./registry/storage/experiments") / out
    base_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "base": model_id,
        "strategy": strategy,
        "budget": budget,
        "edits": edits,
        "ts": time.time()
    }
    (base_dir / "meta.json").write_text(json.dumps(meta))
    (base_dir / "adapter.safetensors").write_bytes(b"dummy")
    return out
