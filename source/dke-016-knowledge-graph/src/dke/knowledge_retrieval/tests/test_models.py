import knowledge_retrieval as kr


def test_models_validate_scores_and_context_confidence():
    node = kr.KnowledgeNode(id="n1", name="Supplier A", confidence=91)
    query = kr.RetrievalQuery(text="Supplier risk", mode=kr.RetrievalMode.HYBRID)
    context = kr.ContextPackage(query=query, entities=("Supplier A",), facts=(node,), relationships=(), evidence=(), confidence=120)
    assert context.confidence == 100
    assert kr.RetrievalMode.EXACT.value == "exact"


def test_relationship_and_evidence_models_are_stable():
    relationship = kr.KnowledgeRelationship(id="r1", source_id="n1", target_id="n2", relationship_type=kr.RelationshipType.DEPENDS_ON)
    evidence = kr.EvidenceItem(id="e1", node_id="n1", evidence_type=kr.EvidenceType.DOCUMENT, source="doc", excerpt="Supplier A risk")
    assert relationship.relationship_type == kr.RelationshipType.DEPENDS_ON
    assert evidence.confidence == 100
