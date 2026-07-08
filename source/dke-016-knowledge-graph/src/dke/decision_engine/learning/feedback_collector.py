from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.scenario_analysis import ScenarioComparison

from .models import DecisionFeedback


class FeedbackCollector:
    VALID_TYPES = {"success", "partial_success", "failure", "unknown"}

    def collect(self, comparison: ScenarioComparison) -> DecisionFeedback:
        predicted = clamp_confidence(comparison.average_score)
        actual = clamp_confidence(self._actual_score(comparison))
        difference = round(actual - predicted, 6)
        feedback_type = self._feedback_type(actual, difference)
        confidence = clamp_confidence((comparison.stability_score * 0.45) + (actual * 0.35) + (self._quality(comparison) * 0.2))
        return DecisionFeedback(
            feedback_id=f"feedback:{comparison.alternative_id}",
            alternative_id=comparison.alternative_id,
            predicted_score=predicted,
            actual_score=actual,
            difference=difference,
            feedback_type=feedback_type,
            confidence=confidence,
            metadata={
                "source": "scenario_analysis",
                "scenario_count": len(comparison.evaluations),
                "recommendation": comparison.recommendation,
                "feedback_sources": ("deterministic_scenario_proxy",),
            },
        )

    def _actual_score(self, comparison: ScenarioComparison) -> float:
        if not comparison.evaluations:
            return comparison.average_score
        weighted_total = 0.0
        probability_total = 0.0
        for evaluation in comparison.evaluations:
            probability = evaluation.scenario.probability or 0.0
            outcome_score = (evaluation.decision_score * 0.55) + (evaluation.confidence * 0.2) + (evaluation.robustness * 0.15) + (evaluation.risk_score * 0.1)
            weighted_total += outcome_score * probability
            probability_total += probability
        if probability_total <= 0.0:
            return comparison.average_score
        return weighted_total / probability_total

    def _feedback_type(self, actual: float, difference: float) -> str:
        if actual >= 0.75 and difference >= -0.05:
            return "success"
        if actual >= 0.5 and difference >= -0.2:
            return "partial_success"
        if actual < 0.5 or difference < -0.2:
            return "failure"
        return "unknown"

    def _quality(self, comparison: ScenarioComparison) -> float:
        if not comparison.evaluations:
            return 0.0
        return min(1.0, len(comparison.evaluations) / 7.0)
