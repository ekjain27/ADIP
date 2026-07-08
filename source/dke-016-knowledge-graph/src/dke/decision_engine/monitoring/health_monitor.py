from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .alert_generator import AlertGenerator
from .models import DecisionHealth, MonitoringMetric


class HealthMonitor:
    def __init__(self, alert_generator: AlertGenerator | None = None) -> None:
        self.alert_generator = alert_generator or AlertGenerator()

    def evaluate(
        self,
        alternative_id: str,
        metrics: tuple[MonitoringMetric, ...],
        drift: dict[str, float],
    ) -> DecisionHealth:
        metric_values = {metric.name: metric.value for metric in metrics}
        completion = metric_values.get("completion_score", 0.0)
        pressure = (
            metric_values.get("approval_count", 0.0) * 0.15
            + metric_values.get("exception_count", 0.0) * 0.25
            + metric_values.get("routing_complexity", 0.0) * 0.15
            + drift.get("risk_drift", 0.0) * 0.15
            + drift.get("confidence_drift", 0.0) * 0.15
            + drift.get("governance_drift", 0.0) * 0.15
        )
        health_score = clamp_confidence((completion * 0.55) + ((1.0 - clamp_confidence(pressure)) * 0.45))
        status = self._status(health_score)
        alerts = self.alert_generator.generate(alternative_id, health_score, status, metrics, drift)
        return DecisionHealth(
            alternative_id=alternative_id,
            health_score=health_score,
            workflow_status=status,
            risk_drift=drift.get("risk_drift", 0.0),
            confidence_drift=drift.get("confidence_drift", 0.0),
            governance_drift=drift.get("governance_drift", 0.0),
            metrics=metrics,
            alerts=alerts,
            metadata={"fabric": "Decision Health Monitoring Fabric"},
        )

    def _status(self, health_score: float) -> str:
        if health_score >= 0.80:
            return "healthy"
        if health_score >= 0.65:
            return "watch"
        if health_score >= 0.45:
            return "degraded"
        return "critical"
