from __future__ import annotations

from typing import Any

from decision_engine.core import DecisionState
from decision_engine.core.models import utc_now

from .alternative_validator import AlternativeValidator
from .models import AlternativeDecision, AlternativeDecisionPackage


class AlternativePackageBuilder:
    def __init__(self, validator: AlternativeValidator | None = None) -> None:
        self.validator = validator or AlternativeValidator()

    def build(
        self,
        alternatives: tuple[AlternativeDecision, ...],
        decision_state: DecisionState | None = None,
        generation_strategy: str = "deterministic_rule_based",
        metadata: dict[str, Any] | None = None,
    ) -> AlternativeDecisionPackage:
        self.validator.validate(alternatives, decision_state)
        package_metadata = {
            "module": "DIE-002",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.alternatives",
        }
        package_metadata.update(metadata or {})
        return AlternativeDecisionPackage(
            alternatives=alternatives,
            total_generated=len(alternatives),
            generation_strategy=generation_strategy,
            metadata=package_metadata,
        )
