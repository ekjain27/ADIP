from __future__ import annotations

from decision_engine.recommendation_service import RecommendationResponse

from .models import DecisionManifest


class DecisionManifestBuilder:
    def build(self, response: RecommendationResponse) -> DecisionManifest:
        governance_status = self._governance_status(response)
        monitoring_status = response.health_status
        workflow_status = response.health_status
        return DecisionManifest(
            manifest_id=f"manifest-{response.alternative_id}".lower().replace(" ", "-").replace("_", "-"),
            alternative_id=response.alternative_id,
            decision_title=response.title,
            decision_summary=response.summary,
            recommendation_priority=response.priority,
            governance_status=governance_status,
            monitoring_status=monitoring_status,
            workflow_status=workflow_status,
            confidence=response.confidence,
            metadata={
                "response_id": response.response_id,
                "source": "Decision Recommendation Interface Fabric",
                "response_metadata": dict(response.metadata),
            },
        )

    def _governance_status(self, response: RecommendationResponse) -> str:
        governance_drift = float(response.metadata.get("governance_drift", 0.0))
        if governance_drift >= 0.70 or response.health_status == "critical":
            return "blocked"
        if governance_drift >= 0.40 or response.priority in {"critical", "high"}:
            return "review_required"
        return "compliant"
