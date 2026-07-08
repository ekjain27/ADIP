from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stable_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class AuditEventType(str, Enum):
    QUERY_RECEIVED = "query_received"
    RETRIEVAL_STARTED = "retrieval_started"
    RETRIEVAL_COMPLETED = "retrieval_completed"
    REASONING_STARTED = "reasoning_started"
    REASONING_COMPLETED = "reasoning_completed"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    FALLBACK_TRIGGERED = "fallback_triggered"
    DECISION_GENERATED = "decision_generated"
    EVIDENCE_LINKED = "evidence_linked"
    AUDIT_COMPLETED = "audit_completed"


class AuditSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditStatus(str, Enum):
    OPEN = "open"
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass(frozen=True)
class AuditEvent:
    decision_id: str
    event_type: AuditEventType | str
    payload: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: stable_id("audit-event"))
    occurred_at: datetime = field(default_factory=utc_now)
    actor: str = "system"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceReference:
    evidence_id: str
    source: str = ""
    excerpt: str = ""
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", max(0.0, min(1.0, self.confidence if self.confidence <= 1 else self.confidence / 100)))


@dataclass(frozen=True)
class ProvenanceRecord:
    subject_id: str
    subject_type: str
    source_module: str
    evidence_refs: tuple[EvidenceReference, ...] = ()
    created_at: datetime = field(default_factory=utc_now)
    record_id: str = field(default_factory=lambda: stable_id("provenance"))
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ClaimEvidenceLink:
    claim: str
    evidence_refs: tuple[EvidenceReference, ...]
    supported: bool
    link_id: str = field(default_factory=lambda: stable_id("claim-link"))
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComplianceFinding:
    code: str
    message: str
    severity: AuditSeverity = AuditSeverity.INFO
    status: AuditStatus = AuditStatus.OPEN
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionTrace:
    decision_id: str
    query: str
    events: tuple[AuditEvent, ...]
    provenance: tuple[ProvenanceRecord, ...]
    evidence_links: tuple[ClaimEvidenceLink, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditReport:
    decision_id: str
    status: AuditStatus
    findings: tuple[ComplianceFinding, ...]
    trace: DecisionTrace
    generated_at: datetime = field(default_factory=utc_now)
    report_id: str = field(default_factory=lambda: stable_id("audit-report"))
    metadata: Mapping[str, Any] = field(default_factory=dict)
