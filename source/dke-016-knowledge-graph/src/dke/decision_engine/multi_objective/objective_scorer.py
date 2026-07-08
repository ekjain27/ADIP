from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.learning import LearningDecisionPackage, LearningResult

from .models import MultiObjective, ObjectiveScore
from .objective_registry import ObjectiveRegistry


class ObjectiveScorer:
    def __init__(self, registry: ObjectiveRegistry | None = None) -> None:
        self.registry = registry or ObjectiveRegistry()

    def score(
        self,
        learning_package: LearningDecisionPackage,
        objectives: tuple[MultiObjective, ...] | None = None,
    ) -> tuple[ObjectiveScore, ...]:
        active_objectives = objectives or self.registry.default_objectives()
        return tuple(self.score_result(result, active_objectives) for result in learning_package.learning_results)

    def score_result(self, result: LearningResult, objectives: tuple[MultiObjective, ...]) -> ObjectiveScore:
        scores = {objective.name: self._score_objective(result, objective.name) for objective in objectives}
        weighted = sum(scores[objective.name] * objective.weight for objective in objectives)
        return ObjectiveScore(
            alternative_id=result.alternative_id,
            scores=scores,
            weighted_score=clamp_confidence(weighted),
            source_learning_score=clamp_confidence(result.learning_score),
            metadata={
                "feedback_type": result.feedback.feedback_type,
                "pattern_count": len(result.patterns),
            },
        )

    def _score_objective(self, result: LearningResult, name: str) -> float:
        feedback = result.feedback
        update = result.confidence_update
        pattern_confidence = sum(pattern.confidence for pattern in result.patterns) / len(result.patterns) if result.patterns else 0.0
        accuracy = 1.0 - abs(feedback.difference)
        if name == "value":
            return clamp_confidence((result.learning_score * 0.45) + (feedback.actual_score * 0.35) + (update.new_confidence * 0.20))
        if name == "risk":
            failure_penalty = 0.25 if feedback.feedback_type == "failure" else 0.0
            return clamp_confidence(1.0 - (abs(feedback.difference) * 0.45) - failure_penalty - (max(0.0, -update.adjustment) * 0.30))
        if name == "confidence":
            return clamp_confidence((update.new_confidence * 0.70) + (feedback.confidence * 0.30))
        if name == "feasibility":
            return clamp_confidence((accuracy * 0.45) + (feedback.predicted_score * 0.25) + (feedback.actual_score * 0.30))
        if name == "compliance":
            text = " ".join((*result.recommendations, *(pattern.name for pattern in result.patterns))).lower()
            penalty = 0.15 if "review assumptions" in text or feedback.feedback_type == "failure" else 0.0
            return clamp_confidence(0.72 + (pattern_confidence * 0.18) - penalty)
        if name == "stability":
            return clamp_confidence((1.0 - abs(update.adjustment)) * 0.55 + accuracy * 0.30 + pattern_confidence * 0.15)
        return clamp_confidence(result.learning_score)
