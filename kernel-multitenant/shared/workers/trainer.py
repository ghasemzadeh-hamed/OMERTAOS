import json
import time
from pathlib import Path


def train_lora(base_model: str, data_path: str, out_dir: str, lr: float = 5e-5, steps: int = 120, r: int = 8):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    time.sleep(2)
    (Path(out_dir) / "adapter.safetensors").write_bytes(b"dummy")
    meta = {"base": base_model, "lr": lr, "steps": steps, "r": r, "finished_at": time.time(), "data_path": data_path}
    (Path(out_dir) / "meta.json").write_text(json.dumps(meta))
    return out_dir
