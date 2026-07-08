from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_decision_id() -> str:
    return f"decision-{uuid4().hex}"


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, round(value, 6)))


class DecisionStatus(str, Enum):
    CREATED = "created"
    RETRIEVING = "retrieving"
    VALIDATING_CONTEXT = "validating_context"
    REASONING = "reasoning"
    VALIDATING_REASONING = "validating_reasoning"
    APPLYING_FALLBACK = "applying_fallback"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True)
class DecisionQuery:
    text: str
    constraints: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("DecisionQuery.text is required")


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "warning"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def blocking(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)


@dataclass(frozen=True)
class ReasoningResult:
    recommendation: str | None = None
    confidence: float = 0.0
    reasoning_summary: str = ""
    supporting_factors: tuple[str, ...] = ()
    risk_factors: tuple[str, ...] = ()
    evidence: tuple[Any, ...] = ()
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    unsupported_conclusions: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", clamp_confidence(self.confidence))


@dataclass(frozen=True)
class DecisionTraceEvent:
    name: str
    occurred_at: datetime = field(default_factory=utc_now)
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionTrace:
    decision_id: str
    events: tuple[DecisionTraceEvent, ...] = ()

    def add(self, name: str, payload: Mapping[str, Any] | None = None) -> "DecisionTrace":
        return DecisionTrace(
            decision_id=self.decision_id,
            events=(*self.events, DecisionTraceEvent(name=name, payload=payload or {})),
        )


@dataclass(frozen=True)
class DecisionState:
    decision_id: str
    query: DecisionQuery
    status: DecisionStatus = DecisionStatus.CREATED
    context_package: Any | None = None
    reasoning_result: ReasoningResult | None = None
    context_validation: ValidationReport | None = None
    reasoning_validation: ValidationReport | None = None
    trace: DecisionTrace | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def transition(self, status: DecisionStatus, **changes: Any) -> "DecisionState":
        data = {
            "decision_id": self.decision_id,
            "query": self.query,
            "status": status,
            "context_package": self.context_package,
            "reasoning_result": self.reasoning_result,
            "context_validation": self.context_validation,
            "reasoning_validation": self.reasoning_validation,
            "trace": self.trace,
            "metadata": self.metadata,
        }
        data.update(changes)
        return DecisionState(**data)


@dataclass(frozen=True)
class DecisionPackage:
    decision_id: str
    query: str
    recommendation: str
    confidence: float
    reasoning_summary: str
    supporting_factors: tuple[str, ...]
    risk_factors: tuple[str, ...]
    evidence: tuple[Any, ...]
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    trace: DecisionTrace
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", clamp_confidence(self.confidence))
