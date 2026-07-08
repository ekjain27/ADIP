from __future__ import annotations

import logging

from decision_engine.alternatives import AlternativeDecision, AlternativeDecisionPackage
from decision_engine.core.models import clamp_confidence

from .evaluation_package import EvaluationPackageBuilder
from .models import EvaluatedAlternative, EvaluatedDecisionPackage, EvaluationCriteria
from .scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)


class DecisionEvaluator:
    STRATEGY = "deterministic_weighted_scoring"

    def __init__(
        self,
        scoring_engine: ScoringEngine | None = None,
        package_builder: EvaluationPackageBuilder | None = None,
    ) -> None:
        self.scoring_engine = scoring_engine or ScoringEngine()
        self.package_builder = package_builder or EvaluationPackageBuilder()

    def evaluate(self, alternative_package: AlternativeDecisionPackage) -> EvaluatedDecisionPackage:
        if not isinstance(alternative_package, AlternativeDecisionPackage):
            raise ValueError("DecisionEvaluator.evaluate requires an AlternativeDecisionPackage")
        logger.info("Evaluating decision alternatives")
        evaluated = tuple(self._evaluate_alternative(alternative) for alternative in alternative_package.alternatives)
        sorted_evaluated = tuple(sorted(evaluated, key=lambda item: item.overall_score, reverse=True))
        return self.package_builder.build(
            sorted_evaluated,
            alternative_package=alternative_package,
            criteria=self.scoring_engine.criteria,
            evaluation_strategy=self.STRATEGY,
            metadata={"source_generation_strategy": alternative_package.generation_strategy},
        )

    def _evaluate_alternative(self, alternative: AlternativeDecision) -> EvaluatedAlternative:
        scores = self.scoring_engine.score(alternative)
        overall = self.scoring_engine.overall_score(scores)
        recommendation_level = self._recommendation_level(overall)
        explanation = self._explanation(alternative, overall, recommendation_level)
        return EvaluatedAlternative(
            alternative=alternative,
            scores=scores,
            overall_score=overall,
            confidence=clamp_confidence(alternative.confidence),
            recommendation_level=recommendation_level,
            explanation=explanation,
            metadata={
                "alternative_id": alternative.alternative_id,
                "score_count": len(scores),
            },
        )

    def _recommendation_level(self, score: float) -> str:
        if score >= 0.80:
            return "strong"
        if score >= 0.60:
            return "moderate"
        if score >= 0.40:
            return "weak"
        return "not_recommended"

    def _explanation(self, alternative: AlternativeDecision, score: float, recommendation_level: str) -> str:
        return (
            f"{alternative.title} scored {score:.3f} and is classified as "
            f"{recommendation_level} based on deterministic weighted criteria."
        )
