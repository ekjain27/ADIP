import knowledge_retrieval as kr


def sample_engine():
    nodes = (
        kr.KnowledgeNode(id="supplier", name="Supplier A", aliases=("Supplier Alpha",), type="supplier", confidence=92, authority=80, freshness=70, usage_frequency=60),
        kr.KnowledgeNode(id="factory", name="Factory B", type="factory", confidence=88, authority=70, freshness=80, usage_frequency=40),
        kr.KnowledgeNode(id="obsolete", name="Old Supplier", obsolete=True),
    )
    relationships = (
        kr.KnowledgeRelationship(id="rel1", source_id="supplier", target_id="factory", relationship_type=kr.RelationshipType.DEPENDS_ON, confidence=84, evidence_ids=("evr",)),
    )
    evidence = (
        kr.EvidenceItem(id="ev1", node_id="supplier", source="contract", excerpt="Supplier Alpha supports Factory B", confidence=90),
        kr.EvidenceItem(id="evr", relationship_id="rel1", source="graph", excerpt="Supplier A depends on Factory B", confidence=83),
    )
    store = kr.InMemoryKnowledgeStore(nodes, relationships, evidence)
    return kr.KnowledgeRetrievalEngine(store=store, entity_expander=kr.StaticEntityExpansionProvider({"Supplier A": ("Supplier Alpha",)}, store))


def test_retrieve_context_returns_context_only_not_decisions():
    context = sample_engine().retrieve_context(kr.RetrievalQuery(text='"Supplier A" risk', max_results=3))
    assert context.facts[0].id == "supplier"
    assert context.evidence
    assert "decision" not in context.metadata
    assert context.metadata["engine"] == "DKE-018"


def test_public_retrieval_methods_cover_required_api():
    engine = sample_engine()
    assert engine.retrieve_entity("Supplier Alpha")[0].node.id == "supplier"
    assert engine.retrieve_related("supplier")[0].id == "factory"
    assert engine.retrieve_evidence("Supplier Alpha")
    assert engine.retrieve_subgraph("supplier")[0]
    assert "Supplier Alpha" in engine.expand_entity("Supplier A")


def test_exact_retrieval_and_retrieve_preserves_each_ranked_score():
    results = sample_engine().retrieve(kr.RetrievalQuery(entities=("Supplier A",), mode=kr.RetrievalMode.EXACT))
    scores = {result.node.id: result.score for result in results}
    assert "supplier" in scores
    assert scores["supplier"] != scores["factory"]
    assert all(0 <= score <= 100 for score in scores.values())
