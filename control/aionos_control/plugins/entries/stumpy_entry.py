"""Entry point helpers for Stumpy integration."""
from typing import Iterable


def aion_entry(ts: Iterable[float], m: int):
    """Compute a matrix profile shape for the given series."""
    import numpy as np
    import stumpy

    ts_array = np.array(list(ts), dtype=float)
    matrix_profile = stumpy.stump(ts_array, m)
    shape = getattr(matrix_profile, "shape", None)
    if shape is None:
        rows = len(matrix_profile)
        cols = len(matrix_profile[0]) if rows else 0
    else:
        rows, cols = shape
    return {"matrix_profile_shape": [int(rows), int(cols)]}
