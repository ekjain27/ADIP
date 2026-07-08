from __future__ import annotations

import logging

from decision_engine.learning import LearningDecisionPackage

from .balance_optimizer import BalanceOptimizer
from .models import MultiObjectiveDecisionPackage
from .multi_objective_package import MultiObjectivePackageBuilder
from .multi_objective_validator import MultiObjectiveValidator
from .objective_registry import ObjectiveRegistry
from .objective_scorer import ObjectiveScorer
from .pareto_analyzer import ParetoAnalyzer
from .tradeoff_matrix import TradeoffMatrixBuilder

logger = logging.getLogger(__name__)


class MultiObjectiveEngine:
    STRATEGY = "deterministic_multi_objective_optimization"

    def __init__(
        self,
        objective_registry: ObjectiveRegistry | None = None,
        objective_scorer: ObjectiveScorer | None = None,
        pareto_analyzer: ParetoAnalyzer | None = None,
        tradeoff_matrix_builder: TradeoffMatrixBuilder | None = None,
        balance_optimizer: BalanceOptimizer | None = None,
        package_builder: MultiObjectivePackageBuilder | None = None,
        validator: MultiObjectiveValidator | None = None,
    ) -> None:
        self.objective_registry = objective_registry or ObjectiveRegistry()
        self.objective_scorer = objective_scorer or ObjectiveScorer(self.objective_registry)
        self.pareto_analyzer = pareto_analyzer or ParetoAnalyzer()
        self.tradeoff_matrix_builder = tradeoff_matrix_builder or TradeoffMatrixBuilder()
        self.balance_optimizer = balance_optimizer or BalanceOptimizer()
        self.package_builder = package_builder or MultiObjectivePackageBuilder()
        self.validator = validator or MultiObjectiveValidator()

    def optimize(self, learning_package: LearningDecisionPackage) -> MultiObjectiveDecisionPackage:
        if not isinstance(learning_package, LearningDecisionPackage):
            raise ValueError("MultiObjectiveEngine.optimize requires a LearningDecisionPackage")
        logger.info("Running deterministic multi-objective optimization")
        objectives = self.objective_registry.default_objectives()
        self.validator.validate_objectives(objectives)
        objective_scores = self.objective_scorer.score(learning_package, objectives)
        pareto_results = self.pareto_analyzer.analyze(objective_scores)
        tradeoff_matrix = self.tradeoff_matrix_builder.build(objective_scores)
        balanced_results = self.balance_optimizer.optimize(objective_scores, pareto_results, tradeoff_matrix)
        selected_result = self._selected_result(balanced_results, learning_package.selected_learning.alternative_id if learning_package.selected_learning else "")
        return self.package_builder.build(
            objectives,
            objective_scores,
            pareto_results,
            tradeoff_matrix,
            balanced_results,
            selected_result,
            optimization_strategy=self.STRATEGY,
            metadata={
                "source_learning_strategy": learning_package.learning_strategy,
                "learning_result_count": len(learning_package.learning_results),
            },
        )

    def _selected_result(self, balanced_results, selected_learning_id: str):
        if not balanced_results:
            return None
        preferred = tuple(result for result in balanced_results if result.alternative_id == selected_learning_id)
        if preferred:
            best = preferred[0]
            max_balance = max(result.balance_score for result in balanced_results)
            if best.balance_score >= max_balance * 0.95:
                return best
        return self.balance_optimizer.select(balanced_results)
