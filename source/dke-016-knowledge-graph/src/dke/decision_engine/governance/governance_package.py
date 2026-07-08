from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import GovernanceDecisionPackage, GovernanceEvaluation, GovernanceMesh
from .governance_validator import GovernanceValidator


class GovernancePackageBuilder:
    def __init__(self, validator: GovernanceValidator | None = None) -> None:
        self.validator = validator or GovernanceValidator()

    def build(
        self,
        evaluations: tuple[GovernanceEvaluation, ...],
        selected_evaluation: GovernanceEvaluation | None,
        mesh: GovernanceMesh,
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> GovernanceDecisionPackage:
        package_metadata = {
            "module": "DIE-014",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.governance",
        }
        package_metadata.update(metadata or {})
        package = GovernanceDecisionPackage(
            evaluations=evaluations,
            selected_evaluation=selected_evaluation,
            mesh=mesh,
            summary=summary or self._summary(evaluations, selected_evaluation),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, evaluations: tuple[GovernanceEvaluation, ...], selected: GovernanceEvaluation | None) -> str:
        if not evaluations:
            return "No provenance results were available for governance evaluation."
        if selected is None:
            return f"Generated {len(evaluations)} governance evaluation(s), but no selected evaluation is available."
        return f"Selected governance evaluation for {selected.alternative_id} with status {selected.governance_status} and score {selected.overall_score:.3f}."
