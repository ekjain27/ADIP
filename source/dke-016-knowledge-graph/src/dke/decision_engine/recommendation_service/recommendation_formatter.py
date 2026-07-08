from __future__ import annotations

from decision_engine.monitoring import DecisionHealth


class RecommendationFormatter:
    VALID_FORMATS = {"detailed", "summary", "executive", "technical"}

    def format(self, health: DecisionHealth, format_type: str = "summary") -> str:
        if format_type not in self.VALID_FORMATS:
            raise ValueError(f"unsupported recommendation format: {format_type}")
        if format_type == "executive":
            return f"{health.alternative_id}: {health.workflow_status} health, score {health.health_score:.3f}."
        if format_type == "technical":
            return (
                f"{health.alternative_id} health={health.health_score:.3f}; "
                f"risk_drift={health.risk_drift:.3f}; confidence_drift={health.confidence_drift:.3f}; "
                f"governance_drift={health.governance_drift:.3f}; alerts={len(health.alerts)}."
            )
        if format_type == "detailed":
            actions = "; ".join(alert.recommended_action for alert in health.alerts) or "Continue monitoring."
            return f"Decision {health.alternative_id} is {health.workflow_status} with health score {health.health_score:.3f}. Recommended actions: {actions}"
        return f"Monitor {health.alternative_id}: status {health.workflow_status}, health {health.health_score:.3f}."
