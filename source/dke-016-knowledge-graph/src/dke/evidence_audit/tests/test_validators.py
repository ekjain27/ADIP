from types import SimpleNamespace

import evidence_audit as ea


def test_unsupported_claim_detection():
    decision = SimpleNamespace(decision_id="d1", query="q", recommendation="Proceed", confidence=0.8, supporting_factors=("claim",), evidence=())
    findings = ea.EvidenceValidator().validate_evidence(decision)
    assert any(finding.code == "missing_recommendation_evidence" for finding in findings)
    assert any(finding.code == "unsupported_claim" for finding in findings)


def test_conflicting_evidence_flagging():
    decision = SimpleNamespace(
        decision_id="d1",
        query="q",
        recommendation="Proceed",
        confidence=0.8,
        risk_factors=("conflicting evidence",),
        evidence=(SimpleNamespace(id="e1"),),
    )
    findings = ea.EvidenceValidator().validate_evidence(decision)
    assert any(finding.code == "conflicting_evidence" for finding in findings)
