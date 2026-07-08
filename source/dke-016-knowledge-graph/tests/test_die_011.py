import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.learning import (
    ConfidenceUpdate,
    DecisionFeedback,
    DecisionLearningEngine,
    LearningDecisionPackage,
    LearningPackageBuilder,
    LearningResult,
)
from decision_engine.multi_objective import (
    BalanceOptimizer,
    BalancedResult,
    MultiObjective,
    MultiObjectiveEngine,
    MultiObjectivePackageBuilder,
    MultiObjectiveValidator,
    ObjectiveRegistry,
    ObjectiveScore,
    ObjectiveScorer,
    ParetoAnalyzer,
    TradeoffMatrixBuilder,
)
from decision_engine.optimization import OptimizationEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.uncertainty import UncertaintyEngine


def test_objective_weights_normalize():
    weights = ObjectiveRegistry().normalize_weights({"value": 2.0, "risk": 1.0, "confidence": 1.0})
    assert sum(weights.values()) == pytest.approx(1.0)
    assert weights["value"] == pytest.approx(0.5)


def test_scoring_returns_scores_0_to_1():
    package = _learning_package()
    objectives = ObjectiveRegistry().default_objectives()
    scores = ObjectiveScorer().score(package, objectives)
    assert scores
    assert all(0.0 <= value <= 1.0 for score in scores for value in score.scores.values())
    assert all(0.0 <= score.weighted_score <= 1.0 for score in scores)


def test_pareto_analyzer_works():
    strong = ObjectiveScore("alt-strong", {"value": 0.9, "risk": 0.9}, 0.9, 0.9)
    weak = ObjectiveScore("alt-weak", {"value": 0.5, "risk": 0.5}, 0.5, 0.5)
    results = ParetoAnalyzer().analyze((strong, weak))
    by_id = {result.alternative_id: result for result in results}
    assert by_id["alt-strong"].is_pareto_optimal
    assert by_id["alt-weak"].dominated_by == ("alt-strong",)


def test_balance_score_0_to_1():
    package = MultiObjectiveEngine().optimize(_learning_package())
    assert all(0.0 <= result.balance_score <= 1.0 for result in package.balanced_results)


def test_tradeoff_matrix_created():
    scores = ObjectiveScorer().score(_learning_package())
    matrix = TradeoffMatrixBuilder().build(scores)
    assert matrix.alternatives
    assert matrix.objectives
    assert set(matrix.matrix) == set(matrix.alternatives)


def test_empty_package_safe():
    empty = LearningDecisionPackage((), None, {}, "empty", "test")
    package = MultiObjectiveEngine().optimize(empty)
    assert package.objective_scores == ()
    assert package.selected_result is None
    assert package.tradeoff_matrix.alternatives == ()


def test_validator_catches_invalid_weights():
    bad_objectives = (MultiObjective("mo-value", "value", 0.8), MultiObjective("mo-risk", "risk", 0.8))
    with pytest.raises(ValueError, match="weights must sum to 1.0"):
        MultiObjectiveValidator().validate_objectives(bad_objectives)


def test_validator_catches_invalid_balance_score():
    score = ObjectiveScore("alt-1", {"value": 0.8}, 0.8, 0.8)
    pareto = ParetoAnalyzer().analyze((score,))[0]
    bad = BalancedResult("alt-1", score, pareto, 1.2, 0.7, "bad")
    with pytest.raises(ValueError, match="balance score must be between 0 and 1"):
        MultiObjectiveValidator().validate_balanced_result(bad)


def test_package_builder_works():
    scores = ObjectiveScorer().score(_learning_package())
    pareto = ParetoAnalyzer().analyze(scores)
    matrix = TradeoffMatrixBuilder().build(scores)
    balanced = BalanceOptimizer().optimize(scores, pareto, matrix)
    selected = BalanceOptimizer().select(balanced)
    package = MultiObjectivePackageBuilder().build(ObjectiveRegistry().default_objectives(), scores, pareto, matrix, balanced, selected)
    assert package.selected_result == selected
    assert package.metadata["module"] == "DIE-011"


def test_full_integration_die_001_to_die_011():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    package = MultiObjectiveEngine().optimize(learning_package)
    assert package.selected_result is not None
    assert package.objective_scores
    assert package.metadata["source_learning_strategy"] == learning_package.learning_strategy


def _learning_package():
    feedback_a = DecisionFeedback("f-alt-a", "alt-a", 0.74, 0.81, 0.07, "success", 0.86)
    update_a = ConfidenceUpdate(0.74, 0.82, 0.08, "positive feedback")
    result_a = LearningResult("alt-a", feedback_a, (), update_a, 0.82, ("Continue monitoring outcomes.",))
    feedback_b = DecisionFeedback("f-alt-b", "alt-b", 0.68, 0.58, -0.10, "partial_success", 0.72)
    update_b = ConfidenceUpdate(0.68, 0.65, -0.03, "mixed feedback")
    result_b = LearningResult("alt-b", feedback_b, (), update_b, 0.64, ("Collect additional evidence.",))
    return LearningPackageBuilder().build((result_a, result_b), result_a, {"feedback_count": 2})


def _scenario_package():
    decision_package = DIECore().process(
        {
            "query": "Select a reliable technical vendor with low risk and policy alignment",
            "semantic_results": [
                {"id": "e1", "text": "Vendor A has strong reliability and measurable value.", "confidence": 0.9},
                {"id": "e2", "text": "Vendor B has compliance concerns and uncertain delivery.", "confidence": 0.65},
            ],
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
