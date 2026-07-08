import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.optimization import OptimizationEngine, OptimizationResult, OptimizedDecisionPackage
from decision_engine.ranking import DecisionRanker
from decision_engine.simulation import DecisionSimulator
from decision_engine.uncertainty import (
    AssumptionAnalyzer,
    RobustnessAnalyzer,
    RobustnessResult,
    SensitivityAnalyzer,
    UncertaintyEngine,
    UncertaintyEstimator,
    UncertaintyPackageBuilder,
    UncertaintyResult,
    UncertaintyValidator,
)


def test_estimator_returns_normalized_uncertainty():
    uncertainty = UncertaintyEstimator().estimate(_optimization_result())
    assert 0.0 <= uncertainty <= 1.0


def test_reliability_score_normalized():
    result = _optimization_result()
    estimator = UncertaintyEstimator()
    reliability = estimator.reliability(result, estimator.estimate(result))
    assert 0.0 <= reliability <= 1.0


def test_sensitivity_analyzer_works():
    sensitivity = SensitivityAnalyzer().analyze(_optimization_result())
    assert sensitivity
    assert all(0.0 <= item.sensitivity_score <= 1.0 for item in sensitivity)


def test_robustness_analyzer_works():
    result = _optimization_result()
    robustness = RobustnessAnalyzer().analyze(result, SensitivityAnalyzer().analyze(result))
    assert 0.0 <= robustness.robustness_score <= 1.0


def test_assumption_analyzer_extracts_assumptions():
    assumptions = AssumptionAnalyzer().analyze(_optimization_result())
    assert assumptions
    assert assumptions[0].description


def test_engine_handles_empty_package():
    package = UncertaintyEngine().analyze(OptimizedDecisionPackage((), None, "test", "empty"))
    assert package.uncertainty_results == ()
    assert package.selected_result is None


def test_validator_catches_invalid_uncertainty():
    result = UncertaintyResult(
        alternative_id="alt-1",
        uncertainty_score=1.2,
        reliability_score=0.5,
        confidence_interval=(0.3, 0.7),
        robustness=RobustnessResult(0.5, True, 0.5),
    )
    with pytest.raises(ValueError, match="uncertainty_score must be between 0 and 1"):
        UncertaintyValidator().validate_result(result)


def test_validator_catches_invalid_robustness():
    with pytest.raises(ValueError, match="robustness_score must be between 0 and 1"):
        UncertaintyValidator().validate_robustness(RobustnessResult(1.2, True, 0.5))


def test_package_builder_works():
    result = UncertaintyEngine()._analyze_result(_optimization_result())
    package = UncertaintyPackageBuilder().build((result,), result)
    assert package.selected_result == result
    assert package.metadata["module"] == "DIE-008"


def test_integration_die_001_to_die_002_to_die_003_to_die_004_to_die_005_to_die_006_to_die_007_to_die_008():
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
    uncertainty_package = UncertaintyEngine().analyze(optimized_package)
    assert uncertainty_package.selected_result is not None
    assert 0.0 <= uncertainty_package.selected_result.reliability_score <= 1.0


def _optimization_result() -> OptimizationResult:
    return OptimizationResult(
        alternative_id="alt-1",
        original_score=0.7,
        optimized_score=0.78,
        improvements=("Increase objective satisfaction.", "Resolve risk assumptions."),
        tradeoffs=("Lower risk may reduce upside.", "Higher confidence may require validation time."),
        objective_results={"value": 0.8, "risk": 0.76, "confidence": 0.82},
        confidence=0.74,
        metadata={"optimization_gain": 0.08, "constraint_satisfaction_score": 0.72, "constraint_violations": ()},
    )
