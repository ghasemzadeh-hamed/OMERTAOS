"""Metric helpers for classification, regression, and drift monitoring."""
from __future__ import annotations

from typing import Dict, Iterable, Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    roc_auc_score,
    r2_score,
)


def compute_classification_metrics(
    y_true,
    y_pred,
    y_prob: Optional[np.ndarray],
) -> Dict[str, float]:
    """Return standard classification metrics."""

    metrics: Dict[str, float] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred, average="weighted")),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted")),
    }

    if y_prob is not None:
        try:
            if y_prob.ndim == 1 or y_prob.shape[1] == 1:
                metrics["auc"] = float(roc_auc_score(y_true, y_prob))
            else:
                metrics["auc"] = float(roc_auc_score(y_true, y_prob, multi_class="ovr"))
        except ValueError:
            metrics["auc"] = float("nan")
    else:
        metrics["auc"] = float("nan")

    return metrics


def compute_regression_metrics(y_true, y_pred) -> Dict[str, float]:
    """Return regression metrics."""

    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    r2 = r2_score(y_true, y_pred)
    return {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}


def psi(expected: Iterable[float], actual: Iterable[float], bins: int = 10) -> float:
    """Compute the population stability index between two distributions."""

    expected_arr = np.asarray(list(expected), dtype=float)
    actual_arr = np.asarray(list(actual), dtype=float)

    if expected_arr.size == 0 or actual_arr.size == 0:
        raise ValueError("PSI requires non-empty inputs.")

    if np.allclose(np.max(expected_arr), np.min(expected_arr)):
        breakpoints = np.linspace(np.min(expected_arr) - 0.5, np.max(expected_arr) + 0.5, bins + 1)
    else:
        breakpoints = np.linspace(np.min(expected_arr), np.max(expected_arr), bins + 1)

    expected_counts, _ = np.histogram(expected_arr, bins=breakpoints)
    actual_counts, _ = np.histogram(actual_arr, bins=breakpoints)

    expected_ratio = np.clip(expected_counts / expected_arr.size, 1e-6, None)
    actual_ratio = np.clip(actual_counts / actual_arr.size, 1e-6, None)

    psi_values = (actual_ratio - expected_ratio) * np.log(actual_ratio / expected_ratio)
    return float(np.sum(psi_values))

