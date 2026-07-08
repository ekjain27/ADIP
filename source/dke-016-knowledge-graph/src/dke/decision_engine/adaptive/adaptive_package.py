from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .adaptive_validator import AdaptiveValidator
from .models import AdaptiveDecision, AdaptiveDecisionPackage


class AdaptivePackageBuilder:
    def __init__(self, validator: AdaptiveValidator | None = None) -> None:
        self.validator = validator or AdaptiveValidator()

    def build(
        self,
        adaptive_results: tuple[AdaptiveDecision, ...],
        selected_adaptive_result: AdaptiveDecision | None,
        adaptation_strategy: str = "deterministic_adaptive_decision_behavior_model",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AdaptiveDecisionPackage:
        package_metadata = {
            "module": "DIE-016",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.adaptive",
        }
        package_metadata.update(metadata or {})
        package = AdaptiveDecisionPackage(
            adaptive_results=adaptive_results,
            selected_adaptive_result=selected_adaptive_result,
            adaptation_strategy=adaptation_strategy,
            summary=summary or self._summary(adaptive_results, selected_adaptive_result),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, results: tuple[AdaptiveDecision, ...], selected: AdaptiveDecision | None) -> str:
        if not results:
            return "No temporal decisions were available for adaptive behavior modeling."
        if selected is None:
            return f"Generated {len(results)} adaptive result(s), but no selected result is available."
        return f"Selected adaptive behavior for {selected.alternative_id} with score {selected.adaptation_score:.3f}."
