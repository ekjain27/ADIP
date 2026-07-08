from __future__ import annotations

from .models import AuditEvent, AuditReport, DecisionTrace


class InMemoryAuditStorage:
    def __init__(self) -> None:
        self._events: dict[str, list[AuditEvent]] = {}
        self._event_ids: set[str] = set()
        self._traces: dict[str, DecisionTrace] = {}
        self._reports: dict[str, AuditReport] = {}

    def append_event(self, event: AuditEvent) -> None:
        if event.event_id in self._event_ids:
            raise ValueError(f"audit event already exists: {event.event_id}")
        self._event_ids.add(event.event_id)
        self._events.setdefault(event.decision_id, []).append(event)

    def events_for_decision(self, decision_id: str) -> tuple[AuditEvent, ...]:
        return tuple(sorted(self._events.get(decision_id, ()), key=lambda event: event.occurred_at))

    def save_trace(self, trace: DecisionTrace) -> None:
        self._traces[trace.decision_id] = trace

    def get_trace(self, decision_id: str) -> DecisionTrace | None:
        return self._traces.get(decision_id)

    def save_report(self, report: AuditReport) -> None:
        self._reports[report.decision_id] = report

    def get_report(self, decision_id: str) -> AuditReport | None:
        return self._reports.get(decision_id)
