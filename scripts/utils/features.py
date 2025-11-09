"""Feature engineering pipelines used in the training stack."""
from __future__ import annotations

from typing import Iterable, List

from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def make_preprocessor(
    numeric_features: Iterable[str],
    categorical_features: Iterable[str],
    *,
    kbest: int = 0,
    task: str = "classification",
) -> ColumnTransformer:
    """Create a preprocessing pipeline that avoids leakage."""

    numeric_features = list(numeric_features)
    categorical_features = list(categorical_features)

    numeric_steps: List[tuple] = [
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]

    if kbest and kbest > 0 and numeric_features:
        score_func = f_classif if task == "classification" else f_regression
        numeric_steps.append(
            (
                "select",
                SelectKBest(
                    score_func=score_func,
                    k=min(kbest, len(numeric_features)),
                ),
            )
        )

    numeric_pipeline = Pipeline(steps=numeric_steps)

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    transformers = []
    if numeric_features:
        transformers.append(("numeric", numeric_pipeline, numeric_features))
    if categorical_features:
        transformers.append(("categorical", categorical_pipeline, categorical_features))

    if not transformers:
        raise ValueError("No features available for preprocessing.")

    return ColumnTransformer(transformers=transformers)
