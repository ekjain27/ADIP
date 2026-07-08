import pytest

from decision_engine.alternatives import AlternativeDecision, AlternativeDecisionPackage, AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import (
    DecisionEvaluator,
    EvaluationCriteria,
    EvaluationScore,
    EvaluationValidator,
    ScoringEngine,
    default_criteria,
    validate_criteria_weights,
)
from decision_engine.evaluation.models import EvaluatedAlternative, EvaluatedDecisionPackage


def test_default_criteria_weights_sum_to_one():
    criteria = default_criteria()
    assert sum(item.weight for item in criteria) == 1.0


def test_scoring_engine_scores_one_alternative():
    scores = ScoringEngine().score(_alternative())
    assert {score.criterion for score in scores} == {criterion.name for criterion in default_criteria()}


def test_all_scores_are_between_zero_and_one():
    scores = ScoringEngine().score(_alternative())
    assert all(0.0 <= score.score <= 1.0 for score in scores)
    assert all(0.0 <= score.weighted_score <= 1.0 for score in scores)


def test_weighted_score_calculation_is_correct():
    score = ScoringEngine().score(_alternative())[0]
    assert score.weighted_score == round(score.score * score.weight, 6)


def test_evaluator_evaluates_package_end_to_end():
    package = DecisionEvaluator().evaluate(_alternative_package())
    assert package.total_evaluated == 2
    assert package.evaluation_strategy == "deterministic_weighted_scoring"


def test_evaluated_alternatives_are_sorted_by_score_descending():
    package = DecisionEvaluator().evaluate(_alternative_package())
    scores = [item.overall_score for item in package.evaluated_alternatives]
    assert scores == sorted(scores, reverse=True)


def test_recommendation_levels_are_assigned_correctly():
    evaluator = DecisionEvaluator()
    assert evaluator._recommendation_level(0.8) == "strong"
    assert evaluator._recommendation_level(0.6) == "moderate"
    assert evaluator._recommendation_level(0.4) == "weak"
    assert evaluator._recommendation_level(0.39) == "not_recommended"


def test_validator_catches_invalid_score():
    evaluated = EvaluatedAlternative(
        alternative=_alternative(),
        scores=(EvaluationScore("confidence", 1.2, 0.15, 0.18, "bad"),),
        overall_score=0.5,
        confidence=0.5,
        recommendation_level="weak",
        explanation="bad",
    )
    package = EvaluatedDecisionPackage(
        evaluated_alternatives=(evaluated,),
        total_evaluated=1,
        evaluation_strategy="test",
        criteria=default_criteria(),
    )
    with pytest.raises(ValueError, match="score must be between 0 and 1"):
        EvaluationValidator().validate(package)


def test_validator_catches_invalid_criteria_weights():
    criteria = (EvaluationCriteria("confidence", 0.5),)
    with pytest.raises(ValueError, match="weights must sum to 1.0"):
        validate_criteria_weights(criteria)


def test_integration_die_001_to_die_002_to_die_003():
    decision_package = DIECore().process(
        {
            "query": "Select a technical vendor within budget and policy limits",
            "semantic_results": [{"id": "e1", "text": "Vendor A has strong uptime.", "confidence": 0.9}],
            "metadata": {"constraints": [{"type": "policy", "severity": "high"}]},
        }
    )
    alternative_package = AlternativeGenerator().generate(decision_package.decision_state)
    evaluated_package = DecisionEvaluator().evaluate(alternative_package)
    assert evaluated_package.total_evaluated == alternative_package.total_generated
    assert evaluated_package.evaluated_alternatives[0].alternative.alternative_id


def _alternative() -> AlternativeDecision:
    return AlternativeDecision(
        alternative_id="alt-1",
        title="Evidence-led decision",
        description="Prioritize the highest evidence path.",
        supporting_evidence=("e1", "e2"),
        supporting_goals=("Choose vendor", "Reduce risk"),
        supporting_constraints=("budget",),
        confidence=0.8,
        feasibility=0.75,
        risks=("May miss weak strategic signals.",),
        advantages=("Traceable", "Fast"),
        disadvantages=("Sensitive to evidence quality",),
    )


def _alternative_package() -> AlternativeDecisionPackage:
    strong = _alternative()
    weak = AlternativeDecision(
        alternative_id="alt-2",
        title="Defer decision",
        description="Wait for more context before deciding.",
        confidence=0.3,
        feasibility=0.4,
        risks=("Decision latency may create opportunity cost.", "critical deadline risk"),
        advantages=("Reduces unknowns",),
        disadvantages=("Slow", "May miss timing"),
    )
    return AlternativeDecisionPackage(
        alternatives=(weak, strong),
        total_generated=2,
        generation_strategy="test",
    )
