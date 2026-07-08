import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.explanation.models import DecisionExplanation, ExplanationDecisionPackage, ExplanationSection
from decision_engine.optimization import (
    ConstraintOptimizer,
    ObjectiveOptimizer,
    OptimizationEngine,
    OptimizationPackageBuilder,
    OptimizationResult,
    OptimizationValidator,
    TradeoffAnalyzer,
)
from decision_engine.ranking import DecisionRanker
from decision_engine.simulation import DecisionSimulator


def test_objective_weights_normalize():
    optimizer = ObjectiveOptimizer()
    weights = optimizer.normalize_weights({"value": 2.0, "risk": 1.0})
    assert sum(weights.values()) == 1.0


def test_optimization_improves_score():
    package = OptimizationEngine().optimize(_explanation_package())
    assert package.selected_result.optimized_score >= package.selected_result.original_score


def test_optimized_score_between_zero_and_one():
    package = OptimizationEngine().optimize(_explanation_package())
    assert all(0.0 <= result.optimized_score <= 1.0 for result in package.optimized_results)


def test_tradeoff_analyzer_produces_summaries():
    tradeoffs = TradeoffAnalyzer().analyze(_explanation())
    assert tradeoffs
    assert all(isinstance(item, str) and item for item in tradeoffs)


def test_constraint_optimizer_works():
    result = ConstraintOptimizer().optimize(_explanation())
    assert "satisfaction_score" in result
    assert 0.0 <= result["satisfaction_score"] <= 1.0


def test_optimization_engine_handles_empty_package():
    package = OptimizationEngine().optimize(ExplanationDecisionPackage((), None, 0, "test"))
    assert package.optimized_results == ()
    assert package.selected_result is None


def test_validator_catches_invalid_weights():
    with pytest.raises(ValueError, match="weights must sum to 1.0"):
        OptimizationValidator().validate_objectives(tuple(ObjectiveOptimizer().default_objectives())[:-1])


def test_validator_catches_invalid_score():
    result = OptimizationResult(
        alternative_id="alt-1",
        original_score=0.5,
        optimized_score=1.2,
        confidence=0.5,
    )
    with pytest.raises(ValueError, match="optimized_score must be between 0 and 1"):
        OptimizationValidator().validate_result(result)


def test_package_builder_works():
    result = OptimizationResult("alt-1", 0.5, 0.6, confidence=0.55, objective_results={"value": 0.7})
    package = OptimizationPackageBuilder().build((result,), result)
    assert package.selected_result == result
    assert package.metadata["module"] == "DIE-007"


def test_integration_die_001_to_die_002_to_die_003_to_die_004_to_die_005_to_die_006_to_die_007():
    decision_package = DIECore().process(
        {
            "query": "Select a technical vendor within budget and policy limits",
            "semantic_results": [{"id": "e1", "text": "Vendor A has strong uptime.", "confidence": 0.9}],
            "metadata": {"constraints": [{"type": "policy", "severity": "high"}]},
        }
    )
    alternative_package = AlternativeGenerator().generate(decision_package.decision_state)
    evaluated_package = DecisionEvaluator().evaluate(alternative_package)
    ranked_package = DecisionRanker().rank(evaluated_package)
    simulation_package = DecisionSimulator().simulate(ranked_package)
    explanation_package = ExplanationGenerator().explain(simulation_package)
    optimized_package = OptimizationEngine().optimize(explanation_package)
    assert optimized_package.selected_result is not None
    assert optimized_package.selected_result.optimized_score >= optimized_package.selected_result.original_score


def _explanation() -> DecisionExplanation:
    section = ExplanationSection("section-1", "Recommendation", "Selected because confidence and risk are balanced.", confidence=0.7)
    return DecisionExplanation(
        alternative_id="alt-1",
        summary="Recommended decision alt-1 has simulated outcome score 0.720.",
        reasoning="It is ranked 1 with ranking score 0.800 and selected for budget policy fit.",
        evidence_explanation="The alternative is supported by 2 evidence items with strong confidence impact.",
        risk_explanation="The alternative has 1 risk item and risk impact is manageable.",
        scenario_explanation="Best case, expected case, and worst case are all described.",
        recommendation_explanation="This alternative is selected with strong recommendation and clear tradeoffs.",
        assumptions=("Demand remains stable.",),
        confidence=0.72,
        sections=(section,),
    )


def _explanation_package() -> ExplanationDecisionPackage:
    explanation = _explanation()
    return ExplanationDecisionPackage((explanation,), explanation, 1, "test")
