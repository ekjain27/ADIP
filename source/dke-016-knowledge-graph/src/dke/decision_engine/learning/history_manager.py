from __future__ import annotations

from .models import DecisionFeedback, LearningPattern, LearningResult


class HistoryManager:
    def __init__(self) -> None:
        self._decision_history: list[str] = []
        self._feedback_history: list[DecisionFeedback] = []
        self._pattern_history: list[LearningPattern] = []

    def snapshot(self) -> dict:
        return {
            "decision_history": tuple(self._decision_history),
            "feedback_history": tuple(self._feedback_history),
            "pattern_history": tuple(self._pattern_history),
            "decision_count": len(self._decision_history),
            "feedback_count": len(self._feedback_history),
            "pattern_count": len(self._pattern_history),
        }

    def record(self, results: tuple[LearningResult, ...]) -> dict:
        for result in results:
            self._decision_history.append(result.alternative_id)
            self._feedback_history.append(result.feedback)
            self._pattern_history.extend(result.patterns)
        return self.snapshot()

    def clear(self) -> None:
        self._decision_history.clear()
        self._feedback_history.clear()
        self._pattern_history.clear()
