from __future__ import annotations

import logging
from typing import Any

from decision_engine.core.models import clamp_confidence
from decision_engine.scenario_analysis import ScenarioAnalysisDecisionPackage, ScenarioComparison

from .confidence_updater import ConfidenceUpdater
from .feedback_collector import FeedbackCollector
from .history_manager import HistoryManager
from .learning_package import LearningPackageBuilder
from .models import LearningDecisionPackage, LearningResult
from .pattern_detector import PatternDetector

logger = logging.getLogger(__name__)


class DecisionLearningEngine:
    STRATEGY = "deterministic_decision_learning"

    def __init__(
        self,
        feedback_collector: FeedbackCollector | None = None,
        pattern_detector: PatternDetector | None = None,
        confidence_updater: ConfidenceUpdater | None = None,
        history_manager: HistoryManager | None = None,
        package_builder: LearningPackageBuilder | None = None,
    ) -> None:
        self.feedback_collector = feedback_collector or FeedbackCollector()
        self.pattern_detector = pattern_detector or PatternDetector()
        self.confidence_updater = confidence_updater or ConfidenceUpdater()
        self.history_manager = history_manager or HistoryManager()
        self.package_builder = package_builder or LearningPackageBuilder()

    def learn(self, scenario_package: ScenarioAnalysisDecisionPackage) -> LearningDecisionPackage:
        if not isinstance(scenario_package, ScenarioAnalysisDecisionPackage):
            raise ValueError("DecisionLearningEngine.learn requires a ScenarioAnalysisDecisionPackage")
        logger.info("Running deterministic decision learning")
        previous_history = self.history_manager.snapshot()
        results = tuple(self._learn_comparison(comparison, previous_history) for comparison in scenario_package.scenario_comparisons)
        selected = self._selected_learning(results, scenario_package.selected_comparison)
        history = self.history_manager.record(results)
        return self.package_builder.build(
            results,
            selected,
            history,
            learning_strategy=self.STRATEGY,
            metadata={
                "source_scenario_strategy": scenario_package.scenario_strategy,
                "scenario_comparison_count": len(scenario_package.scenario_comparisons),
            },
        )

    def _learn_comparison(self, comparison: ScenarioComparison, history: dict) -> LearningResult:
        feedback = self.feedback_collector.collect(comparison)
        patterns = self.pattern_detector.detect(comparison, feedback, history)
        confidence_update = self.confidence_updater.update(comparison, feedback, patterns)
        learning_score = self._learning_score(feedback, confidence_update, patterns)
        return LearningResult(
            alternative_id=comparison.alternative_id,
            feedback=feedback,
            patterns=patterns,
            confidence_update=confidence_update,
            learning_score=learning_score,
            recommendations=self._recommendations(feedback, confidence_update, patterns),
            metadata={"scenario_recommendation": comparison.recommendation},
        )

    def _selected_learning(
        self,
        results: tuple[LearningResult, ...],
        selected_comparison: ScenarioComparison | None,
    ) -> LearningResult | None:
        if not results:
            return None
        if selected_comparison is not None:
            for result in results:
                if result.alternative_id == selected_comparison.alternative_id:
                    return result
        return max(results, key=lambda item: (item.learning_score, item.confidence_update.new_confidence))

    def _learning_score(
        self,
        feedback: Any,
        confidence_update: Any,
        patterns: tuple[Any, ...],
    ) -> float:
        pattern_confidence = sum(pattern.confidence for pattern in patterns) / len(patterns) if patterns else 0.0
        accuracy = 1.0 - abs(feedback.difference)
        score = (accuracy * 0.35) + (feedback.confidence * 0.25) + (confidence_update.new_confidence * 0.25) + (pattern_confidence * 0.15)
        return clamp_confidence(score)

    def _recommendations(self, feedback: Any, confidence_update: Any, patterns: tuple[Any, ...]) -> tuple[str, ...]:
        recommendations: list[str] = []
        pattern_names = {pattern.name for pattern in patterns}
        if feedback.feedback_type == "failure":
            recommendations.append("Review assumptions before reusing this decision pattern.")
        if "High uncertainty" in pattern_names:
            recommendations.append("Collect additional evidence for unstable scenarios.")
        if confidence_update.new_confidence > confidence_update.old_confidence:
            recommendations.append("Increase confidence weighting for similar future decisions.")
        if not recommendations:
            recommendations.append("Continue monitoring outcomes and feedback quality.")
        return tuple(recommendations)
