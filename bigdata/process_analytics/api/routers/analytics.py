"""Analytics query routes."""

from typing import Dict, List

from fastapi import APIRouter

from .. import context

router = APIRouter()


@router.get("/kpis")
def get_kpis() -> Dict[str, float]:
    """Return derived KPIs from observed events."""
    return context.latest_metrics()


@router.get("/conformance")
def get_conformance() -> Dict[str, int]:
    """Return counts of deviations detected across all cases."""
    deviations = 0
    for case_id, activities in context.case_traces.items():
        deviations += len(context.conformance_checker.check_trace(case_id, activities))
    return {"deviations": deviations}


@router.get("/anomalies")
def get_anomalies() -> List[Dict[str, str]]:
    """Return anomalies detected by the DBSCAN model."""
    return list(context.anomaly_log)
