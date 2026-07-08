import knowledge_retrieval as kr


def test_graph_search_finds_entity_subgraph():
    store = kr.InMemoryKnowledgeStore(
        nodes=(kr.KnowledgeNode(id="a", name="A"), kr.KnowledgeNode(id="b", name="B")),
        relationships=(kr.KnowledgeRelationship(id="r", source_id="a", target_id="b"),),
    )
    results = kr.InMemoryGraphSearch(store).search(("A",), 1)
    assert [result.node.id for result in results] == ["a", "b"]
    assert results[0].connectivity == 20
