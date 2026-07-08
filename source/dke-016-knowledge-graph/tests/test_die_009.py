import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.optimization import OptimizationEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import (
    DecisionScenarioEngine,
    ScenarioComparator,
    ScenarioDefinition,
    ScenarioEvaluator,
    ScenarioGenerator,
    ScenarioLibrary,
    ScenarioPackageBuilder,
    ScenarioValidator,
)
from decision_engine.scenario_analysis.models import ScenarioComparison
from decision_engine.simulation import DecisionSimulator
from decision_engine.uncertainty import RobustnessResult, UncertaintyEngine, UncertaintyResult


def test_scenario_library_loads_default_scenarios():
    scenarios = ScenarioLibrary().default_scenarios()
    assert len(scenarios) == 7
    assert {scenario.name for scenario in scenarios} >= {"Optimistic", "Expected", "Technical Failure"}


def test_generator_creates_all_scenarios():
    scenarios = ScenarioGenerator().generate()
    assert len(scenarios) == 7


def test_scenario_probabilities_normalize():
    scenarios = ScenarioGenerator().generate()
    assert abs(sum(scenario.probability for scenario in scenarios) - 1.0) <= 0.00001


def test_scenario_evaluator_works():
    evaluation = ScenarioEvaluator().evaluate(_uncertainty_result(), ScenarioGenerator().generate()[0])
    assert 0.0 <= evaluation.decision_score <= 1.0


def test_comparator_calculates_stability():
    result = _uncertainty_result()
    evaluations = tuple(ScenarioEvaluator().evaluate(result, scenario) for scenario in ScenarioGenerator().generate())
    comparison = ScenarioComparator().compare(result.alternative_id, evaluations)
    assert 0.0 <= comparison.stability_score <= 1.0


def test_comparator_recommendation_valid():
    result = _uncertainty_result()
    evaluations = tuple(ScenarioEvaluator().evaluate(result, scenario) for scenario in ScenarioGenerator().generate())
    comparison = ScenarioComparator().compare(result.alternative_id, evaluations)
    assert comparison.recommendation in ScenarioComparator.VALID_RECOMMENDATIONS


def test_validator_catches_invalid_probability():
    scenario = ScenarioDefinition("bad", "Bad", "Bad", "test", probability=1.2)
    with pytest.raises(ValueError, match="Scenario probability must be between 0 and 1"):
        ScenarioValidator().validate_scenario(scenario)


def test_validator_catches_invalid_stability_score():
    comparison = ScenarioComparison("alt-1", (), 0.5, 0.6, 0.4, 1.2, "weak")
    with pytest.raises(ValueError, match="stability_score must be between 0 and 1"):
        ScenarioValidator().validate_comparison(comparison)


def test_package_builder_works():
    result = _uncertainty_result()
    evaluations = tuple(ScenarioEvaluator().evaluate(result, scenario) for scenario in ScenarioGenerator().generate())
    comparison = ScenarioComparator().compare(result.alternative_id, evaluations)
    package = ScenarioPackageBuilder().build((comparison,), comparison)
    assert package.selected_comparison == comparison
    assert package.metadata["module"] == "DIE-009"


def test_integration_die_001_to_die_002_to_die_003_to_die_004_to_die_005_to_die_006_to_die_007_to_die_008_to_die_009():
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
    scenario_package = DecisionScenarioEngine().analyze(uncertainty_package)
    assert scenario_package.selected_comparison is not None
    assert scenario_package.scenario_comparisons


def _uncertainty_result() -> UncertaintyResult:
    return UncertaintyResult(
        alternative_id="alt-1",
        uncertainty_score=0.25,
        reliability_score=0.78,
        confidence_interval=(0.65, 0.85),
        robustness=RobustnessResult(0.8, True, 0.75),
        explanation="Reliable under current assumptions.",
    )
