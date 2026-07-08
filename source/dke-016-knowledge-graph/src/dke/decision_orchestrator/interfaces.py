from __future__ import annotations

from typing import Any, Protocol

from .models import DecisionPackage, DecisionQuery, ReasoningResult


class RetrievalPort(Protocol):
    def retrieve_context(self, query: DecisionQuery) -> Any: ...
    def retrieve_broader_context(self, query: DecisionQuery) -> Any: ...


class ReasoningPort(Protocol):
    def reason(self, context_package: Any, query: DecisionQuery) -> ReasoningResult: ...


class DecisionPackageBuilderPort(Protocol):
    def build(self, query: DecisionQuery, reasoning_result: ReasoningResult, context_package: Any, trace: Any) -> DecisionPackage: ...


class TraceStorePort(Protocol):
    def record(self, decision_id: str, name: str, payload: dict[str, Any] | None = None) -> None: ...
    def get_trace(self, decision_id: str) -> Any | None: ...
