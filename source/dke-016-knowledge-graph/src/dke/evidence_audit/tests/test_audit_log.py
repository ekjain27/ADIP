import evidence_audit as ea


def test_audit_log_ordering():
    storage = ea.InMemoryAuditStorage()
    log = ea.AuditLog(storage)
    second = log.record("d1", ea.AuditEventType.REASONING_COMPLETED)
    first = log.record("d1", ea.AuditEventType.QUERY_RECEIVED)
    trail = log.get_audit_trail("d1")
    assert {event.event_id for event in trail} == {first.event_id, second.event_id}
    assert len(trail) == 2


def test_audit_log_prevents_overwrite():
    storage = ea.InMemoryAuditStorage()
    event = ea.AuditEvent(decision_id="d1", event_type=ea.AuditEventType.QUERY_RECEIVED)
    storage.append_event(event)
    try:
        storage.append_event(event)
    except ValueError:
        assert True
    else:
        raise AssertionError("duplicate audit event should fail")
