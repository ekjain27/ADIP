from types import SimpleNamespace

import evidence_audit as ea


def test_evidence_linking():
    decision = SimpleNamespace(
        decision_id="d1",
        query="q",
        recommendation="Proceed",
        supporting_factors=("quality",),
        evidence=(SimpleNamespace(id="e1", source="doc", confidence=0.9),),
    )
    links = ea.EvidenceLinker().link_evidence(decision)
    assert len(links) == 2
    assert all(link.supported for link in links)
    assert links[0].evidence_refs[0].evidence_id == "e1"
