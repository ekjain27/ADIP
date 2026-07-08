import pytest

from decision_engine.alternatives import AlternativeDecision, AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator, EvaluationScore, EvaluatedAlternative
from decision_engine.explanation import (
    EvidenceExplainer,
    ExplanationGenerator,
    ExplanationValidator,
    RecommendationExplainer,
    RiskExplainer,
    ScenarioExplainer,
)
from decision_engine.explanation.models import DecisionExplanation, ExplanationDecisionPackage, ExplanationSection
from decision_engine.ranking import DecisionRanker, RankedAlternative, RankedDecisionPackage
from decision_engine.simulation import DecisionSimulator, OutcomeSimulator, SimulationDecisionPackage


def test_explanation_generator_handles_empty_simulation_package():
    package = ExplanationGenerator().explain(SimulationDecisionPackage((), None, 0, "test"))
    assert package.total_explained == 0
    assert package.selected_explanation is None


def test_explanation_generator_creates_explanations_for_simulated_outcomes():
    simulation_package = DecisionSimulator().simulate(_ranked_package())
    package = ExplanationGenerator().explain(simulation_package)
    assert package.total_explained == simulation_package.total_simulated
    assert package.explanations[0].summary


def test_selected_explanation_exists_when_selected_outcome_exists():
    simulation_package = DecisionSimulator().simulate(_ranked_package())
    package = ExplanationGenerator().explain(simulation_package)
    assert package.selected_explanation is not None
    assert package.selected_explanation.alternative_id == simulation_package.selected_outcome.alternative_id


def test_evidence_explainer_produces_non_empty_explanation():
    outcome = OutcomeSimulator().simulate(_ranked())
    assert EvidenceExplainer().explain(outcome)


def test_risk_explainer_produces_non_empty_explanation():
    outcome = OutcomeSimulator().simulate(_ranked())
    assert RiskExplainer().explain(outcome)


def test_scenario_explainer_explains_best_expected_and_worst_cases():
    outcome = OutcomeSimulator().simulate(_ranked())
    text = ScenarioExplainer().explain(outcome)
    assert "Best case" in text
    assert "Expected case" in text
    assert "Worst case" in text


def test_recommendation_explainer_produces_recommendation_explanation():
    outcome = OutcomeSimulator().simulate(_ranked())
    text = RecommendationExplainer().explain(outcome, selected=True)
    assert "selected" in text
    assert "ranking score" in text


def test_explanation_confidence_is_between_zero_and_one():
    simulation_package = DecisionSimulator().simulate(_ranked_package())
    package = ExplanationGenerator().explain(simulation_package)
    assert all(0.0 <= explanation.confidence <= 1.0 for explanation in package.explanations)


def test_validator_catches_invalid_confidence():
    section = ExplanationSection("s1", "Section", "Content", confidence=0.5)
    explanation = DecisionExplanation(
        alternative_id="alt-1",
        summary="Summary",
        reasoning="Reasoning",
        evidence_explanation="Evidence",
        risk_explanation="Risk",
        scenario_explanation="Scenario",
        recommendation_explanation="Recommendation",
        confidence=1.2,
        sections=(section,),
    )
    package = ExplanationDecisionPackage((explanation,), explanation, 1, "test")
    with pytest.raises(ValueError, match="Explanation confidence must be between 0 and 1"):
        ExplanationValidator().validate(package)


def test_integration_die_001_to_die_002_to_die_003_to_die_004_to_die_005_to_die_006():
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
    assert explanation_package.total_explained == simulation_package.total_simulated
    assert explanation_package.selected_explanation is not None


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
    return RankedAlternative(1, evaluated, "alt-1", 0.82, 0.84, "selected", 0.8, "ranked")


def _ranked_package() -> RankedDecisionPackage:
    first = _ranked()
    return RankedDecisionPackage(
        ranked_alternatives=(first,),
        selected_alternative=first,
        top_alternatives=(first,),
        total_ranked=1,
        ranking_strategy="test",
        selection_strategy="test",
    )
