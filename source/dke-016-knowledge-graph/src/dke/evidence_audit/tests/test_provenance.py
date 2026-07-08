from types import SimpleNamespace

import evidence_audit as ea


def test_provenance_record_creation(fake_decision=None):
    decision = fake_decision or SimpleNamespace(
        decision_id="d1",
        query="q",
        recommendation="Proceed",
        confidence=0.8,
        supporting_factors=("factor",),
        evidence=(SimpleNamespace(id="e1"),),
    )
    records = ea.ProvenanceTracker().create_records(decision)
    assert records[0].subject_type == "decision"
    assert any(record.subject_type == "claim" for record in records)
