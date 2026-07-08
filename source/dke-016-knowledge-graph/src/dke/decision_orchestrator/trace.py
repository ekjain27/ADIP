from __future__ import annotations

from typing import Any

from .models import DecisionTrace


class InMemoryTraceStore:
    def __init__(self) -> None:
        self._traces: dict[str, DecisionTrace] = {}

    def start(self, decision_id: str) -> DecisionTrace:
        trace = DecisionTrace(decision_id=decision_id).add("trace_started")
        self._traces[decision_id] = trace
        return trace

    def record(self, decision_id: str, name: str, payload: dict[str, Any] | None = None) -> None:
        trace = self._traces.get(decision_id, DecisionTrace(decision_id=decision_id))
        self._traces[decision_id] = trace.add(name, payload)

    def get_trace(self, decision_id: str) -> DecisionTrace | None:
        return self._traces.get(decision_id)
