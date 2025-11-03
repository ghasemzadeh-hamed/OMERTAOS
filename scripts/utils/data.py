"""Data access and splitting utilities for model training workflows."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sklearn.model_selection import (
    BaseCrossValidator,
    GroupKFold,
    StratifiedKFold,
    TimeSeriesSplit,
    KFold,
    train_test_split,
)


@dataclass
class DatasetMeta:
    """Metadata describing the loaded dataset."""

    task: str
    target: str
    numeric_features: List[str]
    categorical_features: List[str]
    group_column: Optional[str] = None
    groups: Optional[pd.Series] = None
    source: str = ""
    notes: Optional[str] = None


@dataclass
class SplitBundle:
    """Container for resolved dataset splits and cross-validation helpers."""

    X_train: pd.DataFrame
    X_val: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series
    cv_splitter: BaseCrossValidator
    outer_splitter: Optional[BaseCrossValidator]
    groups_train: Optional[pd.Series]
    groups_all: Optional[pd.Series]


def load_data(*, allow_synthetic: bool = False, random_state: int = 42) -> Tuple[pd.DataFrame, pd.Series, DatasetMeta]:
    """Load the training dataset according to environment configuration."""

    dataset_path = os.getenv("AIONOS_DATA_PATH")
    target_column = os.getenv("AIONOS_TARGET_COLUMN")
    task = os.getenv("AIONOS_TASK", "classification").lower()
    group_column = os.getenv("AIONOS_GROUP_COLUMN")

    if dataset_path and target_column:
        data = pd.read_csv(dataset_path)
        if target_column not in data.columns:
            raise RuntimeError(
                f"Target column '{target_column}' not found in dataset located at {dataset_path}."
            )

        y = data[target_column]
        X = data.drop(columns=[target_column])
        numeric = X.select_dtypes(include=["number"]).columns.tolist()
        categorical = [col for col in X.columns if col not in numeric]
        groups = None
        if group_column and group_column in data.columns:
            groups = data[group_column]
        meta = DatasetMeta(
            task=task,
            target=target_column,
            numeric_features=numeric,
            categorical_features=categorical,
            group_column=group_column if groups is not None else None,
            groups=groups,
            source=dataset_path,
            notes="Configured via environment variables.",
        )
        return X, y, meta

    if not allow_synthetic:
        raise RuntimeError(
            "Dataset configuration not provided. Set AIONOS_DATA_PATH and "
            "AIONOS_TARGET_COLUMN environment variables or enable the synthetic "
            "CI fallback."
        )

    from sklearn.datasets import make_classification

    X_array, y_array = make_classification(
        n_samples=600,
        n_features=12,
        n_informative=8,
        n_redundant=2,
        n_repeated=0,
        n_classes=2,
        flip_y=0.01,
        class_sep=1.2,
        random_state=random_state,
    )
    columns = [f"num_{idx}" for idx in range(X_array.shape[1])]
    X = pd.DataFrame(X_array, columns=columns)
    y = pd.Series(y_array, name="target")
    meta = DatasetMeta(
        task="classification",
        target="target",
        numeric_features=columns,
        categorical_features=[],
        source="synthetic_ci",
        notes="Synthetic dataset generated for CI guard rails.",
    )
    return X, y, meta


def _resolve_cv_scheme(
    cfg: Dict[str, Any],
    y: pd.Series,
    groups: Optional[pd.Series],
    random_state: int,
) -> Tuple[BaseCrossValidator, Optional[BaseCrossValidator]]:
    scheme = cfg.get("scheme", "stratified_kfold").lower()
    n_splits = int(cfg.get("n_splits", 5))
    gap = int(cfg.get("gap", 0))

    if scheme == "stratified_kfold":
        splitter: BaseCrossValidator = StratifiedKFold(
            n_splits=n_splits, shuffle=True, random_state=random_state
        )
        outer = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state + 1)
    elif scheme == "group_kfold":
        splitter = GroupKFold(n_splits=n_splits)
        outer = GroupKFold(n_splits=n_splits)
    elif scheme == "time_series":
        splitter = TimeSeriesSplit(n_splits=n_splits, gap=gap)
        outer = TimeSeriesSplit(n_splits=n_splits, gap=gap)
    else:
        splitter = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        outer = KFold(n_splits=n_splits, shuffle=True, random_state=random_state + 1)

    if not cfg.get("nested", False):
        outer = None

    return splitter, outer


def make_splits(
    X: pd.DataFrame,
    y: pd.Series,
    meta: DatasetMeta,
    cfg: Dict[str, Any],
    *,
    random_state: int = 42,
) -> SplitBundle:
    """Create train/validation/test splits and cross-validation helpers."""

    split_cfg = cfg.get("split", {})
    test_size = float(split_cfg.get("test_size", 0.15))
    val_size = float(split_cfg.get("val_size", 0.15))
    stratify_enabled = bool(split_cfg.get("stratify", False))

    groups = meta.groups
    stratify_labels: Optional[pd.Series]
    if stratify_enabled and meta.task == "classification":
        stratify_labels = y
    else:
        stratify_labels = None

    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=stratify_labels,
        random_state=random_state,
    )

    if groups is not None:
        groups_trainval = groups.loc[X_trainval.index]
        groups_test = groups.loc[X_test.index]
    else:
        groups_trainval = None
        groups_test = None

    relative_val = val_size / (1.0 - test_size)
    stratify_inner: Optional[pd.Series]
    if stratify_labels is not None:
        stratify_inner = y_trainval
    else:
        stratify_inner = None

    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval,
        y_trainval,
        test_size=relative_val,
        stratify=stratify_inner,
        random_state=random_state,
    )

    if groups_trainval is not None:
        groups_train = groups_trainval.loc[X_train.index]
    else:
        groups_train = None

    cv_cfg = cfg.get("cv", {})
    cv_splitter, outer_splitter = _resolve_cv_scheme(
        cv_cfg,
        y_train,
        groups_train,
        random_state=random_state,
    )

    bundle = SplitBundle(
        X_train=X_train,
        X_val=X_val,
        X_test=X_test,
        y_train=y_train,
        y_val=y_val,
        y_test=y_test,
        cv_splitter=cv_splitter,
        outer_splitter=outer_splitter,
        groups_train=groups_train,
        groups_all=groups if groups is not None else None,
    )

    return bundle

