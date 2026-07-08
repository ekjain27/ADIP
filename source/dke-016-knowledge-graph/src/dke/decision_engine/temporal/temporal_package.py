from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import TemporalDecision, TemporalDecisionPackage
from .temporal_validator import TemporalValidator


class TemporalPackageBuilder:
    def __init__(self, validator: TemporalValidator | None = None) -> None:
        self.validator = validator or TemporalValidator()

    def build(
        self,
        temporal_results: tuple[TemporalDecision, ...],
        selected_result: TemporalDecision | None,
        timeline_summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> TemporalDecisionPackage:
        package_metadata = {
            "module": "DIE-015",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.temporal",
        }
        package_metadata.update(metadata or {})
        package = TemporalDecisionPackage(
            temporal_results=temporal_results,
            selected_result=selected_result,
            timeline_summary=timeline_summary or self._summary(temporal_results, selected_result),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, results: tuple[TemporalDecision, ...], selected: TemporalDecision | None) -> str:
        if not results:
            return "No governance evaluations were available for temporal lineage tracking."
        if selected is None:
            return f"Generated {len(results)} temporal decision ledger(s), but no selected result is available."
        return f"Selected temporal lineage for {selected.alternative_id} with stability score {selected.stability_score:.3f}."
