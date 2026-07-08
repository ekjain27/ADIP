from types import SimpleNamespace

import decision_orchestrator as do


class BroaderRetrieval:
    def __init__(self):
        self.called = False

    def retrieve_broader_context(self, query):
        self.called = True
        return SimpleNamespace(facts=("fact",), evidence=("e1",), confidence=75)


def test_fallback_on_weak_context_requests_broader_retrieval():
    adapter = BroaderRetrieval()
    report = do.ValidationReport(valid=True, issues=(do.ValidationIssue("weak_context", "weak"),))
    context = SimpleNamespace(facts=("fact",), evidence=("e1",), confidence=20)
    improved = do.FallbackPolicy().improve_context(adapter, do.DecisionQuery("query"), context, report)
    assert adapter.called
    assert improved.confidence == 75


def test_fallback_on_low_confidence_adds_limitation():
    result = do.ReasoningResult(recommendation="Proceed", confidence=0.4, evidence=("e1",))
    adjusted = do.FallbackPolicy().apply_reasoning_fallback(
        result,
        do.ValidationReport(valid=True),
        do.ValidationReport(valid=True),
    )
    assert adjusted.confidence == 0.4
    assert any("below threshold" in limitation for limitation in adjusted.limitations)
