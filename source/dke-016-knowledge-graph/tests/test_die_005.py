import pytest

from decision_engine.alternatives import AlternativeDecision, AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator, EvaluationScore, EvaluatedAlternative
from decision_engine.ranking import DecisionRanker, RankedAlternative, RankedDecisionPackage
from decision_engine.simulation import (
    DecisionSimulator,
    ImpactAnalyzer,
    OutcomeSimulator,
    Scenario,
    ScenarioGenerator,
    SimulatedOutcome,
    SimulationDecisionPackage,
    SimulationValidator,
)


def test_scenario_generator_creates_best_expected_and_worst_scenarios():
    scenarios = ScenarioGenerator().generate(_ranked())
    assert {scenario.scenario_type for scenario in scenarios} == {"best_case", "expected_case", "worst_case"}


def test_scenario_probabilities_are_normalized():
    scenarios = ScenarioGenerator().generate(_ranked())
    assert abs(sum(scenario.probability for scenario in scenarios) - 1.0) <= 0.00001


def test_outcome_simulator_creates_one_simulated_outcome():
    outcome = OutcomeSimulator().simulate(_ranked())
    assert outcome.alternative_id == "alt-1"
    assert len(outcome.scenarios) == 3


def test_outcome_score_is_between_zero_and_one():
    outcome = OutcomeSimulator().simulate(_ranked())
    assert 0.0 <= outcome.outcome_score <= 1.0


def test_impact_analyzer_returns_normalized_risk_impact():
    score = ImpactAnalyzer().risk_impact(_ranked())
    assert 0.0 <= score <= 1.0


def test_impact_analyzer_returns_normalized_confidence_impact():
    ranked = _ranked()
    scenarios = ScenarioGenerator().generate(ranked)
    score = ImpactAnalyzer().confidence_impact(ranked, scenarios)
    assert 0.0 <= score <= 1.0


def test_decision_simulator_simulates_ranked_package_end_to_end():
    package = DecisionSimulator().simulate(_ranked_package())
    assert package.total_simulated == 2
    assert package.simulation_strategy == "deterministic_scenario_simulation"


def test_selected_outcome_exists_when_outcomes_exist():
    package = DecisionSimulator().simulate(_ranked_package())
    assert package.selected_outcome is not None
    assert package.selected_outcome.alternative_id == "alt-1"


def test_validator_catches_invalid_probability():
    ranked = _ranked()
    bad_scenario = Scenario(
        scenario_id="s1",
        scenario_type="best_case",
        title="Bad",
        description="Bad",
        probability=1.2,
        impact_score=0.5,
        confidence=0.5,
    )
    expected = Scenario("s2", "expected_case", "Expected", "Expected", probability=0.0, impact_score=0.5, confidence=0.5)
    worst = Scenario("s3", "worst_case", "Worst", "Worst", probability=0.0, impact_score=0.5, confidence=0.5)
    outcome = SimulatedOutcome(
        alternative_id="alt-1",
        ranked_alternative=ranked,
        scenarios=(bad_scenario, expected, worst),
        expected_outcome=expected,
        best_case=bad_scenario,
        worst_case=worst,
        risk_impact=0.5,
        confidence_impact=0.5,
        outcome_score=0.5,
        explanation="bad",
    )
    package = SimulationDecisionPackage((outcome,), outcome, 1, "test")
    with pytest.raises(ValueError, match="Scenario probability must be between 0 and 1"):
        SimulationValidator().validate(package)


def test_integration_die_001_to_die_002_to_die_003_to_die_004_to_die_005():
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
    assert simulation_package.total_simulated == ranked_package.total_ranked
    assert simulation_package.selected_outcome is not None


def _ranked() -> RankedAlternative:
    alternative = AlternativeDecision(
        alternative_id="alt-1",
        title="Alternative 1",
        description="A strong alternative",
        supporting_evidence=("e1", "e2"),
        supporting_goals=("goal",),
        supporting_constraints=("budget",),
        assumptions=("Demand remains stable.",),
        confidence=0.8,
        feasibility=0.8,
        risks=("minor risk",),
        advantages=("traceable", "fast"),
        disadvantages=("limited upside",),
    )
    evaluated = EvaluatedAlternative(
        alternative=alternative,
        scores=(EvaluationScore("confidence", 0.8, 0.15, 0.12, "confidence"),),
        overall_score=0.82,
        confidence=0.8,
        recommendation_level="strong",
        explanation="evaluated",
    )
    return RankedAlternative(
        rank=1,
        evaluated_alternative=evaluated,
        alternative_id="alt-1",
        overall_score=0.82,
        ranking_score=0.84,
        selection_status="selected",
        tie_breaker_score=0.8,
        explanation="ranked",
    )


def _ranked_package() -> RankedDecisionPackage:
    first = _ranked()
    second_alt = AlternativeDecision("alt-2", "Alternative 2", "A weaker option", confidence=0.5, risks=("deadline risk",))
    second_eval = EvaluatedAlternative(
        alternative=second_alt,
        scores=(EvaluationScore("confidence", 0.5, 0.15, 0.075, "confidence"),),
        overall_score=0.45,
        confidence=0.5,
        recommendation_level="weak",
        explanation="evaluated",
    )
    second = RankedAlternative(2, second_eval, "alt-2", 0.45, 0.46, "shortlisted", 0.4, "ranked")
    return RankedDecisionPackage(
        ranked_alternatives=(first, second),
        selected_alternative=first,
        top_alternatives=(first, second),
        total_ranked=2,
        ranking_strategy="test",
        selection_strategy="test",
    )
