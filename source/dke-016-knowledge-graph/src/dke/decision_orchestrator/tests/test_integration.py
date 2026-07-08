from types import SimpleNamespace

import decision_orchestrator as do


class FakeDKE018:
    RetrievalQuery = None

    def __init__(self):
        self.called = False

    def retrieve_context(self, query):
        self.called = True
        return SimpleNamespace(query=query, facts=("fact",), relationships=("rel",), evidence=("e1",), confidence=88, metadata={})


class FakeDKE017:
    def __init__(self):
        self.received_context = None

    def reason(self, context_package, query):
        self.received_context = context_package
        return {
            "recommendation": "Approve controlled rollout",
            "confidence": 0.82,
            "reasoning_summary": "Retrieved evidence supports a controlled rollout.",
            "supporting_factors": ("evidence",),
            "risk_factors": ("execution risk",),
            "evidence": tuple(context_package.evidence),
            "assumptions": ("current evidence remains valid",),
            "limitations": (),
        }


def test_integration_with_fake_dke018_and_dke017_adapters():
    retrieval_module = FakeDKE018()
    reasoning_service = FakeDKE017()
    orchestrator = do.DecisionReasoningOrchestrator(
        retrieval_adapter=do.RetrievalAdapter(retrieval_module),
        reasoning_adapter=do.ReasoningAdapter(reasoning_service),
    )
    package = orchestrator.run_pipeline("approve rollout")
    assert retrieval_module.called
    assert reasoning_service.received_context is not None
    assert package.recommendation == "Approve controlled rollout"
    assert package.evidence == ("e1",)


def test_retrieval_adapter_supports_query_constructor_style():
    class QueryStyleRetrieval:
        class RetrievalQuery:
            def __init__(self, query, metadata=None):
                self.query = query
                self.metadata = metadata

        def __init__(self):
            self.received = None

        def retrieve_context(self, query):
            self.received = query
            return SimpleNamespace(facts=("fact",), relationships=(), evidence=("e1",), confidence=80)

    module = QueryStyleRetrieval()
    context = do.RetrievalAdapter(module).retrieve_context(do.DecisionQuery("approve rollout", metadata={"source": "test"}))
    assert module.received.query == "approve rollout"
    assert module.received.metadata == {"source": "test"}
    assert context.facts == ("fact",)


def test_retrieval_adapter_supports_text_constructor_style_and_supported_broader_fields():
    class TextStyleRetrieval:
        class RetrievalQuery:
            def __init__(self, text, max_results=10):
                self.text = text
                self.max_results = max_results

        def __init__(self):
            self.received = None

        def retrieve_context(self, query):
            self.received = query
            return SimpleNamespace(facts=("fact",), relationships=(), evidence=("e1",), confidence=80)

    module = TextStyleRetrieval()
    context = do.RetrievalAdapter(module).retrieve_broader_context(do.DecisionQuery("approve rollout"))
    assert module.received.text == "approve rollout"
    assert module.received.max_results == 25
    assert not hasattr(module.received, "max_depth")
    assert context.evidence == ("e1",)
