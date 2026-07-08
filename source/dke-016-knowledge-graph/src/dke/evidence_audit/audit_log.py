from __future__ import annotations

from typing import Any

from .models import AuditEvent, AuditEventType
from .storage import InMemoryAuditStorage


class AuditLog:
    def __init__(self, storage: InMemoryAuditStorage | None = None) -> None:
        self.storage = storage or InMemoryAuditStorage()

    def record_event(self, event: AuditEvent | dict[str, Any]) -> AuditEvent:
        audit_event = event if isinstance(event, AuditEvent) else AuditEvent(**event)
        self.storage.append_event(audit_event)
        return audit_event

    def record(self, decision_id: str, event_type: AuditEventType | str, payload: dict[str, Any] | None = None) -> AuditEvent:
        return self.record_event(AuditEvent(decision_id=decision_id, event_type=event_type, payload=payload or {}))

    def get_audit_trail(self, decision_id: str) -> tuple[AuditEvent, ...]:
        return self.storage.events_for_decision(decision_id)
