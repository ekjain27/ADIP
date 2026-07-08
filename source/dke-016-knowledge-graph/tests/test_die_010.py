import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.learning import (
    ConfidenceUpdater,
    DecisionFeedback,
    DecisionLearningEngine,
    FeedbackCollector,
    LearningPackageBuilder,
    LearningResult,
    LearningValidator,
    PatternDetector,
)
from decision_engine.optimization import OptimizationEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine, ScenarioAnalysisDecisionPackage
from decision_engine.simulation import DecisionSimulator
from decision_engine.uncertainty import UncertaintyEngine


def test_feedback_collector_works():
    comparison = _scenario_package().selected_comparison
    feedback = FeedbackCollector().collect(comparison)
    assert feedback.alternative_id == comparison.alternative_id
    assert feedback.feedback_type in FeedbackCollector.VALID_TYPES
    assert -1.0 <= feedback.difference <= 1.0


def test_pattern_detector_identifies_patterns():
    comparison = _scenario_package().selected_comparison
    feedback = FeedbackCollector().collect(comparison)
    patterns = PatternDetector().detect(comparison, feedback)
    assert patterns
    assert any(pattern.name in {"Strong confidence", "Consistent optimization", "Repeated success", "Limited signal"} for pattern in patterns)


def test_confidence_updater_normalizes_values():
    comparison = _scenario_package().selected_comparison
    feedback = FeedbackCollector().collect(comparison)
    patterns = PatternDetector().detect(comparison, feedback)
    update = ConfidenceUpdater().update(comparison, feedback, patterns)
    assert 0.0 <= update.old_confidence <= 1.0
    assert 0.0 <= update.new_confidence <= 1.0


def test_history_manager_stores_history():
    package = DecisionLearningEngine().learn(_scenario_package())
    assert package.history["decision_count"] == len(package.learning_results)
    assert package.history["feedback_count"] == len(package.learning_results)
    assert package.history["pattern_count"] >= len(package.learning_results)


def test_learning_engine_handles_empty_package():
    empty = ScenarioAnalysisDecisionPackage((), None, "test", "empty")
    package = DecisionLearningEngine().learn(empty)
    assert package.learning_results == ()
    assert package.selected_learning is None


def test_learning_score_normalized():
    package = DecisionLearningEngine().learn(_scenario_package())
    assert all(0.0 <= result.learning_score <= 1.0 for result in package.learning_results)


def test_validator_catches_invalid_confidence():
    feedback = DecisionFeedback("f1", "alt-1", 0.5, 0.5, 0.0, "success", 1.2)
    with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
        LearningValidator().validate_feedback(feedback)


def test_validator_catches_invalid_learning_score():
    feedback = DecisionFeedback("f1", "alt-1", 0.5, 0.5, 0.0, "success", 0.8)
    update = ConfidenceUpdater().update(_scenario_package().selected_comparison, feedback, ())
    result = LearningResult("alt-1", feedback, (), update, 1.2)
    with pytest.raises(ValueError, match="learning score must be between 0 and 1"):
        LearningValidator().validate_result(result)


def test_package_builder_works():
    comparison = _scenario_package().selected_comparison
    feedback = FeedbackCollector().collect(comparison)
    patterns = PatternDetector().detect(comparison, feedback)
    update = ConfidenceUpdater().update(comparison, feedback, patterns)
    result = LearningResult(comparison.alternative_id, feedback, patterns, update, 0.8)
    package = LearningPackageBuilder().build((result,), result, {"feedback_count": 1})
    assert package.selected_learning == result
    assert package.metadata["module"] == "DIE-010"


def test_integration_die_001_to_die_010():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    assert learning_package.selected_learning is not None
    assert learning_package.learning_results


def _scenario_package() -> ScenarioAnalysisDecisionPackage:
    decision_package = DIECore().process(
        {
            "query": "Select a reliable technical vendor with low risk and policy alignment",
            "semantic_results": [{"id": "e1", "text": "Vendor A has strong reliability.", "confidence": 0.9}],
            "metadata": {"constraints": [{"type": "policy", "severity": "medium"}]},
        }
    )
    alternative_package = AlternativeGenerator().generate(decision_package.decision_state)
    evaluated_package = DecisionEvaluator().evaluate(alternative_package)
    ranked_package = DecisionRanker().rank(evaluated_package)
    simulation_package = DecisionSimulator().simulate(ranked_package)
    explanation_package = ExplanationGenerator().explain(simulation_package)
    optimized_package = OptimizationEngine().optimize(explanation_package)
    uncertainty_package = UncertaintyEngine().analyze(optimized_package)
    return DecisionScenarioEngine().analyze(uncertainty_package)
