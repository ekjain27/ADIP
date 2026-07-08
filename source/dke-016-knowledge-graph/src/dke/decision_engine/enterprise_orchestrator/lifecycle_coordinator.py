from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.recommendation_service import RecommendationResponse, RecommendationServicePackage

from .models import LifecycleState
from .readiness_assessor import ReadinessAssessor


class LifecycleCoordinator:
    STAGES = (
        "recommendation",
        "delivery_readiness",
        "monitoring",
        "workflow",
        "adaptive_behavior",
        "temporal_lineage",
        "governance",
        "provenance",
        "strategic_plan",
        "enterprise_summary",
    )

    def __init__(self, readiness_assessor: ReadinessAssessor | None = None) -> None:
        self.readiness_assessor = readiness_assessor or ReadinessAssessor()

    def coordinate(
        self,
        recommendation_package: RecommendationServicePackage,
        response: RecommendationResponse,
    ) -> LifecycleState:
        completed = self._completed_stages(recommendation_package, response)
        blocked = self._blocked_stages(response)
        pending = tuple(stage for stage in self.STAGES if stage not in completed and stage not in blocked)
        readiness_score = self._readiness_score(completed, blocked, response)
        current_stage = blocked[0] if blocked else (pending[0] if pending else "enterprise_summary")
        return LifecycleState(
            state_id=f"lifecycle-{response.alternative_id}".lower().replace(" ", "-").replace("_", "-"),
            current_stage=current_stage,
            completed_stages=completed,
            pending_stages=pending,
            blocked_stages=blocked,
            readiness_score=readiness_score,
            metadata={
                "service_strategy": recommendation_package.service_strategy,
                "selected_response": response == recommendation_package.selected_response,
                "delivery_count": len(self._deliveries_for_response(recommendation_package, response)),
            },
        )

    def _completed_stages(
        self,
        recommendation_package: RecommendationServicePackage,
        response: RecommendationResponse,
    ) -> tuple[str, ...]:
        completed = [
            "recommendation",
            "monitoring",
            "workflow",
            "adaptive_behavior",
            "temporal_lineage",
            "governance",
            "provenance",
            "strategic_plan",
        ]
        if self._deliveries_for_response(recommendation_package, response):
            completed.append("delivery_readiness")
        if response.recommendation:
            completed.append("enterprise_summary")
        return tuple(stage for stage in self.STAGES if stage in completed)

    def _blocked_stages(self, response: RecommendationResponse) -> tuple[str, ...]:
        blocked: list[str] = []
        if response.health_status == "critical":
            blocked.append("monitoring")
        if response.priority == "critical":
            blocked.append("governance")
        return tuple(blocked)

    def _readiness_score(
        self,
        completed: tuple[str, ...],
        blocked: tuple[str, ...],
        response: RecommendationResponse,
    ) -> float:
        completion_ratio = len(completed) / len(self.STAGES)
        response_score = self.readiness_assessor.score(response)
        blocked_penalty = min(len(blocked) * 0.15, 0.30)
        return clamp_confidence((completion_ratio * 0.45) + (response_score * 0.55) - blocked_penalty)

    def _deliveries_for_response(
        self,
        recommendation_package: RecommendationServicePackage,
        response: RecommendationResponse,
    ):
        return tuple(
            delivery
            for delivery in recommendation_package.deliveries
            if delivery.metadata.get("alternative_id") == response.alternative_id
        )
