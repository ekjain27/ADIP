from types import SimpleNamespace

import decision_orchestrator as do


def test_models_create_valid_decision_package():
    trace = do.DecisionTrace(decision_id="d1").add("created")
    package = do.DecisionPackage(
        decision_id="d1",
        query="choose supplier",
        recommendation="Proceed cautiously",
        confidence=1.5,
        reasoning_summary="Strong evidence with risks.",
        supporting_factors=("evidence",),
        risk_factors=("risk",),
        evidence=(SimpleNamespace(id="e1"),),
        assumptions=("assumption",),
        limitations=("limitation",),
        trace=trace,
    )
    assert package.confidence == 1
    assert package.decision_id == "d1"


def test_decision_query_requires_text():
    try:
        do.DecisionQuery(text=" ")
    except ValueError as exc:
        assert "required" in str(exc)
    else:
        raise AssertionError("empty query should fail")
