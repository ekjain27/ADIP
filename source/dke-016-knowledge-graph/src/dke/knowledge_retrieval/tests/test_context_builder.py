import knowledge_retrieval as kr


def test_context_builder_packages_facts_relationships_evidence_and_trace():
    query = kr.RetrievalQuery(text="Supplier")
    node = kr.KnowledgeNode(id="supplier", name="Supplier")
    relationship = kr.KnowledgeRelationship(id="rel", source_id="supplier", target_id="factory")
    evidence = kr.EvidenceItem(id="ev", node_id="supplier")
    trace = kr.RetrievalTrace(query=query, expanded_entities=("Supplier",))
    result = kr.RetrievalResult(node=node, score=80, relationships=(relationship,), evidence=(evidence,))
    context = kr.ContextBuilder().build(query, ("Supplier",), (result,), trace)
    assert context.facts == (node,)
    assert context.relationships == (relationship,)
    assert context.evidence == (evidence,)
    assert context.metadata["trace"] == trace
    assert context.metadata["retrieval_results"] == (result,)


def test_context_package_format_is_stable_for_reasoning():
    query = kr.RetrievalQuery(text="Supplier")
    context = kr.ContextPackage(query=query, entities=("Supplier",), facts=(), relationships=(), evidence=(), confidence=75, metadata={})
    assert context.query is query
    assert context.entities == ("Supplier",)
    assert isinstance(context.facts, tuple)
    assert isinstance(context.relationships, tuple)
    assert isinstance(context.evidence, tuple)
