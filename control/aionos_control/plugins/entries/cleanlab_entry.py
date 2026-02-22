"""Entry point helpers for Cleanlab integration."""
from typing import Iterable, Sequence


def aion_entry(y_true: Iterable[int], y_pred_proba: Sequence[Sequence[float]]):
    """Compute label quality scores using Cleanlab."""
    import numpy as np
    from cleanlab.rank import get_label_quality_scores

    y_true_array = np.array(list(y_true))
    y_pred_array = np.array(list(y_pred_proba))
    scores = get_label_quality_scores(labels=y_true_array, pred_probs=y_pred_array)
    return {"label_quality_scores": scores.tolist()}
