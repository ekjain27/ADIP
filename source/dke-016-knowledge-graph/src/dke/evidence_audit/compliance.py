from __future__ import annotations

from .models import AuditSeverity, AuditStatus, ComplianceFinding


class ComplianceEvaluator:
    def status_for(self, findings: tuple[ComplianceFinding, ...]) -> AuditStatus:
        if any(finding.status == AuditStatus.FAILED or finding.severity == AuditSeverity.CRITICAL for finding in findings):
            return AuditStatus.FAILED
        if any(finding.status == AuditStatus.WARNING or finding.severity in {AuditSeverity.MEDIUM, AuditSeverity.HIGH} for finding in findings):
            return AuditStatus.WARNING
        return AuditStatus.PASSED
