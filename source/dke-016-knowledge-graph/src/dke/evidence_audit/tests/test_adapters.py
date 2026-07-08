from types import SimpleNamespace

import evidence_audit as ea


def test_dke019_adapter_compatibility():
    package = SimpleNamespace(
        decision_id="d1",
        query="choose",
        recommendation="Proceed",
        confidence=75,
        supporting_factors=("factor",),
        risk_factors=("risk",),
        assumptions=("assumption",),
        limitations=(),
        evidence=(SimpleNamespace(id="e1"),),
    )
    adapter = ea.DecisionPackageAdapter(package)
    assert adapter.confidence == 0.75
    assert adapter.claims() == ("factor", "Proceed")


def test_context_and_reasoning_adapters():
    evidence = SimpleNamespace(id="e1", source="doc", excerpt="text", confidence=0.9)
    assert ea.EvidenceAdapter().to_reference(evidence).evidence_id == "e1"
    reasoning = {"evidence": (evidence,), "unsupported_conclusions": ("claim",)}
    assert ea.ReasoningOutputAdapter(reasoning).unsupported_claims() == ("claim",)


def test_frozen_module_adapter_compatibility_names():
    context = SimpleNamespace(query="q", facts=("fact",), relationships=("rel",), evidence=(SimpleNamespace(id="e1"),), confidence=88)
    decision = SimpleNamespace(decision_id="d1", query="q", recommendation="Proceed", confidence=0.8, evidence=(SimpleNamespace(id="e1"),))
    reasoning = {"explanation": {"steps": ("step",)}, "unsupported_conclusions": ("unsupported",)}
    assert ea.DKE018ContextPackageAdapter(context).confidence == 0.88
    assert ea.DKE019DecisionPackageAdapter(decision).decision_id == "d1"
    assert ea.DKE017ReasoningOutputAdapter(reasoning).reasoning_steps() == ("step",)
    assert ea.DKE018ContextPackageAdapter.module.module_name == "knowledge_retrieval"
    assert ea.DKE017ReasoningOutputAdapter.module.module_name == "knowledge_reasoning"
    assert ea.DKE019DecisionPackageAdapter.module.module_name == "decision_orchestrator"
