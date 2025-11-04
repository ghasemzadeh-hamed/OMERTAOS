def passed_gates(base, new, objective):
    metric = objective.get("metric", "accuracy")
    delta_min = float(objective.get("delta_min", 0.0))
    baseline = float(base.get(metric, 0.0))
    updated = float(new.get(metric, 0.0))
    return (updated - baseline) >= delta_min
