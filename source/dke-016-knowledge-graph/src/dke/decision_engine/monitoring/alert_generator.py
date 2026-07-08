from __future__ import annotations

from .models import DecisionAlert, MonitoringMetric


class AlertGenerator:
    def generate(
        self,
        alternative_id: str,
        health_score: float,
        workflow_status: str,
        metrics: tuple[MonitoringMetric, ...],
        drift: dict[str, float],
    ) -> tuple[DecisionAlert, ...]:
        alerts: list[DecisionAlert] = []
        if workflow_status in {"degraded", "critical"}:
            alerts.append(self._alert(alternative_id, "health_degradation", "critical" if workflow_status == "critical" else "high", "workflow_health", f"Workflow health is {workflow_status}.", "Review workflow execution and trigger remediation."))
        for drift_name, drift_value in drift.items():
            if drift_value >= 0.65:
                alerts.append(self._alert(alternative_id, drift_name, "high", drift_name, f"{drift_name.replace('_', ' ').title()} detected at {drift_value:.3f}.", "Escalate monitoring and review adaptive controls."))
            elif drift_value >= 0.45:
                alerts.append(self._alert(alternative_id, drift_name, "medium", drift_name, f"{drift_name.replace('_', ' ').title()} requires watch.", "Increase checkpoint review frequency."))
        for metric in metrics:
            if metric.name == "exception_count" and metric.value >= 0.50:
                alerts.append(self._alert(alternative_id, "excessive_exceptions", "high", metric.metric_id, "Exception signal exceeds workflow tolerance.", "Activate exception recovery and fallback workflow review."))
            elif metric.status == "degraded":
                alerts.append(self._alert(alternative_id, "metric_degraded", "medium", metric.metric_id, f"Metric {metric.name} is degraded.", "Review related workflow stage and mitigation plan."))
        return tuple(dict((alert.alert_id, alert) for alert in alerts).values())

    def _alert(
        self,
        alternative_id: str,
        alert_type: str,
        severity: str,
        related_metric: str,
        message: str,
        recommended_action: str,
    ) -> DecisionAlert:
        clean = alternative_id.lower().replace(" ", "-").replace("_", "-")
        return DecisionAlert(
            alert_id=f"alert-{clean}-{alert_type}-{related_metric}".replace("_", "-"),
            alert_type=alert_type,
            severity=severity,
            message=message,
            related_metric=related_metric,
            recommended_action=recommended_action,
            metadata={"alternative_id": alternative_id},
        )
