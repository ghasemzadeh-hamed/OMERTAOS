"""Entry point helpers for Nevergrad integration."""

def aion_entry(dim: int = 5, budget: int = 100):
    """Run a simple optimization task with Nevergrad."""
    import nevergrad as ng
    import numpy as np

    def sphere(x):
        array = np.array(x, dtype=float)
        return float(np.sum(array ** 2))

    optimizer = ng.optimizers.NGOpt(parametrization=dim, budget=budget)
    recommendation = optimizer.minimize(sphere)
    return {"best_x": list(recommendation.value)}
