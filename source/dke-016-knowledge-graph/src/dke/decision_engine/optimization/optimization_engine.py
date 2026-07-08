from __future__ import annotations

import logging

from decision_engine.core.models import clamp_confidence
from decision_engine.explanation import DecisionExplanation, ExplanationDecisionPackage

from .constraint_optimizer import ConstraintOptimizer
from .models import OptimizationObjective, OptimizationResult, OptimizedDecisionPackage
from .objective_optimizer import ObjectiveOptimizer
from .optimization_package import OptimizationPackageBuilder
from .optimization_validator import OptimizationValidator
from .tradeoff_analyzer import TradeoffAnalyzer

logger = logging.getLogger(__name__)


class OptimizationEngine:
    STRATEGY = "rule_based_multi_objective_optimization"

    def __init__(
        self,
        objective_optimizer: ObjectiveOptimizer | None = None,
        constraint_optimizer: ConstraintOptimizer | None = None,
        tradeoff_analyzer: TradeoffAnalyzer | None = None,
        package_builder: OptimizationPackageBuilder | None = None,
        validator: OptimizationValidator | None = None,
    ) -> None:
        self.objective_optimizer = objective_optimizer or ObjectiveOptimizer()
        self.constraint_optimizer = constraint_optimizer or ConstraintOptimizer()
        self.tradeoff_analyzer = tradeoff_analyzer or TradeoffAnalyzer()
        self.package_builder = package_builder or OptimizationPackageBuilder()
        self.validator = validator or OptimizationValidator()

    def optimize(self, explanation_package: ExplanationDecisionPackage) -> OptimizedDecisionPackage:
        if not isinstance(explanation_package, ExplanationDecisionPackage):
            raise ValueError("OptimizationEngine.optimize requires an ExplanationDecisionPackage")
        logger.info("Optimizing decision explanations")
        objectives = self.objective_optimizer.default_objectives()
        self.validator.validate_objectives(objectives)
        results = tuple(self._optimize_explanation(explanation, objectives) for explanation in explanation_package.explanations)
        selected = self._selected_result(results, explanation_package.selected_explanation)
        return self.package_builder.build(
            results,
            selected,
            optimization_strategy=self.STRATEGY,
            metadata={
                "source_explanation_strategy": explanation_package.explanation_strategy,
                "objective_count": len(objectives),
            },
        )

    def _optimize_explanation(
        self,
        explanation: DecisionExplanation,
        objectives: tuple[OptimizationObjective, ...],
    ) -> OptimizationResult:
        objective_results = self.objective_optimizer.optimize(explanation, objectives)
        objective_gain = self.objective_optimizer.improvement_score(objective_results, objectives)
        constraint_result = self.constraint_optimizer.optimize(explanation)
        tradeoffs = self.tradeoff_analyzer.analyze(explanation)
        original_score = clamp_confidence(explanation.confidence)
        gain = min(0.18, max(0.0, (objective_gain - original_score) * 0.3 + 0.06))
        optimized_score = clamp_confidence(original_score + gain)
        confidence = clamp_confidence((explanation.confidence + optimized_score + constraint_result["satisfaction_score"]) / 3.0)
        improvements = (
            f"Increase objective satisfaction to {objective_gain:.3f}.",
            f"Raise constraint satisfaction to {constraint_result['satisfaction_score']:.3f}.",
            *constraint_result["improvements"],
        )
        if constraint_result["violations"]:
            improvements = (*improvements, "Resolve detected constraint violations before final commitment.")
        return OptimizationResult(
            alternative_id=explanation.alternative_id,
            original_score=original_score,
            optimized_score=optimized_score,
            improvements=tuple(improvements),
            tradeoffs=tradeoffs,
            objective_results=objective_results,
            confidence=confidence,
            metadata={
                "optimization_gain": round(optimized_score - original_score, 6),
                "constraint_violations": constraint_result["violations"],
                "constraint_satisfaction_score": constraint_result["satisfaction_score"],
            },
        )

    def _selected_result(
        self,
        results: tuple[OptimizationResult, ...],
        selected_explanation: DecisionExplanation | None,
    ) -> OptimizationResult | None:
        if not results:
            return None
        if selected_explanation is not None:
            for result in results:
                if result.alternative_id == selected_explanation.alternative_id:
                    return result
        return max(results, key=lambda result: result.optimized_score)
