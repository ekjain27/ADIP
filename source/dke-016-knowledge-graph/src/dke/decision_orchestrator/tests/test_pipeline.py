from types import SimpleNamespace

import decision_orchestrator as do


class FakeRetrieval:
    def __init__(self):
        self.calls = []

    def retrieve_context(self, query):
        self.calls.append("retrieve_context")
        return SimpleNamespace(facts=("fact",), evidence=("e1",), confidence=80)

    def retrieve_broader_context(self, query):
        self.calls.append("retrieve_broader_context")
        return SimpleNamespace(facts=("fact", "broader"), evidence=("e1", "e2"), confidence=90)


class FakeReasoning:
    def __init__(self):
        self.calls = []

    def reason(self, context_package, query):
        self.calls.append("reason")
        return do.ReasoningResult(
            recommendation="Proceed",
            confidence=0.8,
            reasoning_summary="Evidence supports proceeding.",
            supporting_factors=("support",),
            risk_factors=("risk",),
            evidence=tuple(context_package.evidence),
        )


def test_pipeline_order_retrieval_and_reasoning_called():
    retrieval = FakeRetrieval()
    reasoning = FakeReasoning()
    package = do.DecisionPipeline(retrieval, reasoning).run("choose supplier")
    assert retrieval.calls == ["retrieve_context"]
    assert reasoning.calls == ["reason"]
    assert package.recommendation == "Proceed"
    names = [event.name for event in package.trace.events]
    assert names.index("retrieve_context_completed") < names.index("reasoning_started")
