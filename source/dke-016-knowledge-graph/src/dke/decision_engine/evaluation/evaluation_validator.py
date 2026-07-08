from __future__ import annotations

from decision_engine.alternatives import AlternativeDecisionPackage

from .criteria import validate_criteria_weights
from .models import EvaluatedAlternative, EvaluatedDecisionPackage, EvaluationScore


class EvaluationValidator:
    VALID_RECOMMENDATION_LEVELS = {"strong", "moderate", "weak", "not_recommended"}

    def validate(
        self,
        package: EvaluatedDecisionPackage,
        alternative_package: AlternativeDecisionPackage | None = None,
    ) -> None:
        if not isinstance(package, EvaluatedDecisionPackage):
            raise ValueError("Expected EvaluatedDecisionPackage")
        if not package.evaluated_alternatives:
            raise ValueError("EvaluatedDecisionPackage must contain evaluated alternatives")
        if package.total_evaluated != len(package.evaluated_alternatives):
            raise ValueError("total_evaluated does not match evaluated alternative count")
        validate_criteria_weights(package.criteria)
        original_ids = {item.alternative_id for item in alternative_package.alternatives} if alternative_package else set()
        for evaluated in package.evaluated_alternatives:
            self.validate_evaluated_alternative(evaluated, original_ids)

    def validate_evaluated_alternative(self, evaluated: EvaluatedAlternative, original_ids: set[str] | None = None) -> None:
        if not evaluated.alternative:
            raise ValueError("EvaluatedAlternative must link to an original alternative")
        if original_ids is not None and original_ids and evaluated.alternative.alternative_id not in original_ids:
            raise ValueError(f"Evaluated alternative {evaluated.alternative.alternative_id} is not in the source package")
        if not 0.0 <= evaluated.overall_score <= 1.0:
            raise ValueError("overall_score must be between 0 and 1")
        if not 0.0 <= evaluated.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if evaluated.recommendation_level not in self.VALID_RECOMMENDATION_LEVELS:
            raise ValueError(f"Invalid recommendation level: {evaluated.recommendation_level}")
        if not evaluated.scores:
            raise ValueError("EvaluatedAlternative must include criterion scores")
        for score in evaluated.scores:
            self.validate_score(score)

    def validate_score(self, score: EvaluationScore) -> None:
        if not score.criterion.strip():
            raise ValueError("EvaluationScore.criterion is required")
        if not 0.0 <= score.score <= 1.0:
            raise ValueError(f"score must be between 0 and 1 for {score.criterion}")
        if not 0.0 <= score.weight <= 1.0:
            raise ValueError(f"weight must be between 0 and 1 for {score.criterion}")
        expected = round(score.score * score.weight, 6)
        if abs(score.weighted_score - expected) > 0.000001:
            raise ValueError(
                f"weighted_score is incorrect for {score.criterion}: expected {expected}, got {score.weighted_score}"
            )
