"""Model factory helpers for the anti-overfitting guard stack."""
from __future__ import annotations

from typing import Any, Dict

from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.base import BaseEstimator
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    StackingClassifier,
    StackingRegressor,
)
from sklearn.linear_model import LogisticRegression, Ridge
from xgboost import XGBClassifier, XGBRegressor

_TREE_DEFAULTS = {
    "learning_rate": 0.05,
    "n_estimators": 200,
    "max_depth": 6,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
}


def _tree_regularization(cfg: Dict[str, Any]) -> Dict[str, float]:
    trees_cfg = cfg.get("regularization", {}).get("trees", {})
    return {
        "reg_lambda": float(trees_cfg.get("reg_lambda", 1.0)),
        "reg_alpha": float(trees_cfg.get("reg_alpha", 0.0)),
    }


def build_xgb_classifier(cfg: Dict[str, Any], *, random_state: int) -> XGBClassifier:
    regularization = _tree_regularization(cfg)
    params = {
        **_TREE_DEFAULTS,
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "random_state": random_state,
        "use_label_encoder": False,
        **regularization,
    }
    return XGBClassifier(**params)


def build_xgb_regressor(cfg: Dict[str, Any], *, random_state: int) -> XGBRegressor:
    regularization = _tree_regularization(cfg)
    params = {
        **_TREE_DEFAULTS,
        "objective": "reg:squarederror",
        "random_state": random_state,
        **regularization,
    }
    return XGBRegressor(**params)


def build_lgbm_classifier(cfg: Dict[str, Any], *, random_state: int) -> LGBMClassifier:
    regularization = _tree_regularization(cfg)
    return LGBMClassifier(
        n_estimators=int(_TREE_DEFAULTS["n_estimators"]),
        learning_rate=_TREE_DEFAULTS["learning_rate"],
        max_depth=_TREE_DEFAULTS["max_depth"],
        subsample=_TREE_DEFAULTS["subsample"],
        colsample_bytree=_TREE_DEFAULTS["colsample_bytree"],
        objective="binary",
        random_state=random_state,
        reg_lambda=regularization["reg_lambda"],
        reg_alpha=regularization["reg_alpha"],
    )


def build_lgbm_regressor(cfg: Dict[str, Any], *, random_state: int) -> LGBMRegressor:
    regularization = _tree_regularization(cfg)
    return LGBMRegressor(
        n_estimators=int(_TREE_DEFAULTS["n_estimators"]),
        learning_rate=_TREE_DEFAULTS["learning_rate"],
        max_depth=_TREE_DEFAULTS["max_depth"],
        subsample=_TREE_DEFAULTS["subsample"],
        colsample_bytree=_TREE_DEFAULTS["colsample_bytree"],
        objective="regression",
        random_state=random_state,
        reg_lambda=regularization["reg_lambda"],
        reg_alpha=regularization["reg_alpha"],
    )


def build_stacking_classifier(cfg: Dict[str, Any], *, random_state: int, stacking_cv: int = 5) -> StackingClassifier:
    estimators = [
        ("xgb", build_xgb_classifier(cfg, random_state=random_state)),
        ("lgbm", build_lgbm_classifier(cfg, random_state=random_state + 7)),
        (
            "rf",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=6,
                max_features="sqrt",
                class_weight="balanced",
                random_state=random_state + 11,
            ),
        ),
    ]
    final_estimator = LogisticRegression(
        penalty="l1",
        C=0.5,
        solver="saga",
        max_iter=2000,
        random_state=random_state,
    )
    return StackingClassifier(
        estimators=estimators,
        final_estimator=final_estimator,
        cv=stacking_cv,
        stack_method="predict_proba",
        passthrough=False,
        n_jobs=None,
    )


def build_stacking_regressor(cfg: Dict[str, Any], *, random_state: int, stacking_cv: int = 5) -> StackingRegressor:
    estimators = [
        ("xgb", build_xgb_regressor(cfg, random_state=random_state)),
        ("lgbm", build_lgbm_regressor(cfg, random_state=random_state + 7)),
        (
            "rf",
            RandomForestRegressor(
                n_estimators=250,
                max_depth=8,
                max_features="auto",
                random_state=random_state + 19,
            ),
        ),
    ]
    final_estimator = Ridge(alpha=0.5, random_state=random_state)
    return StackingRegressor(
        estimators=estimators,
        final_estimator=final_estimator,
        cv=stacking_cv,
        passthrough=False,
        n_jobs=None,
    )


def build_model(task: str, cfg: Dict[str, Any], *, random_state: int = 42) -> BaseEstimator:
    ensemble_cfg = cfg.get("ensemble", {})
    stacking_cv = int(ensemble_cfg.get("stacking_cv", 5))
    methods = [method.lower() for method in ensemble_cfg.get("methods", [])]

    if task == "classification":
        if "stacking" in methods:
            return build_stacking_classifier(cfg, random_state=random_state, stacking_cv=stacking_cv)
        return build_xgb_classifier(cfg, random_state=random_state)

    if task == "regression":
        if "stacking" in methods:
            return build_stacking_regressor(cfg, random_state=random_state, stacking_cv=stacking_cv)
        return build_xgb_regressor(cfg, random_state=random_state)

    raise ValueError(f"Unsupported task '{task}'.")


def collect_early_stopping_params(
    estimator: BaseEstimator,
    early_cfg: Dict[str, Any],
    *,
    task: str,
    X_val,
    y_val,
) -> Dict[str, Any]:
    """Return fit keyword arguments enabling early stopping when supported."""

    if not early_cfg.get("enabled", False):
        return {}

    patience = int(early_cfg.get("patience", 50))
    metric = "auc" if task == "classification" else "rmse"

    def payload(prefix: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            f"{prefix}early_stopping_rounds": patience,
            f"{prefix}eval_set": [(X_val, y_val)],
            f"{prefix}verbose": False,
        }
        data[f"{prefix}eval_metric"] = metric
        return data

    if isinstance(estimator, (XGBClassifier, XGBRegressor, LGBMClassifier, LGBMRegressor)):
        return payload("")

    if isinstance(estimator, (StackingClassifier, StackingRegressor)):
        params: Dict[str, Any] = {}
        for name, base_estimator in estimator.estimators:
            if isinstance(base_estimator, (XGBClassifier, XGBRegressor, LGBMClassifier, LGBMRegressor)):
                params.update(payload(f"{name}__"))
        return params

    return {}

