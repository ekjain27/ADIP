from __future__ import annotations

from .models import ConfidenceUpdate, DecisionFeedback, LearningDecisionPackage, LearningPattern, LearningResult


class LearningValidator:
    VALID_FEEDBACK_TYPES = {"success", "partial_success", "failure", "unknown"}

    def validate_feedback(self, feedback: DecisionFeedback) -> None:
        if not feedback.feedback_id.strip():
            raise ValueError("DecisionFeedback.feedback_id is required")
        if not feedback.alternative_id.strip():
            raise ValueError("DecisionFeedback.alternative_id is required")
        for field_name in ("predicted_score", "actual_score", "confidence"):
            self._validate_unit(getattr(feedback, field_name), field_name)
        if not -1.0 <= feedback.difference <= 1.0:
            raise ValueError("feedback difference must be between -1 and 1")
        if feedback.feedback_type not in self.VALID_FEEDBACK_TYPES:
            raise ValueError(f"Invalid feedback_type: {feedback.feedback_type}")

    def validate_pattern(self, pattern: LearningPattern) -> None:
        if not pattern.pattern_id.strip():
            raise ValueError("LearningPattern.pattern_id is required")
        if pattern.frequency < 1:
            raise ValueError("pattern frequency must be at least 1")
        self._validate_unit(pattern.confidence, "pattern confidence")

    def validate_confidence_update(self, update: ConfidenceUpdate) -> None:
        self._validate_unit(update.old_confidence, "old_confidence")
        self._validate_unit(update.new_confidence, "new_confidence")
        if not -1.0 <= update.adjustment <= 1.0:
            raise ValueError("confidence adjustment must be between -1 and 1")

    def validate_result(self, result: LearningResult) -> None:
        if not result.alternative_id.strip():
            raise ValueError("LearningResult.alternative_id is required")
        self.validate_feedback(result.feedback)
        for pattern in result.patterns:
            self.validate_pattern(pattern)
        self.validate_confidence_update(result.confidence_update)
        self._validate_unit(result.learning_score, "learning score")

    def validate_package(self, package: LearningDecisionPackage) -> None:
        if not isinstance(package, LearningDecisionPackage):
            raise ValueError("Expected LearningDecisionPackage")
        if package.learning_results and package.selected_learning is None:
            raise ValueError("selected learning is required when learning results exist")
        if not package.learning_results and package.selected_learning is not None:
            raise ValueError("selected learning must be None when no learning results exist")
        if package.selected_learning is not None and package.selected_learning not in package.learning_results:
            raise ValueError("selected learning must be present in learning results")
        for result in package.learning_results:
            self.validate_result(result)
        self._validate_history(package)

    def _validate_history(self, package: LearningDecisionPackage) -> None:
        history = package.history
        feedback_count = int(history.get("feedback_count", len(history.get("feedback_history", ()))))
        if feedback_count < len(package.learning_results):
            raise ValueError("history consistency error: feedback history is missing learning results")

    def _validate_unit(self, value: float, field_name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field_name} must be between 0 and 1")
