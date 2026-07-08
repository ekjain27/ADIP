from __future__ import annotations

from .compliance import ComplianceEvaluator
from .models import AuditReport, ComplianceFinding, DecisionTrace


class AuditReportGenerator:
    def generate(self, decision_id: str, trace: DecisionTrace, findings: tuple[ComplianceFinding, ...]) -> AuditReport:
        status = ComplianceEvaluator().status_for(findings)
        metadata = {"finding_count": len(findings), "traceability_chain": {**dict(trace.metadata.get("traceability_chain", {})), "audit_report": decision_id}}
        return AuditReport(decision_id=decision_id, status=status, findings=findings, trace=trace, metadata=metadata)
