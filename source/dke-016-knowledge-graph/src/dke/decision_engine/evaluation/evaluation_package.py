from __future__ import annotations

from typing import Any

from decision_engine.alternatives import AlternativeDecisionPackage
from decision_engine.core.models import utc_now

from .criteria import default_criteria
from .evaluation_validator import EvaluationValidator
from .models import EvaluatedAlternative, EvaluatedDecisionPackage, EvaluationCriteria


class EvaluationPackageBuilder:
    def __init__(self, validator: EvaluationValidator | None = None) -> None:
        self.validator = validator or EvaluationValidator()

    def build(
        self,
        evaluated_alternatives: tuple[EvaluatedAlternative, ...],
        alternative_package: AlternativeDecisionPackage | None = None,
        criteria: tuple[EvaluationCriteria, ...] | None = None,
        evaluation_strategy: str = "deterministic_weighted_scoring",
        metadata: dict[str, Any] | None = None,
    ) -> EvaluatedDecisionPackage:
        package_metadata = {
            "module": "DIE-003",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.evaluation",
        }
        package_metadata.update(metadata or {})
        package = EvaluatedDecisionPackage(
            evaluated_alternatives=evaluated_alternatives,
            total_evaluated=len(evaluated_alternatives),
            evaluation_strategy=evaluation_strategy,
            criteria=criteria or default_criteria(),
            metadata=package_metadata,
        )
        self.validator.validate(package, alternative_package)
        return package
