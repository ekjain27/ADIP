from __future__ import annotations

from typing import Any

from .adapters import DKE018ContextPackageAdapter, DecisionPackageAdapter, ReasoningOutputAdapter
from .evidence_linker import EvidenceLinker
from .models import AuditEvent, AuditEventType, DecisionTrace
from .provenance import ProvenanceTracker


class TraceBuilder:
    def build_trace(
        self,
        decision_package: Any,
        context_package: Any | None = None,
        reasoning_output: Any | None = None,
        events: tuple[AuditEvent, ...] = (),
    ) -> DecisionTrace:
        package = DecisionPackageAdapter(decision_package)
        context = DKE018ContextPackageAdapter(context_package) if context_package is not None else None
        reasoning = ReasoningOutputAdapter(reasoning_output) if reasoning_output is not None else None
        converted_events = tuple(
            AuditEvent(
                decision_id=package.decision_id,
                event_type=getattr(event, "name", AuditEventType.DECISION_GENERATED),
                payload=dict(getattr(event, "payload", {}) or {}),
            )
            for event in package.trace_events()
        )
        base_events = tuple(events) + converted_events
        if not base_events:
            base_events = (AuditEvent(decision_id=package.decision_id, event_type=AuditEventType.DECISION_GENERATED, payload={"recommendation": package.recommendation}),)
        if context is not None:
            base_events = (
                *base_events,
                AuditEvent(
                    decision_id=package.decision_id,
                    event_type=AuditEventType.RETRIEVAL_COMPLETED,
                    payload={"facts": len(context.facts()), "evidence": len(context.evidence()), "confidence": context.confidence},
                ),
            )
        if reasoning is not None:
            base_events = (
                *base_events,
                AuditEvent(
                    decision_id=package.decision_id,
                    event_type=AuditEventType.REASONING_COMPLETED,
                    payload={"steps": len(reasoning.reasoning_steps()), "unsupported_claims": reasoning.unsupported_claims()},
                ),
            )
        links = EvidenceLinker().link_evidence(decision_package, context_package)
        provenance = ProvenanceTracker().create_records(decision_package, context_package)
        return DecisionTrace(
            decision_id=package.decision_id,
            query=package.query,
            events=base_events,
            provenance=provenance,
            evidence_links=links,
            metadata={
                "confidence": package.confidence,
                "risks": package.risks(),
                "assumptions": package.assumptions(),
                "traceability_chain": {
                    "query": package.query,
                    "context_package": context is not None,
                    "evidence_count": len(tuple(ref for link in links for ref in link.evidence_refs)),
                    "reasoning_output": reasoning is not None,
                    "decision_package": package.decision_id,
                    "audit_report": None,
                },
            },
        )
