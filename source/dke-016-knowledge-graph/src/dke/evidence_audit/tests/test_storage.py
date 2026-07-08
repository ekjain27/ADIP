import evidence_audit as ea


def test_storage_interface_behavior():
    storage = ea.InMemoryAuditStorage()
    event = ea.AuditEvent(decision_id="d1", event_type=ea.AuditEventType.QUERY_RECEIVED)
    storage.append_event(event)
    assert storage.events_for_decision("d1") == (event,)
