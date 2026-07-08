from __future__ import annotations

from decision_engine.monitoring import DecisionHealth


class PriorityAssigner:
    VALID_PRIORITIES = {"critical", "high", "medium", "low"}

    def assign(self, health: DecisionHealth) -> str:
        severities = {alert.severity for alert in health.alerts}
        max_drift = max(health.risk_drift, health.confidence_drift, health.governance_drift)
        if health.workflow_status == "critical" or "critical" in severities or health.health_score < 0.45:
            return "critical"
        if health.workflow_status == "degraded" or "high" in severities or max_drift >= 0.65:
            return "high"
        if health.workflow_status == "watch" or "medium" in severities or max_drift >= 0.40:
            return "medium"
        return "low"
