import evidence_audit as ea


def test_compliance_finding_severity_drives_status():
    findings = (ea.ComplianceFinding("x", "problem", ea.AuditSeverity.HIGH, ea.AuditStatus.WARNING),)
    assert ea.ComplianceEvaluator().status_for(findings) == ea.AuditStatus.WARNING
    failed = (ea.ComplianceFinding("x", "problem", ea.AuditSeverity.CRITICAL, ea.AuditStatus.OPEN),)
    assert ea.ComplianceEvaluator().status_for(failed) == ea.AuditStatus.FAILED
