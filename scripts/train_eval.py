"""Train and evaluate models with anti-overfitting guard rails."""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import yaml
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_selection import SelectFromModel
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.metrics import compute_classification_metrics, compute_regression_metrics, psi
from scripts.utils.data import DatasetMeta, load_data, make_splits
from scripts.utils.features import make_preprocessor
from scripts.utils.models import build_model, collect_early_stopping_params

_sklearn_spec = importlib.util.find_spec("sklearn")
if _sklearn_spec is not None:
    _sklearn_module = importlib.import_module("sklearn")
    SKLEARN_VERSION = getattr(_sklearn_module, "__version__", "0.0")
else:  # pragma: no cover - scikit-learn missing at runtime
    SKLEARN_VERSION = "0.0"

_SKLEARN_VERSION_PARTS = SKLEARN_VERSION.split(".")
_SKLEARN_MAJOR = int(_SKLEARN_VERSION_PARTS[0]) if _SKLEARN_VERSION_PARTS else 0
_SKLEARN_MINOR_PART = _SKLEARN_VERSION_PARTS[1] if len(_SKLEARN_VERSION_PARTS) > 1 else "0"
_SKLEARN_MINOR = int("".join(ch for ch in _SKLEARN_MINOR_PART if ch.isdigit()) or "0")
_LEGACY_PIPELINE_FIT = (_SKLEARN_MAJOR, _SKLEARN_MINOR) < (1, 3)

ARTIFACTS_DIR = Path("artifacts")


def _set_seeds(seed: int) -> None:
    """Ensure reproducible behaviour across libraries."""

    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def _resolve_task(meta: DatasetMeta, cli_task: Optional[str]) -> str:
    return cli_task or meta.task


def _feature_selector(task: str, random_state: int) -> SelectFromModel:
    if task == "classification":
        base_estimator = RandomForestClassifier(
            n_estimators=256,
            max_depth=6,
            max_features="sqrt",
            random_state=random_state,
        )
    else:
        base_estimator = RandomForestRegressor(
            n_estimators=256,
            max_depth=8,
            max_features="auto",
            random_state=random_state,
        )
    return SelectFromModel(estimator=base_estimator, threshold="median")


def _prepare_pipeline(
    meta: DatasetMeta,
    cfg: Dict[str, Any],
    *,
    task: str,
    random_state: int,
    ci_mode: bool,
) -> Pipeline:
    feature_cfg = cfg.get("feature_selection", {})
    filter_cfg = feature_cfg.get("filter", {})
    kbest = int(filter_cfg.get("kbest", 0))

    preprocessor = make_preprocessor(
        numeric_features=meta.numeric_features,
        categorical_features=meta.categorical_features,
        kbest=kbest,
        task=task,
    )

    steps = [("preprocess", preprocessor)]

    if feature_cfg.get("embedded", "") == "select_from_model":
        steps.append(("embedded_selector", _feature_selector(task, random_state)))

    estimator = build_model(task, cfg, random_state=random_state, ci_mode=ci_mode)
    steps.append(("estimator", estimator))

    return Pipeline(steps=steps)


def _route_fit_param(key: str) -> str:
    return f"estimator__{key}"


def _collect_fit_params(
    pipeline: Pipeline,
    cfg: Dict[str, Any],
    *,
    task: str,
    X_val,
    y_val,
) -> Dict[str, Any]:
    early_cfg = cfg.get("early_stopping", {})
    params = collect_early_stopping_params(
        pipeline.named_steps["estimator"],
        early_cfg,
        task=task,
        X_val=X_val,
        y_val=y_val,
    )
    if not _LEGACY_PIPELINE_FIT:
        return {}
    return {_route_fit_param(key): value for key, value in params.items()}


