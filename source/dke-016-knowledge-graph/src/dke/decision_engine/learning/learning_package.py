from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .learning_validator import LearningValidator
from .models import LearningDecisionPackage, LearningResult


class LearningPackageBuilder:
    def __init__(self, validator: LearningValidator | None = None) -> None:
        self.validator = validator or LearningValidator()

    def build(
        self,
        learning_results: tuple[LearningResult, ...],
        selected_learning: LearningResult | None,
        history: dict[str, Any],
        learning_strategy: str = "deterministic_decision_learning",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> LearningDecisionPackage:
        package_metadata = {
            "module": "DIE-010",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.learning",
        }
        package_metadata.update(metadata or {})
        package = LearningDecisionPackage(
            learning_results=learning_results,
            selected_learning=selected_learning,
            history=history,
            summary=summary or self._summary(learning_results, selected_learning),
            learning_strategy=learning_strategy,
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, results: tuple[LearningResult, ...], selected: LearningResult | None) -> str:
        if not results:
            return "No scenario comparisons were available for decision learning."
        if selected is None:
            return f"Processed {len(results)} learning result(s), but no selected learning result is available."
        return f"Selected {selected.alternative_id} learning score {selected.learning_score:.3f} with confidence {selected.confidence_update.new_confidence:.3f}."
