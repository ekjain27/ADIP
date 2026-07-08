from types import SimpleNamespace

import evidence_audit as ea


def test_audit_report_generation():
    decision = SimpleNamespace(decision_id="d1", query="q", recommendation="Proceed", confidence=0.7, evidence=(SimpleNamespace(id="e1"),))
    trace = ea.TraceBuilder().build_trace(decision)
    findings = ea.EvidenceValidator().validate_evidence(decision)
    report = ea.AuditReportGenerator().generate("d1", trace, findings)
    assert report.decision_id == "d1"
    assert report.metadata["finding_count"] == len(findings)