def _probabilities(estimator, X):
    if hasattr(estimator, "predict_proba"):
        return estimator.predict_proba(X)
    if hasattr(estimator, "decision_function"):
        scores = estimator.decision_function(X)
        if scores.ndim == 1:
            return np.vstack([1 - scores, scores]).T
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate guarded models.")
    parser.add_argument("--config", required=True, help="Path to YAML configuration file.")
    parser.add_argument(
        "--task",
        choices=["classification", "regression"],
        default=None,
        help="Override task type detected from metadata.",
    )
    parser.add_argument(
        "--group_key",
        default=None,
        help="Optional column indicating grouping for CV.",
    )
    parser.add_argument("--ci", action="store_true", help="Enable synthetic CI fallback dataset.")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle)

    seed = int(cfg.get("seed", 42))
    _set_seeds(seed)

    X, y, meta = load_data(allow_synthetic=args.ci, random_state=seed)

    if args.group_key:
        if args.group_key not in X.columns:
            raise RuntimeError(f"Group key '{args.group_key}' not found in features.")
        meta.group_column = args.group_key
        meta.groups = X[args.group_key]
        X = X.drop(columns=[args.group_key])
        meta.numeric_features = [col for col in meta.numeric_features if col != args.group_key]
        meta.categorical_features = [col for col in meta.categorical_features if col != args.group_key]

    task = _resolve_task(meta, args.task)

    pipeline = _prepare_pipeline(meta, cfg, task=task, random_state=seed, ci_mode=args.ci)

    splits = make_splits(X, y, meta, cfg, random_state=seed)

    fit_params = _collect_fit_params(
        pipeline,
        cfg,
        task=task,
        X_val=splits.X_val,
        y_val=splits.y_val,
    )

    pipeline.fit(splits.X_train, splits.y_train, **fit_params)

    y_train_pred = pipeline.predict(splits.X_train)
    y_val_pred = pipeline.predict(splits.X_val)
    y_test_pred = pipeline.predict(splits.X_test)

    train_prob = None
    val_prob = None
    test_prob = None
    if task == "classification":
        train_prob = _probabilities(pipeline, splits.X_train)
        val_prob = _probabilities(pipeline, splits.X_val)
        test_prob = _probabilities(pipeline, splits.X_test)

    if task == "classification":
        train_metrics = compute_classification_metrics(splits.y_train, y_train_pred, train_prob)
        val_metrics = compute_classification_metrics(splits.y_val, y_val_pred, val_prob)
        test_metrics = compute_classification_metrics(splits.y_test, y_test_pred, test_prob)
    else:
        train_metrics = compute_regression_metrics(splits.y_train, y_train_pred)
        val_metrics = compute_regression_metrics(splits.y_val, y_val_pred)
        test_metrics = compute_regression_metrics(splits.y_test, y_test_pred)

    drift_metrics: Dict[str, float] = {}
    if task == "classification" and train_prob is not None and val_prob is not None:
        train_scores = train_prob[:, 1] if train_prob.ndim > 1 else train_prob
        val_scores = val_prob[:, 1] if val_prob.ndim > 1 else val_prob
        drift_metrics["train_val_psi"] = psi(train_scores, val_scores)
    elif task == "regression":
        drift_metrics["train_val_psi"] = psi(y_train_pred, y_val_pred)

    cv_summary: Dict[str, Dict[str, float]] = {}
    outer = splits.outer_splitter
    if outer is not None:
        if task == "classification":
            scoring = {
                "auc": "roc_auc",
                "f1": "f1_weighted",
                "accuracy": "accuracy",
            }
        else:
            scoring = {
                "mae": "neg_mean_absolute_error",
                "rmse": "neg_root_mean_squared_error",
                "r2": "r2",
            }

        cv_results = cross_validate(
            pipeline,
            X,
            y,
            cv=outer,
            scoring=scoring,
            n_jobs=1,
            error_score="raise",
            groups=splits.groups_all,
        )

        for key, values in cv_results.items():
            if not key.startswith("test_"):
                continue
            metric_name = key.replace("test_", "")
            arr = np.array(values)
            if task == "regression" and metric_name in {"mae", "rmse"}:
                arr = -arr
            cv_summary[metric_name] = {
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr, ddof=1) if arr.size > 1 else 0.0),
            }

    ARTIFACTS_DIR.mkdir(exist_ok=True)

    metrics_payload = {
        "task": task,
        "train": train_metrics,
        "val": val_metrics,
        "test": test_metrics,
        "cv": cv_summary,
        "drift": drift_metrics,
        "meta": {
            "dataset_source": meta.source,
            "target": meta.target,
        },
    }

    with open(ARTIFACTS_DIR / "metrics.json", "w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)

    with open(ARTIFACTS_DIR / "cv_summary.json", "w", encoding="utf-8") as handle:
        json.dump(cv_summary, handle, indent=2)

    with open(ARTIFACTS_DIR / "model_config.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "task": task,
                "config": cfg,
                "pipeline_steps": [name for name, _ in pipeline.steps],
                "random_state": seed,
            },
            handle,
            indent=2,
        )

    importance_payload = []
    try:
        scoring_metric = "roc_auc" if task == "classification" else "neg_mean_squared_error"
        importances = permutation_importance(
            pipeline,
            splits.X_val,
            splits.y_val,
            n_repeats=5,
            random_state=seed,
            scoring=scoring_metric,
        )
        feature_names = pipeline.named_steps["preprocess"].get_feature_names_out()
        for name, value in sorted(
            zip(feature_names, importances.importances_mean),
            key=lambda item: item[1],
            reverse=True,
        ):
            importance_payload.append({"feature": name, "importance": float(value)})
    except Exception as exc:  # noqa: BLE001
        importance_payload.append({"feature": "unavailable", "importance": 0.0, "reason": str(exc)})

    with open(ARTIFACTS_DIR / "feature_importance.json", "w", encoding="utf-8") as handle:
        json.dump(importance_payload, handle, indent=2)

    summary = {
        "task": task,
        "train_auc_or_mae": train_metrics.get("auc") if task == "classification" else train_metrics.get("mae"),
        "val_auc_or_mae": val_metrics.get("auc") if task == "classification" else val_metrics.get("mae"),
        "test_auc_or_mae": test_metrics.get("auc") if task == "classification" else test_metrics.get("mae"),
        "cv_metrics": cv_summary,
        "drift": drift_metrics,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

