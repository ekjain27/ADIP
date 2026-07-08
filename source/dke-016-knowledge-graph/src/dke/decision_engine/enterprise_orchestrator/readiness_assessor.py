from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.recommendation_service import RecommendationResponse


class ReadinessAssessor:
    VALID_STATUSES = {"ready", "review_required", "blocked", "incomplete"}

    def assess(
        self,
        response: RecommendationResponse,
        delivery_ready: bool = True,
    ) -> tuple[float, str]:
        score = self.score(response, delivery_ready)
        return score, self.status(score, response, delivery_ready)

    def score(self, response: RecommendationResponse, delivery_ready: bool = True) -> float:
        priority_factor = {
            "low": 1.0,
            "medium": 0.82,
            "high": 0.58,
            "critical": 0.34,
        }.get(response.priority, 0.0)
        health_factor = {
            "healthy": 1.0,
            "watch": 0.75,
            "degraded": 0.48,
            "critical": 0.20,
        }.get(response.health_status, 0.0)
        alert_factor = max(0.0, 1.0 - min(len(response.alerts), 5) * 0.12)
        delivery_factor = 1.0 if delivery_ready else 0.55
        score = (
            response.confidence * 0.35
            + health_factor * 0.25
            + priority_factor * 0.20
            + alert_factor * 0.10
            + delivery_factor * 0.10
        )
        return clamp_confidence(score)

    def status(
        self,
        score: float,
        response: RecommendationResponse,
        delivery_ready: bool = True,
    ) -> str:
        if not delivery_ready:
            return "incomplete"
        if response.priority == "critical" or response.health_status == "critical":
            return "blocked"
        if score >= 0.78 and response.priority in {"low", "medium"} and not response.alerts:
            return "ready"
        if score < 0.45 or response.health_status == "degraded":
            return "blocked"
        return "review_required"
