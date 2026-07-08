from __future__ import annotations

from .models import DecisionManifest, EnterpriseDecision, EnterpriseDecisionPackage, LifecycleState
from .readiness_assessor import ReadinessAssessor


class OrchestrationValidator:
    VALID_GOVERNANCE_STATUSES = {"compliant", "review_required", "blocked"}
    VALID_HEALTH_STATUSES = {"healthy", "watch", "degraded", "critical"}
    VALID_WORKFLOW_STATUSES = {"healthy", "watch", "degraded", "critical"}

    def validate_manifest(self, manifest: DecisionManifest) -> None:
        if not manifest.manifest_id.strip() or not manifest.alternative_id.strip():
            raise ValueError("manifest id and alternative id are required")
        if manifest.governance_status not in self.VALID_GOVERNANCE_STATUSES:
            raise ValueError(f"invalid governance status: {manifest.governance_status}")
        if manifest.monitoring_status not in self.VALID_HEALTH_STATUSES:
            raise ValueError(f"invalid monitoring status: {manifest.monitoring_status}")
        if manifest.workflow_status not in self.VALID_WORKFLOW_STATUSES:
            raise ValueError(f"invalid workflow status: {manifest.workflow_status}")
        if not 0.0 <= manifest.confidence <= 1.0:
            raise ValueError("manifest confidence must be between 0 and 1")

    def validate_lifecycle_state(self, lifecycle_state: LifecycleState) -> None:
        if not lifecycle_state.state_id.strip():
            raise ValueError("lifecycle state id is required")
        if not 0.0 <= lifecycle_state.readiness_score <= 1.0:
            raise ValueError("lifecycle readiness score must be between 0 and 1")
        all_stages = (
            lifecycle_state.completed_stages
            + lifecycle_state.pending_stages
            + lifecycle_state.blocked_stages
        )
        if len(all_stages) != len(set(all_stages)):
            raise ValueError("lifecycle stages must not overlap")
        if lifecycle_state.current_stage not in all_stages and lifecycle_state.current_stage != "enterprise_summary":
            raise ValueError("current lifecycle stage must be represented in lifecycle state")

    def validate_decision(self, decision: EnterpriseDecision) -> None:
        if decision.alternative_id != decision.manifest.alternative_id:
            raise ValueError("manifest alternative reference must match enterprise decision")
        self.validate_manifest(decision.manifest)
        self.validate_lifecycle_state(decision.lifecycle_state)
        if not 0.0 <= decision.readiness_score <= 1.0:
            raise ValueError("enterprise readiness score must be between 0 and 1")
        if decision.enterprise_status not in ReadinessAssessor.VALID_STATUSES:
            raise ValueError(f"invalid enterprise status: {decision.enterprise_status}")

    def validate_package(self, package: EnterpriseDecisionPackage) -> None:
        if not isinstance(package, EnterpriseDecisionPackage):
            raise ValueError("Expected EnterpriseDecisionPackage")
        for decision in package.enterprise_decisions:
            self.validate_decision(decision)
        alternatives = {decision.alternative_id for decision in package.enterprise_decisions}
        if package.enterprise_decisions and package.selected_enterprise_decision is None:
            raise ValueError("selected enterprise decision is required when decisions exist")
        if not package.enterprise_decisions and package.selected_enterprise_decision is not None:
            raise ValueError("selected enterprise decision must be None when no decisions exist")
        if (
            package.selected_enterprise_decision is not None
            and package.selected_enterprise_decision.alternative_id not in alternatives
        ):
            raise ValueError("selected enterprise decision must be present in decisions")
