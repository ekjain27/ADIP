from dataclasses import FrozenInstanceError

import evidence_audit as ea


def test_audit_event_creation_and_immutability():
    event = ea.AuditEvent(decision_id="d1", event_type=ea.AuditEventType.QUERY_RECEIVED)
    assert event.event_id.startswith("audit-event-")
    try:
        event.decision_id = "d2"
    except FrozenInstanceError:
        assert True
    else:
        raise AssertionError("AuditEvent should be immutable")


def test_expected_models_exist():
    assert ea.AuditSeverity.HIGH.value == "high"
    assert ea.AuditStatus.PASSED.value == "passed"
    assert ea.EvidenceReference("e1", confidence=80).confidence == 0.8
