from types import SimpleNamespace

import decision_orchestrator as do


class FakeRetrieval:
    def __init__(self):
        self.called = False

    def retrieve_context(self, query):
        self.called = True
        return SimpleNamespace(facts=("fact",), evidence=("e1",), confidence=70)

    def retrieve_broader_context(self, query):
        return SimpleNamespace(facts=("fact", "extra"), evidence=("e1", "e2"), confidence=85)


class FakeReasoning:
    def __init__(self):
        self.called = False

    def reason(self, context_package, query):
        self.called = True
        return do.ReasoningResult(recommendation="Proceed", confidence=0.7, reasoning_summary="ok", evidence=("e1",))


def test_orchestrator_start_decision_uses_adapters():
    retrieval = FakeRetrieval()
    reasoning = FakeReasoning()
    orchestrator = do.DecisionReasoningOrchestrator(retrieval, reasoning)
    package = orchestrator.start_decision("choose supplier")
    assert retrieval.called
    assert reasoning.called
    assert orchestrator.get_trace(package.decision_id) is not None


def test_reasoning_adapter_accepts_callable():
    adapter = do.ReasoningAdapter(lambda context, query: {"recommendation": "Proceed", "confidence": 0.6, "evidence": ("e1",)})
    result = adapter.reason(SimpleNamespace(evidence=("e1",)), do.DecisionQuery("query"))
    assert result.recommendation == "Proceed"


class FakeDKE017PublicService:
    def __init__(self):
        self.received_query = None

    def reason(self, reasoning_query):
        self.received_query = reasoning_query
        return {
            "conclusions": ({"id": "c1", "confidence": 0.72, "summary": "Supplier path supports decision context."},),
            "conflicts": (),
            "explanation": {"summary": "DKE-017 explanation summary"},
        }


def test_reasoning_adapter_calls_dke017_style_public_reason_api():
    service = FakeDKE017PublicService()
    adapter = do.ReasoningAdapter(service)
    context = SimpleNamespace(facts=(SimpleNamespace(id="supplier", name="Supplier A"),), evidence=("e1",))
    result = adapter.reason(context, do.DecisionQuery("query"))
    assert service.received_query["sourceNodeId"] == "supplier"
    assert result.confidence == 0.72
    assert result.metadata["source"] == "DKE-017"


def test_reasoning_adapter_without_dke017_service_fails_loudly():
    adapter = do.ReasoningAdapter()
    try:
        adapter.reason(SimpleNamespace(facts=(), evidence=()), do.DecisionQuery("query"))
    except RuntimeError as exc:
        assert "DKE-017 public API" in str(exc)
    else:
        raise AssertionError("missing DKE-017 service should fail loudly")
