from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .explanation_validator import ExplanationValidator
from .models import DecisionExplanation, ExplanationDecisionPackage


class ExplanationPackageBuilder:
    def __init__(self, validator: ExplanationValidator | None = None) -> None:
        self.validator = validator or ExplanationValidator()

    def build(
        self,
        explanations: tuple[DecisionExplanation, ...],
        selected_explanation: DecisionExplanation | None,
        explanation_strategy: str = "deterministic_rule_based_explanation",
        metadata: dict[str, Any] | None = None,
    ) -> ExplanationDecisionPackage:
        package_metadata = {
            "module": "DIE-006",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.explanation",
        }
        package_metadata.update(metadata or {})
        package = ExplanationDecisionPackage(
            explanations=explanations,
            selected_explanation=selected_explanation,
            total_explained=len(explanations),
            explanation_strategy=explanation_strategy,
            metadata=package_metadata,
        )
        self.validator.validate(package)
        return package
