from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.monitoring import DecisionHealth, MonitoringDecisionPackage

from .models import RecommendationResponse
from .priority_assigner import PriorityAssigner
from .recommendation_formatter import RecommendationFormatter


class ResponseBuilder:
    def __init__(
        self,
        formatter: RecommendationFormatter | None = None,
        priority_assigner: PriorityAssigner | None = None,
    ) -> None:
        self.formatter = formatter or RecommendationFormatter()
        self.priority_assigner = priority_assigner or PriorityAssigner()

    def build(self, monitoring_package: MonitoringDecisionPackage) -> tuple[RecommendationResponse, ...]:
        return tuple(self.build_response(result, selected=result == monitoring_package.selected_monitoring) for result in monitoring_package.monitoring_results)

    def build_response(self, health: DecisionHealth, selected: bool = False) -> RecommendationResponse:
        priority = self.priority_assigner.assign(health)
        alerts = tuple(alert.message for alert in health.alerts)
        next_actions = tuple(dict.fromkeys(alert.recommended_action for alert in health.alerts)) or ("Continue deterministic monitoring.",)
        recommendation = self.formatter.format(health, "detailed" if selected else "summary")
        return RecommendationResponse(
            response_id=f"rec-{health.alternative_id}".lower().replace(" ", "-").replace("_", "-"),
            alternative_id=health.alternative_id,
            title=f"Recommendation for {health.alternative_id}",
            summary=self.formatter.format(health, "summary"),
            recommendation=recommendation,
            priority=priority,
            confidence=clamp_confidence(health.health_score),
            health_status=health.workflow_status,
            alerts=alerts,
            next_actions=next_actions,
            metadata={
                "selected_monitoring": selected,
                "risk_drift": health.risk_drift,
                "confidence_drift": health.confidence_drift,
                "governance_drift": health.governance_drift,
            },
        )
