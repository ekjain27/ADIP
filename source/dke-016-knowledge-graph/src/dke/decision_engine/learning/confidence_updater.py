from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.scenario_analysis import ScenarioComparison

from .models import ConfidenceUpdate, DecisionFeedback, LearningPattern


class ConfidenceUpdater:
    def update(
        self,
        comparison: ScenarioComparison,
        feedback: DecisionFeedback,
        patterns: tuple[LearningPattern, ...],
    ) -> ConfidenceUpdate:
        old_confidence = clamp_confidence((comparison.stability_score * 0.55) + (comparison.average_score * 0.45))
        accuracy = clamp_confidence(1.0 - abs(feedback.difference))
        pattern_confidence = self._pattern_confidence(patterns)
        risk_penalty = clamp_confidence(1.0 - comparison.worst_score)
        adjustment = ((accuracy - 0.5) * 0.2) + ((feedback.confidence - 0.5) * 0.15) + ((pattern_confidence - 0.5) * 0.1) - (risk_penalty * 0.08)
        new_confidence = clamp_confidence(old_confidence + adjustment)
        return ConfidenceUpdate(
            old_confidence=old_confidence,
            new_confidence=new_confidence,
            adjustment=round(new_confidence - old_confidence, 6),
            reason=self._reason(old_confidence, new_confidence, accuracy, risk_penalty),
            metadata={
                "prediction_accuracy": accuracy,
                "feedback_confidence": feedback.confidence,
                "pattern_confidence": pattern_confidence,
                "risk_penalty": risk_penalty,
            },
        )

    def _pattern_confidence(self, patterns: tuple[LearningPattern, ...]) -> float:
        if not patterns:
            return 0.0
        return clamp_confidence(sum(pattern.confidence for pattern in patterns) / len(patterns))

    def _reason(self, old_confidence: float, new_confidence: float, accuracy: float, risk_penalty: float) -> str:
        if new_confidence > old_confidence:
            return f"Confidence increased due to prediction accuracy {accuracy:.3f}."
        if new_confidence < old_confidence:
            return f"Confidence decreased due to risk penalty {risk_penalty:.3f}."
        return "Confidence unchanged after deterministic learning update."
