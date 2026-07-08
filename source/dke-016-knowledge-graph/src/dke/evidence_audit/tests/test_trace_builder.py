from types import SimpleNamespace

import evidence_audit as ea


def test_trace_builder_exportable_structure():
    decision = SimpleNamespace(decision_id="d1", query="q", recommendation="Proceed", confidence=0.7, evidence=(SimpleNamespace(id="e1"),))
    trace = ea.TraceBuilder().build_trace(decision)
    assert trace.decision_id == "d1"
    assert trace.events
    assert trace.evidence_links
    assert trace.provenance
