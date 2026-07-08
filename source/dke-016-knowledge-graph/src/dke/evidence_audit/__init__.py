from .adapters import (
    DKE017ReasoningOutputAdapter,
    DKE018ContextPackageAdapter,
    DKE019DecisionPackageAdapter,
    DecisionPackageAdapter,
    EvidenceAdapter,
    ModuleCompatibility,
    ReasoningOutputAdapter,
)
from .audit_log import AuditLog
from .compliance import ComplianceEvaluator
from .evidence_linker import EvidenceLinker
from .interfaces import AuditStorage
from .models import (
    AuditEvent,
    AuditEventType,
    AuditReport,
    AuditSeverity,
    AuditStatus,
    ClaimEvidenceLink,
    ComplianceFinding,
    DecisionTrace,
    EvidenceReference,
    ProvenanceRecord,
)
from .provenance import ProvenanceTracker
from .report import AuditReportGenerator
from .storage import InMemoryAuditStorage
from .trace_builder import TraceBuilder
from .validators import EvidenceValidator

_storage = InMemoryAuditStorage()
_audit_log = AuditLog(_storage)


def record_event(event):
    return _audit_log.record_event(event)


def record_decision(decision_package):
    event = _audit_log.record(
        getattr(decision_package, "decision_id"),
        AuditEventType.DECISION_GENERATED,
        {"recommendation": getattr(decision_package, "recommendation", "")},
    )
    trace = build_trace(decision_package)
    _storage.save_trace(trace)
    return event


def build_trace(decision_package):
    trace = TraceBuilder().build_trace(decision_package, events=_storage.events_for_decision(getattr(decision_package, "decision_id")))
    _storage.save_trace(trace)
    return trace


def link_evidence(decision_package, context_package=None):
    return EvidenceLinker().link_evidence(decision_package, context_package)


def validate_evidence(decision_package):
    return EvidenceValidator().validate_evidence(decision_package)


def generate_audit_report(decision_id):
    trace = _storage.get_trace(decision_id)
    if trace is None:
        raise KeyError(f"no trace found for decision_id: {decision_id}")
    findings = (ComplianceFinding("audit_trace_available", "audit trace is available", AuditSeverity.INFO, AuditStatus.PASSED),)
    report = AuditReportGenerator().generate(decision_id, trace, findings)
    _storage.save_report(report)
    return report


def get_audit_trail(decision_id):
    return _storage.events_for_decision(decision_id)


def export_trace(decision_id):
    trace = _storage.get_trace(decision_id)
    if trace is None:
        raise KeyError(f"no trace found for decision_id: {decision_id}")
    return {
        "decision_id": trace.decision_id,
        "query": trace.query,
        "events": [event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type) for event in trace.events],
        "evidence_links": [link.claim for link in trace.evidence_links],
        "provenance": [record.record_id for record in trace.provenance],
        "metadata": dict(trace.metadata),
    }


__all__ = [
    "AuditEvent",
    "AuditEventType",
    "AuditLog",
    "AuditReport",
    "AuditReportGenerator",
    "AuditSeverity",
    "AuditStatus",
    "AuditStorage",
    "ClaimEvidenceLink",
    "ComplianceEvaluator",
    "ComplianceFinding",
    "DKE017ReasoningOutputAdapter",
    "DKE018ContextPackageAdapter",
    "DKE019DecisionPackageAdapter",
    "DecisionPackageAdapter",
    "DecisionTrace",
    "EvidenceAdapter",
    "EvidenceLinker",
    "EvidenceReference",
    "EvidenceValidator",
    "InMemoryAuditStorage",
    "ModuleCompatibility",
    "ProvenanceRecord",
    "ProvenanceTracker",
    "ReasoningOutputAdapter",
    "TraceBuilder",
    "build_trace",
    "export_trace",
    "generate_audit_report",
    "get_audit_trail",
    "link_evidence",
    "record_decision",
    "record_event",
    "validate_evidence",
]
