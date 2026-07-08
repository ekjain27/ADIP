from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now
from decision_engine.evaluation import EvaluatedDecisionPackage

from .models import RankedAlternative, RankedDecisionPackage
from .ranking_validator import RankingValidator


class RankingPackageBuilder:
    def __init__(self, validator: RankingValidator | None = None) -> None:
        self.validator = validator or RankingValidator()

    def build(
        self,
        ranked_alternatives: tuple[RankedAlternative, ...],
        selected_alternative: RankedAlternative | None,
        top_alternatives: tuple[RankedAlternative, ...],
        evaluated_package: EvaluatedDecisionPackage | None = None,
        ranking_strategy: str = "deterministic_weighted_rank",
        selection_strategy: str = "top_ranked_selection",
        metadata: dict[str, Any] | None = None,
    ) -> RankedDecisionPackage:
        package_metadata = {
            "module": "DIE-004",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.ranking",
        }
        package_metadata.update(metadata or {})
        package = RankedDecisionPackage(
            ranked_alternatives=ranked_alternatives,
            selected_alternative=selected_alternative,
            top_alternatives=top_alternatives,
            total_ranked=len(ranked_alternatives),
            ranking_strategy=ranking_strategy,
            selection_strategy=selection_strategy,
            metadata=package_metadata,
        )
        self.validator.validate(package, evaluated_package)
        return package
