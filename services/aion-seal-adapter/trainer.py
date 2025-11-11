from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

import requests

from .config import settings
from .dataset_builder import build_sft_dataset, fetch_self_edits
from .evaluator import evaluate_model


def finetune_lora(dataset: list[dict], suffix: str) -> str:
    output_dir = Path(settings.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_dir = output_dir / f"{settings.BASE_MODEL_NAME}-seal-{suffix}"
    model_dir.mkdir(parents=True, exist_ok=True)

    data_path = model_dir / "dataset.jsonl"
    with data_path.open("w", encoding="utf-8") as handle:
        for sample in dataset:
            handle.write(json.dumps(sample, ensure_ascii=False) + "\n")

    with (model_dir / "README.txt").open("w", encoding="utf-8") as readme:
        readme.write("SEAL-style adapted model based on high-reward self-edits.\n")

    return str(model_dir)


def get_best_score() -> float:
    try:
        response = requests.get(f"{settings.REGISTRY_URL}/models", timeout=10)
        response.raise_for_status()
        models = response.json()
        if not isinstance(models, list):
            return 0.0
        best = 0.0
        for model in models:
            score = float(model.get("score", 0.0))
            if score > best:
                best = score
        return best
    except Exception:
        return 0.0


def register_if_better(model_path: str, score: float) -> bool:
    best = get_best_score()
    if score < best + settings.IMPROVEMENT_THRESHOLD:
        return False

    payload: Dict[str, Any] = {
        "name": Path(model_path).name,
        "parent": settings.BASE_MODEL_NAME,
        "path": model_path,
        "score": score,
        "metadata": {"source": "seal-adapter"},
    }
    response = requests.post(f"{settings.REGISTRY_URL}/models", json=payload, timeout=10)
    response.raise_for_status()
    return True


def run_seal_iteration() -> Dict[str, Any]:
    edits = fetch_self_edits()
    if not edits:
        return {"status": "no_edits"}

    dataset = build_sft_dataset(edits)
    if not dataset:
        return {"status": "no_dataset"}

    suffix = str(int(time.time()))
    model_path = finetune_lora(dataset, suffix)
    score = evaluate_model(model_path)
    registered = False
    try:
        registered = register_if_better(model_path, score)
    except requests.HTTPError as exc:  # propagate meaningful message while still returning status
        return {
            "status": "registry_error",
            "model_path": model_path,
            "score": score,
            "detail": str(exc),
        }

    return {
        "status": "registered" if registered else "discarded",
        "model_path": model_path,
        "score": score,
    }
