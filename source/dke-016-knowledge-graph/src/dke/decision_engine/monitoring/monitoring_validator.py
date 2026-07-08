from __future__ import annotations

from .models import DecisionAlert, DecisionHealth, MonitoringDecisionPackage, MonitoringMetric


class MonitoringValidator:
    VALID_METRIC_STATUSES = {"healthy", "watch", "degraded", "critical"}
    VALID_WORKFLOW_STATUSES = {"healthy", "watch", "degraded", "critical"}
    VALID_ALERT_SEVERITIES = {"low", "medium", "high", "critical"}

    def validate_metric(self, metric: MonitoringMetric) -> None:
        if not metric.metric_id.strip() or not metric.name.strip():
            raise ValueError("monitoring metric id and name are required")
        self._validate_unit(metric.value, "metric value")
        self._validate_unit(metric.threshold, "metric threshold")
        if metric.status not in self.VALID_METRIC_STATUSES:
            raise ValueError(f"invalid metric status: {metric.status}")

    def validate_alert(self, alert: DecisionAlert) -> None:
        if not alert.alert_id.strip():
            raise ValueError("decision alert id is required")
        if alert.severity not in self.VALID_ALERT_SEVERITIES:
            raise ValueError(f"invalid alert severity: {alert.severity}")
        if not alert.recommended_action.strip():
            raise ValueError("decision alert recommended action is required")

    def validate_health(self, health: DecisionHealth) -> None:
        if not health.alternative_id.strip():
            raise ValueError("DecisionHealth.alternative_id is required")
        self._validate_unit(health.health_score, "health score")
        self._validate_unit(health.risk_drift, "risk drift")
        self._validate_unit(health.confidence_drift, "confidence drift")
        self._validate_unit(health.governance_drift, "governance drift")
        if health.workflow_status not in self.VALID_WORKFLOW_STATUSES:
            raise ValueError(f"invalid workflow status: {health.workflow_status}")
        for metric in health.metrics:
            self.validate_metric(metric)
        for alert in health.alerts:
            self.validate_alert(alert)

    def validate_package(self, package: MonitoringDecisionPackage) -> None:
        if not isinstance(package, MonitoringDecisionPackage):
            raise ValueError("Expected MonitoringDecisionPackage")
        for result in package.monitoring_results:
            self.validate_health(result)
        if package.monitoring_results and package.selected_monitoring is None:
            raise ValueError("selected monitoring is required when monitoring results exist")
        if not package.monitoring_results and package.selected_monitoring is not None:
            raise ValueError("selected monitoring must be None when no monitoring results exist")
        if package.selected_monitoring is not None and package.selected_monitoring not in package.monitoring_results:
            raise ValueError("selected monitoring must be present in monitoring results")

    def _validate_unit(self, value: float, field_name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field_name} must be between 0 and 1")
