from __future__ import annotations

import logging

from decision_engine.recommendation_service import RecommendationResponse, RecommendationServicePackage

from .decision_manifest import DecisionManifestBuilder
from .enterprise_package import EnterprisePackageBuilder
from .lifecycle_coordinator import LifecycleCoordinator
from .models import EnterpriseDecision
from .readiness_assessor import ReadinessAssessor

logger = logging.getLogger(__name__)


class EnterpriseDecisionOrchestrator:
    STRATEGY = "deterministic_enterprise_decision_orchestration_fabric"

    def __init__(
        self,
        manifest_builder: DecisionManifestBuilder | None = None,
        lifecycle_coordinator: LifecycleCoordinator | None = None,
        readiness_assessor: ReadinessAssessor | None = None,
        package_builder: EnterprisePackageBuilder | None = None,
    ) -> None:
        self.manifest_builder = manifest_builder or DecisionManifestBuilder()
        self.readiness_assessor = readiness_assessor or ReadinessAssessor()
        self.lifecycle_coordinator = lifecycle_coordinator or LifecycleCoordinator(self.readiness_assessor)
        self.package_builder = package_builder or EnterprisePackageBuilder()

    def orchestrate(self, recommendation_package: RecommendationServicePackage) -> object:
        if not isinstance(recommendation_package, RecommendationServicePackage):
            raise ValueError("EnterpriseDecisionOrchestrator.orchestrate requires a RecommendationServicePackage")
        logger.info("Building deterministic enterprise decision orchestration package")
        decisions = tuple(
            self._enterprise_decision(recommendation_package, response)
            for response in recommendation_package.responses
        )
        selected = self._selected_decision(
            decisions,
            recommendation_package.selected_response.alternative_id
            if recommendation_package.selected_response
            else "",
        )
        return self.package_builder.build(
            decisions,
            selected,
            orchestration_strategy=self.STRATEGY,
            metadata={
                "source_module": recommendation_package.metadata.get("module", "DIE-019"),
                "response_count": len(recommendation_package.responses),
                "fabric_links": (
                    "Decision Recommendation Interface Fabric",
                    "Decision Health Monitoring Fabric",
                    "Adaptive Decision Workflow Graph",
                    "Adaptive Decision Behavior Model",
                    "Temporal Decision Lineage Ledger",
                    "Dynamic Decision Governance Mesh",
                    "Decision Provenance Graph",
                ),
            },
        )

    def _enterprise_decision(
        self,
        recommendation_package: RecommendationServicePackage,
        response: RecommendationResponse,
    ) -> EnterpriseDecision:
        manifest = self.manifest_builder.build(response)
        lifecycle_state = self.lifecycle_coordinator.coordinate(recommendation_package, response)
        delivery_ready = bool(
            [
                delivery
                for delivery in recommendation_package.deliveries
                if delivery.metadata.get("alternative_id") == response.alternative_id
            ]
        )
        readiness_score, enterprise_status = self.readiness_assessor.assess(response, delivery_ready)
        combined_readiness = round((readiness_score * 0.65) + (lifecycle_state.readiness_score * 0.35), 6)
        final_status = self.readiness_assessor.status(combined_readiness, response, delivery_ready)
        return EnterpriseDecision(
            alternative_id=response.alternative_id,
            manifest=manifest,
            lifecycle_state=lifecycle_state,
            readiness_score=combined_readiness,
            enterprise_status=final_status,
            final_recommendation=response.recommendation,
            next_actions=response.next_actions,
            audit_notes=self._audit_notes(response, manifest, lifecycle_state),
            metadata={
                "response_id": response.response_id,
                "assessor_status": enterprise_status,
                "selected_response": response == recommendation_package.selected_response,
            },
        )

    def _audit_notes(
        self,
        response: RecommendationResponse,
        manifest,
        lifecycle_state,
    ) -> tuple[str, ...]:
        return (
            f"Recommendation priority: {response.priority}",
            f"Governance status: {manifest.governance_status}",
            f"Monitoring status: {manifest.monitoring_status}",
            f"Lifecycle current stage: {lifecycle_state.current_stage}",
        )

    def _selected_decision(
        self,
        decisions: tuple[EnterpriseDecision, ...],
        selected_alternative_id: str,
    ) -> EnterpriseDecision | None:
        if not decisions:
            return None
        if selected_alternative_id:
            for decision in decisions:
                if decision.alternative_id == selected_alternative_id:
                    return decision
        status_order = {"ready": 3, "review_required": 2, "incomplete": 1, "blocked": 0}
        return max(
            decisions,
            key=lambda decision: (
                status_order[decision.enterprise_status],
                decision.readiness_score,
                decision.manifest.confidence,
                decision.alternative_id,
            ),
        )
