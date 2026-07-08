import decision_orchestrator as do


def test_trace_creation_and_lookup():
    store = do.InMemoryTraceStore()
    store.start("d1")
    store.record("d1", "retrieved", {"facts": 2})
    trace = store.get_trace("d1")
    assert trace is not None
    assert [event.name for event in trace.events] == ["trace_started", "retrieved"]
