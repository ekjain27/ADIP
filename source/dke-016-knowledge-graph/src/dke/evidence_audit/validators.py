from __future__ import annotations

from typing import Any

from .adapters import DecisionPackageAdapter
from .evidence_linker import EvidenceLinker
from .models import AuditSeverity, AuditStatus, ComplianceFinding


class EvidenceValidator:
    def validate_evidence(self, decision_package: Any, context_package: Any | None = None) -> tuple[ComplianceFinding, ...]:
        package = DecisionPackageAdapter(decision_package)
        findings: list[ComplianceFinding] = []
        links = EvidenceLinker().link_evidence(decision_package, context_package)
        if not package.evidence() and not package.limitations():
            findings.append(ComplianceFinding("missing_recommendation_evidence", "recommendation lacks evidence or limitation", AuditSeverity.HIGH, AuditStatus.FAILED))
        for link in links:
            if not link.supported:
                findings.append(ComplianceFinding("unsupported_claim", f"claim lacks evidence: {link.claim}", AuditSeverity.MEDIUM, AuditStatus.WARNING))
        if not 0 <= package.confidence <= 1:
            findings.append(ComplianceFinding("invalid_confidence", "confidence must be between 0 and 1", AuditSeverity.HIGH, AuditStatus.FAILED))
        if any("conflict" in str(item).lower() for item in package.risks()):
            findings.append(ComplianceFinding("conflicting_evidence", "conflicting evidence was flagged", AuditSeverity.MEDIUM, AuditStatus.WARNING))
        if not links:
            findings.append(ComplianceFinding("missing_provenance", "no claim/evidence provenance links were created", AuditSeverity.MEDIUM, AuditStatus.WARNING))
        if not findings:
            findings.append(ComplianceFinding("evidence_validated", "evidence traceability passed", AuditSeverity.INFO, AuditStatus.PASSED))
        return tuple(findings)
