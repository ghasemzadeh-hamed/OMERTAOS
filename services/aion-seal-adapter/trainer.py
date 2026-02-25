from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict

import requests

from .config import settings
from .dataset_builder import build_sft_dataset, fetch_self_edits
from .evaluator import evaluate_model
from .registry_client import HTTPModelRegistryClient, ModelRegistryPort

logger = logging.getLogger(__name__)


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


def run_seal_iteration(registry: ModelRegistryPort | None = None) -> Dict[str, Any]:
    registry_client = registry or HTTPModelRegistryClient()

    edits = fetch_self_edits()
    if not edits:
        logger.info("seal_iteration_skipped", extra={"reason": "no_edits"})
        return {"status": "no_edits"}

    dataset = build_sft_dataset(edits)
    if not dataset:
        logger.info("seal_iteration_skipped", extra={"reason": "no_dataset"})
        return {"status": "no_dataset"}

    suffix = str(int(time.time()))
    model_path = finetune_lora(dataset, suffix)
    score = evaluate_model(model_path)
    registered = False
    try:
        registered = registry_client.register_if_better(model_path, score)
    except requests.HTTPError as exc:  # propagate meaningful message while still returning status
        logger.warning("seal_registry_error", extra={"model_path": model_path, "error": str(exc)})
        return {
            "status": "registry_error",
            "model_path": model_path,
            "score": score,
            "detail": str(exc),
        }

    status = "registered" if registered else "discarded"
    logger.info("seal_iteration_completed", extra={"status": status, "model_path": model_path, "score": score})
    return {
        "status": status,
        "model_path": model_path,
        "score": score,
    }
