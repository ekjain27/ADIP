import knowledge_retrieval as kr


def test_traversal_respects_depth_and_prevents_cycles():
    store = kr.InMemoryKnowledgeStore(
        nodes=(kr.KnowledgeNode(id="a", name="A"), kr.KnowledgeNode(id="b", name="B"), kr.KnowledgeNode(id="c", name="C")),
        relationships=(
            kr.KnowledgeRelationship(id="ab", source_id="a", target_id="b"),
            kr.KnowledgeRelationship(id="bc", source_id="b", target_id="c"),
            kr.KnowledgeRelationship(id="ca", source_id="c", target_id="a"),
        ),
    )
    traversal = kr.GraphTraversal(store)
    nodes, relationships = traversal.subgraph("a", 1)
    assert {node.id for node in nodes} == {"a", "b", "c"}
    assert {relationship.id for relationship in relationships} == {"ab", "ca"}


def test_graph_traversal_depth_limits_related_nodes():
    store = kr.InMemoryKnowledgeStore(
        nodes=(kr.KnowledgeNode(id="a", name="A"), kr.KnowledgeNode(id="b", name="B"), kr.KnowledgeNode(id="c", name="C")),
        relationships=(
            kr.KnowledgeRelationship(id="ab", source_id="a", target_id="b"),
            kr.KnowledgeRelationship(id="bc", source_id="b", target_id="c"),
        ),
    )
    traversal = kr.GraphTraversal(store)
    shallow_nodes, _ = traversal.subgraph("a", 1)
    deep_nodes, _ = traversal.subgraph("a", 2)
    assert {node.id for node in shallow_nodes} == {"a", "b"}
    assert {node.id for node in deep_nodes} == {"a", "b", "c"}
