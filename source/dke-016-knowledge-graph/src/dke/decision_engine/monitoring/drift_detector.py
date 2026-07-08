from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.workflow import WorkflowDecision

from .models import MonitoringMetric


class DriftDetector:
    def detect(self, workflow: WorkflowDecision, metrics: tuple[MonitoringMetric, ...]) -> dict[str, float]:
        metric_values = {metric.name: metric.value for metric in metrics}
        exception_pressure = metric_values.get("exception_count", 0.0)
        approval_pressure = metric_values.get("approval_count", 0.0)
        routing_pressure = metric_values.get("routing_complexity", 0.0)
        completion_gap = 1.0 - clamp_confidence(workflow.completion_score)
        risk_drift = clamp_confidence((exception_pressure * 0.45) + (routing_pressure * 0.25) + (completion_gap * 0.30))
        confidence_drift = clamp_confidence((completion_gap * 0.60) + (approval_pressure * 0.20) + (exception_pressure * 0.20))
        governance_drift = clamp_confidence((approval_pressure * 0.45) + (exception_pressure * 0.35) + (routing_pressure * 0.20))
        return {
            "risk_drift": risk_drift,
            "confidence_drift": confidence_drift,
            "governance_drift": governance_drift,
        }
