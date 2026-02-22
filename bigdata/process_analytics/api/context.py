"""Shared runtime context for the process analytics API."""

from collections import defaultdict
from typing import Any, Dict, List

from ..conformance.conformance_checker import ConformanceChecker
from ..core.utils import InMemoryEventSink
from ..discovery.discovery_engine import SimpleDiscoveryEngine
from ..ingestion.event_ingestor import EventIngestor
from ..performance.performance_analyzer import PerformanceAnalyzer
from ..predictive.anomaly_detector_dbscan import DBSCANAnomalyDetector
from ..predictive.outcome_predictor import RuleBasedOutcomePredictor
from ..predictive.time_predictor import SimpleTimePredictor
from ..prescriptive.decision_engine import DecisionEngine
from ..prescriptive.optimizer_ga import GeneticOptimizer
from ..prescriptive.rl_agent import TabularRLAgent
from ..orchestrator.adapters_omertaos import OMERTAOSAdapter
from ..orchestrator.self_evolving_controller import SelfEvolvingController


event_sink = InMemoryEventSink()
ingestor = EventIngestor(event_sink)
performance_analyzer = PerformanceAnalyzer()
discovery_engine = SimpleDiscoveryEngine()
time_predictor = SimpleTimePredictor()
outcome_predictor = RuleBasedOutcomePredictor({})
anomaly_detector = DBSCANAnomalyDetector()
case_traces: Dict[str, List[str]] = defaultdict(list)
allowed_relations: Dict[str, set] = {}
conformance_checker = ConformanceChecker(allowed_relations)
optimizer = GeneticOptimizer()
rl_agent = TabularRLAgent(actions=["scale", "reconfigure", "reroute"])
decision_engine = DecisionEngine(optimizer, rl_agent)
dispatch_log: List[Dict[str, Any]] = []
anomaly_log: List[Dict[str, Any]] = []
anomaly_features: List[List[float]] = []


class LoggingDispatcher:
    """Dispatcher that records actions for inspection."""

    def dispatch(self, action: Dict[str, Any]) -> None:
        dispatch_log.append(action)


dispatcher = LoggingDispatcher()
adapter = OMERTAOSAdapter(dispatcher)
controller = SelfEvolvingController(decision_engine, adapter)


def register_event(event: Dict[str, Any]) -> None:
    """Update in-memory analytics state with the provided event."""
    case_id = event["case_id"]
    case_traces[case_id].append(event["activity"])
    duration = event.get("duration_ms")
    status_flag = 1.0 if event.get("status") == "error" else 0.0
    if duration is not None:
        time_predictor.update(event["activity"], float(duration))
    anomaly_features.append([float(duration or 0.0), status_flag])
    events_seen = len(anomaly_features)
    if events_seen >= anomaly_detector.model.min_samples:
        anomaly_detector.fit(anomaly_features)
        labels = anomaly_detector.detect(anomaly_features[-anomaly_detector.model.min_samples :])
        if -1 in labels:
            anomaly_log.append({"case_id": case_id, "activity": event["activity"], "status": "anomaly"})


def rebuild_discovery_model() -> None:
    """Refresh discovery and conformance models based on known traces."""
    global allowed_relations
    allowed_relations.clear()
    allowed_relations.update(discovery_engine.discover_relations(case_traces))


def latest_metrics() -> Dict[str, float]:
    """Compute KPIs from stored events."""
    events = event_sink.list_events()
    activity_durations = performance_analyzer.avg_activity_duration(events)
    throughput = len(case_traces)
    latency = sum(activity_durations.values()) / len(activity_durations) if activity_durations else 0.0
    error_rate = (
        sum(1 for event in events if event.get("status") == "error") / len(events)
        if events
        else 0.0
    )
    return {
        "throughput": float(throughput),
        "latency": float(latency),
        "error_rate": float(error_rate),
    }


def proposed_actions(context_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run the self-evolving controller for the given context."""
    return controller.tick(context_payload)
