"""DBSCAN-based anomaly detection for process analytics."""

from typing import List

import numpy as np
from sklearn.cluster import DBSCAN


class DBSCANAnomalyDetector:
    """Detect anomalies using the DBSCAN clustering algorithm."""

    def __init__(self, eps: float = 0.5, min_samples: int = 5):
        self.model = DBSCAN(eps=eps, min_samples=min_samples)
        self.fitted = False

    def fit(self, features: List[List[float]]) -> None:
        """Fit the DBSCAN model on the provided feature vectors."""
        X = np.array(features)
        self.model.fit(X)
        self.fitted = True

    def detect(self, features: List[List[float]]) -> List[int]:
        """Return cluster labels for the provided samples (-1 marks anomalies)."""
        if not self.fitted:
            raise RuntimeError("Model not fitted")
        X = np.array(features)
        labels = self.model.fit_predict(X)
        return labels.tolist()
