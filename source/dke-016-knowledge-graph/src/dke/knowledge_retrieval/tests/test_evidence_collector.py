import knowledge_retrieval as kr


def test_evidence_collector_collects_node_and_relationship_evidence_once():
    store = kr.InMemoryKnowledgeStore(
        nodes=(kr.KnowledgeNode(id="a", name="A"),),
        relationships=(kr.KnowledgeRelationship(id="r", source_id="a", target_id="b"),),
        evidence=(kr.EvidenceItem(id="e1", node_id="a"), kr.EvidenceItem(id="e2", relationship_id="r")),
    )
    evidence = kr.EvidenceCollector(store).collect(("a",), ("r",))
    assert [item.id for item in evidence] == ["e1", "e2"]
