from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.scenario_analysis import ScenarioComparison

from .models import DecisionFeedback, LearningPattern


class PatternDetector:
    def detect(self, comparison: ScenarioComparison, feedback: DecisionFeedback, history: dict | None = None) -> tuple[LearningPattern, ...]:
        history = history or {}
        patterns: list[LearningPattern] = []
        history_frequency = self._history_frequency(feedback.alternative_id, feedback.feedback_type, history)
        if feedback.feedback_type == "success":
            patterns.append(self._pattern("repeated-success", "Repeated success", "Alternative is matching or exceeding predicted outcomes.", max(1, history_frequency), feedback.confidence, ("feedback", "outcome")))
        if feedback.feedback_type == "failure":
            patterns.append(self._pattern("repeated-failure", "Repeated failure", "Alternative is underperforming predicted outcomes.", max(1, history_frequency), 1.0 - feedback.actual_score, ("feedback", "risk")))
        if comparison.stability_score < 0.5 or abs(feedback.difference) > 0.2:
            patterns.append(self._pattern("high-uncertainty", "High uncertainty", "Scenario outcomes vary enough to reduce forecast reliability.", 1, 1.0 - comparison.stability_score, ("scenario", "confidence")))
        if comparison.recommendation in {"strong", "moderate"} and comparison.stability_score >= 0.6:
            patterns.append(self._pattern("consistent-optimization", "Consistent optimization", "Scenario analysis indicates consistently optimized outcomes.", 1, comparison.stability_score, ("scenario", "optimization")))
        if comparison.worst_score < 0.45:
            patterns.append(self._pattern("high-risk", "High risk", "Worst-case scenario remains below acceptable decision quality.", 1, 1.0 - comparison.worst_score, ("scenario", "risk")))
        if feedback.confidence >= 0.75 and comparison.stability_score >= 0.65:
            patterns.append(self._pattern("strong-confidence", "Strong confidence", "Feedback quality and scenario stability support confidence.", 1, feedback.confidence, ("feedback", "confidence")))
        if not patterns:
            patterns.append(self._pattern("limited-signal", "Limited signal", "Available feedback has limited learning signal.", 1, feedback.confidence, ("feedback",)))
        return tuple(patterns)

    def _pattern(
        self,
        suffix: str,
        name: str,
        description: str,
        frequency: int,
        confidence: float,
        affected_components: tuple[str, ...],
    ) -> LearningPattern:
        return LearningPattern(
            pattern_id=f"pattern:{suffix}",
            name=name,
            description=description,
            frequency=frequency,
            confidence=clamp_confidence(confidence),
            affected_components=affected_components,
            metadata={"detector": "deterministic_rules"},
        )

    def _history_frequency(self, alternative_id: str, feedback_type: str, history: dict) -> int:
        feedback_history = history.get("feedback_history", ())
        return sum(
            1
            for item in feedback_history
            if getattr(item, "alternative_id", None) == alternative_id and getattr(item, "feedback_type", None) == feedback_type
        )
