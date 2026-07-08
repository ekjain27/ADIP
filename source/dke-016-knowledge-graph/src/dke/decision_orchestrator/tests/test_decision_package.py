from types import SimpleNamespace

import decision_orchestrator as do


def test_decision_package_structure():
    trace = do.DecisionTrace("d1").add("built")
    context = SimpleNamespace(evidence=("context-evidence",), confidence=82)
    result = do.ReasoningResult(
        recommendation="Choose Supplier A",
        confidence=0.76,
        reasoning_summary="Supplier A is supported.",
        supporting_factors=("quality",),
        risk_factors=("capacity",),
        assumptions=("demand stable",),
    )
    package = do.DecisionPackageBuilder().build(do.DecisionQuery("choose supplier"), result, context, trace)
    assert package.recommendation == "Choose Supplier A"
    assert package.evidence == ("context-evidence",)
    assert package.metadata["orchestrator"] == "DKE-019"
