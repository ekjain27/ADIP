import pytest

from decision_engine.alternatives import AlternativeDecision, AlternativeDecisionPackage, AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator, EvaluationScore, EvaluatedAlternative, EvaluatedDecisionPackage, default_criteria
from decision_engine.ranking import DecisionRanker, RankedAlternative, RankedDecisionPackage, RankingStrategy, RankingValidator, TieBreaker


def test_ranking_strategy_calculates_score_between_zero_and_one():
    score = RankingStrategy().score(_evaluated("alt-1", 0.75, 0.8, "moderate"))
    assert 0.0 <= score <= 1.0


def test_ranker_ranks_evaluated_alternatives():
    package = DecisionRanker().rank(_evaluated_package())
    assert package.total_ranked == 3
    assert package.ranked_alternatives


def test_ranks_are_sequential():
    package = DecisionRanker().rank(_evaluated_package())
    assert [item.rank for item in package.ranked_alternatives] == [1, 2, 3]


def test_selected_alternative_is_rank_one():
    package = DecisionRanker().rank(_evaluated_package())
    assert package.selected_alternative is not None
    assert package.selected_alternative.rank == 1
    assert package.selected_alternative.selection_status == "selected"


def test_top_n_selection_works():
    package = DecisionRanker().rank(_evaluated_package(), top_n=2)
    assert len(package.top_alternatives) == 2
    assert package.top_alternatives[1].selection_status == "shortlisted"
    assert package.ranked_alternatives[2].selection_status == "rejected"


def test_tie_breaker_resolves_ties_deterministically():
    first = _evaluated("alt-a", 0.7, 0.8, "moderate")
    second = _evaluated("alt-b", 0.7, 0.8, "moderate")
    ordered = TieBreaker().ordered(((second, 0.7), (first, 0.7)))
    assert ordered[0][0].alternative.alternative_id == "alt-a"


def test_validator_catches_duplicate_ranks():
    evaluated = _evaluated("alt-1", 0.7, 0.8, "moderate")
    ranked = RankedAlternative(1, evaluated, "alt-1", 0.7, 0.7, "selected", 0.7, "ok")
    other = RankedAlternative(1, evaluated, "alt-1", 0.7, 0.7, "shortlisted", 0.7, "ok")
    package = RankedDecisionPackage((ranked, other), ranked, (ranked,), 2, "test", "test")
    with pytest.raises(ValueError, match="Duplicate ranks"):
        RankingValidator().validate(package)


def test_validator_catches_invalid_ranking_score():
    evaluated = _evaluated("alt-1", 0.7, 0.8, "moderate")
    ranked = RankedAlternative(1, evaluated, "alt-1", 0.7, 1.2, "selected", 0.7, "bad")
    package = RankedDecisionPackage((ranked,), ranked, (ranked,), 1, "test", "test")
    with pytest.raises(ValueError, match="ranking_score must be between 0 and 1"):
        RankingValidator().validate(package)


def test_empty_package_does_not_crash():
    empty = EvaluatedDecisionPackage((), 0, "test", default_criteria())
    package = DecisionRanker().rank(empty)
    assert package.total_ranked == 0
    assert package.selected_alternative is None
    assert package.top_alternatives == ()


def test_integration_die_001_to_die_002_to_die_003_to_die_004():
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
    assert ranked_package.selected_alternative is not None
    assert ranked_package.selected_alternative.rank == 1
    assert ranked_package.total_ranked == evaluated_package.total_evaluated


def _evaluated(alternative_id: str, overall: float, confidence: float, recommendation: str) -> EvaluatedAlternative:
    alternative = AlternativeDecision(
        alternative_id=alternative_id,
        title=f"Alternative {alternative_id}",
        description=f"Description {alternative_id}",
        supporting_evidence=("e1", "e2"),
        supporting_goals=("goal",),
        supporting_constraints=("budget",),
        confidence=confidence,
        feasibility=confidence,
        risks=("minor risk",),
        advantages=("traceable", "fast"),
        disadvantages=("limited upside",),
    )
    return EvaluatedAlternative(
        alternative=alternative,
        scores=(EvaluationScore("confidence", confidence, 0.15, round(confidence * 0.15, 6), "confidence"),),
        overall_score=overall,
        confidence=confidence,
        recommendation_level=recommendation,
        explanation="evaluated",
    )


def _evaluated_package() -> EvaluatedDecisionPackage:
    return EvaluatedDecisionPackage(
        evaluated_alternatives=(
            _evaluated("alt-weak", 0.45, 0.5, "weak"),
            _evaluated("alt-strong", 0.88, 0.85, "strong"),
            _evaluated("alt-moderate", 0.66, 0.72, "moderate"),
        ),
        total_evaluated=3,
        evaluation_strategy="test",
        criteria=default_criteria(),
    )
