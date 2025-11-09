"""Guard rails evaluating generalization health before deployment."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict

import yaml

ARTIFACTS_DIR = Path("artifacts")
METRICS_FILE = ARTIFACTS_DIR / "metrics.json"


def _load_metrics() -> Dict:
    if not METRICS_FILE.exists():
        raise FileNotFoundError("metrics.json not found. Run train_eval.py first.")
    with open(METRICS_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_config(config_path: Path) -> Dict:
    with open(config_path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _primary_metric(task: str) -> str:
    return "auc" if task == "classification" else "mae"


def _gap(train_value: float, val_value: float) -> float:
    baseline = max(abs(train_value), 1e-8)
    return abs(train_value - val_value) / baseline


def _max_cv_std(cv_summary: Dict[str, Dict[str, float]]) -> float:
    if not cv_summary:
        return 0.0

    max_std = 0.0
    for values in cv_summary.values():
        if not isinstance(values, dict):
            continue
        try:
            std_value = float(values.get("std", 0.0))
        except (TypeError, ValueError):
            continue
        if math.isnan(std_value):
            continue
        max_std = max(max_std, std_value)
    return max_std


def main() -> int:
    config_path = Path("policies/training.yaml")
    cfg = _load_config(config_path)
    metrics = _load_metrics()

    task = metrics.get("task", "classification")
    metric_name = _primary_metric(task)

    train_raw = metrics.get("train", {}).get(metric_name, 0.0)
    val_raw = metrics.get("val", {}).get(metric_name, 0.0)
    try:
        train_value = float(train_raw)
    except (TypeError, ValueError):
        train_value = 0.0
    try:
        val_value = float(val_raw)
    except (TypeError, ValueError):
        val_value = 0.0

    if math.isnan(train_value) or math.isnan(val_value):
        gap_ratio = 0.0
    else:
        gap_ratio = _gap(train_value, val_value)

    guard_cfg = cfg.get("guards", {})
    max_gap = float(guard_cfg.get("max_train_val_gap", 0.1))
    max_cv_std = float(guard_cfg.get("max_cv_std", 0.03))
    drift_cfg = cfg.get("monitoring", {}).get("drift", {})
    psi_threshold = float(drift_cfg.get("psi_threshold", 0.2))

    cv_summary = metrics.get("cv", {})
    cv_std = _max_cv_std(cv_summary)

    drift_raw = metrics.get("drift", {}).get("train_val_psi", 0.0)
    try:
        drift_value = float(drift_raw)
    except (TypeError, ValueError):
        drift_value = 0.0
    if math.isnan(drift_value):
        drift_value = 0.0

    failures = []
    if gap_ratio > max_gap:
        failures.append(f"Train/val gap ratio {gap_ratio:.3f} exceeds threshold {max_gap:.3f}.")
    if cv_std > max_cv_std:
        failures.append(f"Cross-validation std {cv_std:.3f} exceeds threshold {max_cv_std:.3f}.")
    if abs(drift_value) > psi_threshold:
        failures.append(f"Population stability index {drift_value:.3f} exceeds threshold {psi_threshold:.3f}.")

    if failures:
        print("FAIL: generalization guard triggered.")
        for msg in failures:
            print(f" - {msg}")
        return 1

    print("PASS: generalization checks within guard thresholds.")
    print(
        json.dumps(
            {
                "metric": metric_name,
                "gap_ratio": gap_ratio,
                "cv_std": cv_std,
                "drift": drift_value,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
