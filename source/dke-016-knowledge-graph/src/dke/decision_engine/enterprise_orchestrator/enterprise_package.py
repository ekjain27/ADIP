from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import EnterpriseDecision, EnterpriseDecisionPackage
from .orchestration_validator import OrchestrationValidator


class EnterprisePackageBuilder:
    def __init__(self, validator: OrchestrationValidator | None = None) -> None:
        self.validator = validator or OrchestrationValidator()

    def build(
        self,
        enterprise_decisions: tuple[EnterpriseDecision, ...],
        selected_enterprise_decision: EnterpriseDecision | None,
        orchestration_strategy: str = "deterministic_enterprise_decision_orchestration_fabric",
        lifecycle_summary: str = "",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> EnterpriseDecisionPackage:
        package_metadata = {
            "module": "DIE-020",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.enterprise_orchestrator",
        }
        package_metadata.update(metadata or {})
        package = EnterpriseDecisionPackage(
            enterprise_decisions=enterprise_decisions,
            selected_enterprise_decision=selected_enterprise_decision,
            orchestration_strategy=orchestration_strategy,
            lifecycle_summary=lifecycle_summary or self._lifecycle_summary(enterprise_decisions),
            summary=summary or self._summary(enterprise_decisions, selected_enterprise_decision),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _lifecycle_summary(self, decisions: tuple[EnterpriseDecision, ...]) -> str:
        if not decisions:
            return "No recommendation service responses were available for enterprise orchestration."
        ready = sum(1 for decision in decisions if decision.enterprise_status == "ready")
        blocked = sum(1 for decision in decisions if decision.enterprise_status == "blocked")
        return f"Coordinated {len(decisions)} enterprise decision lifecycle(s): {ready} ready, {blocked} blocked."

    def _summary(
        self,
        decisions: tuple[EnterpriseDecision, ...],
        selected: EnterpriseDecision | None,
    ) -> str:
        if not decisions:
            return "No enterprise decision was selected because no recommendation responses were provided."
        if selected is None:
            return f"Created {len(decisions)} enterprise decision(s), but no selected enterprise decision is available."
        return (
            f"Selected enterprise decision for {selected.alternative_id} with status "
            f"{selected.enterprise_status} and readiness {selected.readiness_score:.3f}."
        )
