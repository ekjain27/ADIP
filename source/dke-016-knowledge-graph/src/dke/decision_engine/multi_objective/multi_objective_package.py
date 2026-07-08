from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import BalancedResult, MultiObjective, MultiObjectiveDecisionPackage, ObjectiveScore, ParetoResult, TradeoffMatrix
from .multi_objective_validator import MultiObjectiveValidator


class MultiObjectivePackageBuilder:
    def __init__(self, validator: MultiObjectiveValidator | None = None) -> None:
        self.validator = validator or MultiObjectiveValidator()

    def build(
        self,
        objectives: tuple[MultiObjective, ...],
        objective_scores: tuple[ObjectiveScore, ...],
        pareto_results: tuple[ParetoResult, ...],
        tradeoff_matrix: TradeoffMatrix,
        balanced_results: tuple[BalancedResult, ...],
        selected_result: BalancedResult | None,
        optimization_strategy: str = "deterministic_multi_objective_optimization",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> MultiObjectiveDecisionPackage:
        package_metadata = {
            "module": "DIE-011",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.multi_objective",
        }
        package_metadata.update(metadata or {})
        package = MultiObjectiveDecisionPackage(
            objectives=objectives,
            objective_scores=objective_scores,
            pareto_results=pareto_results,
            tradeoff_matrix=tradeoff_matrix,
            balanced_results=balanced_results,
            selected_result=selected_result,
            optimization_strategy=optimization_strategy,
            summary=summary or self._summary(objective_scores, selected_result),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, scores: tuple[ObjectiveScore, ...], selected: BalancedResult | None) -> str:
        if not scores:
            return "No learning results were available for multi-objective optimization."
        if selected is None:
            return f"Scored {len(scores)} alternative(s), but no balanced result was selected."
        return f"Selected {selected.alternative_id} with balance score {selected.balance_score:.3f} across {len(selected.objective_score.scores)} objectives."
