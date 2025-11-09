"""Model factory helpers for the anti-overfitting guard stack."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from sklearn.base import BaseEstimator
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    StackingClassifier,
    StackingRegressor,
)
from sklearn.linear_model import LogisticRegression, Ridge

try:  # Optional dependency: LightGBM is not required in CI
    from lightgbm import LGBMClassifier, LGBMRegressor  # type: ignore
except ImportError:  # pragma: no cover - optional dependency missing
    LGBMClassifier = None  # type: ignore[assignment]
    LGBMRegressor = None  # type: ignore[assignment]

try:  # Optional dependency: XGBoost is not required in CI
    from xgboost import XGBClassifier, XGBRegressor  # type: ignore
except ImportError:  # pragma: no cover - optional dependency missing
    XGBClassifier = None  # type: ignore[assignment]
    XGBRegressor = None  # type: ignore[assignment]

_TREE_DEFAULTS = {
    "learning_rate": 0.05,
    "n_estimators": 200,
    "max_depth": 6,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
}

_HAS_XGB = XGBClassifier is not None and XGBRegressor is not None
_HAS_LGBM = LGBMClassifier is not None and LGBMRegressor is not None


def _tree_regularization(cfg: Dict[str, Any]) -> Dict[str, float]:
    trees_cfg = cfg.get("regularization", {}).get("trees", {})
    return {
        "reg_lambda": float(trees_cfg.get("reg_lambda", 1.0)),
        "reg_alpha": float(trees_cfg.get("reg_alpha", 0.0)),
    }


def build_xgb_classifier(cfg: Dict[str, Any], *, random_state: int) -> "XGBClassifier":
    if not _HAS_XGB:  # pragma: no cover - guarded at call site
        raise RuntimeError("XGBoost is not available.")
    regularization = _tree_regularization(cfg)
    params = {
        **_TREE_DEFAULTS,
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "random_state": random_state,
        "use_label_encoder": False,
        **regularization,
    }
    return XGBClassifier(**params)  # type: ignore[return-value]


def build_xgb_regressor(cfg: Dict[str, Any], *, random_state: int) -> "XGBRegressor":
    if not _HAS_XGB:  # pragma: no cover - guarded at call site
        raise RuntimeError("XGBoost is not available.")
    regularization = _tree_regularization(cfg)
    params = {
        **_TREE_DEFAULTS,
        "objective": "reg:squarederror",
        "random_state": random_state,
        **regularization,
    }
    return XGBRegressor(**params)  # type: ignore[return-value]


def build_lgbm_classifier(cfg: Dict[str, Any], *, random_state: int) -> "LGBMClassifier":
    if not _HAS_LGBM:  # pragma: no cover - guarded at call site
        raise RuntimeError("LightGBM is not available.")
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
    )  # type: ignore[return-value]


def build_lgbm_regressor(cfg: Dict[str, Any], *, random_state: int) -> "LGBMRegressor":
    if not _HAS_LGBM:  # pragma: no cover - guarded at call site
        raise RuntimeError("LightGBM is not available.")
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
    )  # type: ignore[return-value]


def build_random_forest_classifier(*, random_state: int) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=256,
        max_depth=6,
        max_features="sqrt",
        class_weight="balanced",
        random_state=random_state,
    )


def build_random_forest_regressor(*, random_state: int) -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        max_features="auto",
        random_state=random_state,
    )


def _stacking_estimators(
    cfg: Dict[str, Any],
    *,
    random_state: int,
    allow_xgb: bool,
    allow_lgbm: bool,
) -> List[Tuple[str, BaseEstimator]]:
    estimators: List[Tuple[str, BaseEstimator]] = []
    if allow_xgb and _HAS_XGB:
        estimators.append(("xgb", build_xgb_classifier(cfg, random_state=random_state)))
    if allow_lgbm and _HAS_LGBM:
        estimators.append(("lgbm", build_lgbm_classifier(cfg, random_state=random_state + 7)))
    estimators.append(("rf", build_random_forest_classifier(random_state=random_state + 11)))
    return estimators


def build_stacking_classifier(
    cfg: Dict[str, Any],
    *,
    random_state: int,
    stacking_cv: int = 5,
    allow_xgb: bool = True,
    allow_lgbm: bool = True,
) -> StackingClassifier:
    estimators = _stacking_estimators(
        cfg,
        random_state=random_state,
        allow_xgb=allow_xgb,
        allow_lgbm=allow_lgbm,
    )
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


def _stacking_regressors(
    cfg: Dict[str, Any],
    *,
    random_state: int,
    allow_xgb: bool,
    allow_lgbm: bool,
) -> List[Tuple[str, BaseEstimator]]:
    estimators: List[Tuple[str, BaseEstimator]] = []
    if allow_xgb and _HAS_XGB:
        estimators.append(("xgb", build_xgb_regressor(cfg, random_state=random_state)))
    if allow_lgbm and _HAS_LGBM:
        estimators.append(("lgbm", build_lgbm_regressor(cfg, random_state=random_state + 7)))
    estimators.append(("rf", build_random_forest_regressor(random_state=random_state + 19)))
    return estimators


def build_stacking_regressor(
    cfg: Dict[str, Any],
    *,
    random_state: int,
    stacking_cv: int = 5,
    allow_xgb: bool = True,
    allow_lgbm: bool = True,
) -> StackingRegressor:
    estimators = _stacking_regressors(
        cfg,
        random_state=random_state,
        allow_xgb=allow_xgb,
        allow_lgbm=allow_lgbm,
    )
    final_estimator = Ridge(alpha=0.5, random_state=random_state)
    return StackingRegressor(
        estimators=estimators,
        final_estimator=final_estimator,
        cv=stacking_cv,
        passthrough=False,
        n_jobs=None,
    )


def build_model(
    task: str,
    cfg: Dict[str, Any],
    *,
    random_state: int = 42,
    ci_mode: bool = False,
) -> BaseEstimator:
    ensemble_cfg = cfg.get("ensemble", {})
    stacking_cv = int(ensemble_cfg.get("stacking_cv", 5))
    methods = [method.lower() for method in ensemble_cfg.get("methods", [])]

    if ci_mode:
        methods = [m for m in methods if m in {"bagging", "random_forest", "rf"}]

    allow_xgb = not ci_mode
    allow_lgbm = not ci_mode

    if task == "classification":
        if "stacking" in methods and (_HAS_XGB or _HAS_LGBM):
            return build_stacking_classifier(
                cfg,
                random_state=random_state,
                stacking_cv=stacking_cv,
                allow_xgb=allow_xgb,
                allow_lgbm=allow_lgbm,
            )
        if "boosting" in methods and _HAS_XGB and not ci_mode:
            return build_xgb_classifier(cfg, random_state=random_state)
        return build_random_forest_classifier(random_state=random_state)

    if task == "regression":
        if "stacking" in methods and (_HAS_XGB or _HAS_LGBM):
            return build_stacking_regressor(
                cfg,
                random_state=random_state,
                stacking_cv=stacking_cv,
                allow_xgb=allow_xgb,
                allow_lgbm=allow_lgbm,
            )
        if "boosting" in methods and _HAS_XGB and not ci_mode:
            return build_xgb_regressor(cfg, random_state=random_state)
        return build_random_forest_regressor(random_state=random_state)

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

    boosting_types: Tuple[type, ...] = tuple(
        tp
        for tp in (
            XGBClassifier if _HAS_XGB else None,
            XGBRegressor if _HAS_XGB else None,
            LGBMClassifier if _HAS_LGBM else None,
            LGBMRegressor if _HAS_LGBM else None,
        )
        if tp is not None
    )

    if boosting_types and isinstance(estimator, boosting_types):
        return payload("")

    if isinstance(estimator, (StackingClassifier, StackingRegressor)):
        params: Dict[str, Any] = {}
        for name, base_estimator in estimator.estimators:
            if boosting_types and isinstance(base_estimator, boosting_types):
                params.update(payload(f"{name}__"))
        return params

    return {}

