from types import SimpleNamespace

import evidence_audit as ea


def test_integration_workflow_from_decision_to_audit_report():
    decision = SimpleNamespace(
        decision_id="d-integration",
        query="approve rollout",
        recommendation="Approve controlled rollout",
        confidence=0.82,
        supporting_factors=("evidence supports rollout",),
        risk_factors=("execution risk",),
        assumptions=("current evidence remains valid",),
        limitations=(),
        evidence=(SimpleNamespace(id="e1", source="contract", excerpt="support", confidence=0.9),),
    )
    event = ea.record_decision(decision)
    assert event.event_type == ea.AuditEventType.DECISION_GENERATED
    trace = ea.build_trace(decision)
    findings = ea.validate_evidence(decision)
    report = ea.AuditReportGenerator().generate(decision.decision_id, trace, findings)
    exported = ea.export_trace(decision.decision_id)
    assert report.status == ea.AuditStatus.PASSED
    assert exported["decision_id"] == "d-integration"
    assert ea.get_audit_trail(decision.decision_id)


def test_trace_links_query_context_evidence_reasoning_decision_and_audit_report():
    evidence = SimpleNamespace(id="e1", source="doc", excerpt="support", confidence=0.9)
    context = SimpleNamespace(query="approve rollout", facts=("fact",), relationships=("rel",), evidence=(evidence,), confidence=80)
    reasoning = {"explanation": {"steps": ("reasoning step",)}, "unsupported_conclusions": ()}
    decision = SimpleNamespace(
        decision_id="d-chain",
        query="approve rollout",
        recommendation="Approve",
        confidence=0.8,
        supporting_factors=("supported by evidence",),
        risk_factors=(),
        assumptions=(),
        limitations=(),
        evidence=(evidence,),
    )
    trace = ea.TraceBuilder().build_trace(decision, context, reasoning)
    findings = ea.EvidenceValidator().validate_evidence(decision, context)
    report = ea.AuditReportGenerator().generate(decision.decision_id, trace, findings)
    chain = report.metadata["traceability_chain"]
    assert chain["query"] == "approve rollout"
    assert chain["context_package"] is True
    assert chain["evidence_count"] >= 1
    assert chain["reasoning_output"] is True
    assert chain["decision_package"] == "d-chain"
    assert chain["audit_report"] == "d-chain"
