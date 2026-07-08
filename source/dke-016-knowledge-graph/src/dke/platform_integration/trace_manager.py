from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from .observability_errors import TraceValidationError


DETERMINISTIC_TRACE_TIMESTAMP = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class TraceRecord:
    trace_id: str
    status: str
    context: Mapping[str, Any]
    started_at: str = DETERMINISTIC_TRACE_TIMESTAMP
    ended_at: str | None = None

    def end(self) -> "TraceRecord":
        if self.status == "ended":
            raise TraceValidationError(f"trace already ended: {self.trace_id}")
        return replace(self, status="ended", ended_at=DETERMINISTIC_TRACE_TIMESTAMP)

    def snapshot(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "status": self.status,
            "context": dict(sorted(self.context.items())),
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }


class TraceManager:
    def __init__(self) -> None:
        self._traces: dict[str, TraceRecord] = {}
        self._counter = 0

    def start_trace(self, context: Mapping[str, Any] | None = None) -> TraceRecord:
        if context is not None and not isinstance(context, Mapping):
            raise TraceValidationError("trace context must be a mapping")
        self._counter += 1
        trace_id = f"trace-{self._counter:06d}"
        record = TraceRecord(trace_id=trace_id, status="active", context=dict(context or {}))
        self._traces[trace_id] = record
        return record

    def end_trace(self, trace_id: str) -> TraceRecord:
        normalized = self._validate_trace_id(trace_id)
        try:
            record = self._traces[normalized]
        except KeyError as exc:
            raise TraceValidationError(f"trace is not registered: {normalized}") from exc
        ended = record.end()
        self._traces[normalized] = ended
        return ended

    def snapshot(self) -> dict[str, Any]:
        return {
            "trace_count": len(self._traces),
            "traces": tuple(self._traces[trace_id].snapshot() for trace_id in sorted(self._traces)),
        }

    def _validate_trace_id(self, trace_id: str) -> str:
        if not isinstance(trace_id, str) or not trace_id.startswith("trace-"):
            raise TraceValidationError(f"invalid trace id: {trace_id}")
        return trace_id
