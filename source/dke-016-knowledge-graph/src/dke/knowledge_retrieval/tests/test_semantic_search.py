import knowledge_retrieval as kr


def test_semantic_search_is_deterministic_and_scores_matches():
    store = kr.InMemoryKnowledgeStore(
        nodes=(
            kr.KnowledgeNode(id="a", name="Decision Risk", facts={"topic": "supplier factory"}),
            kr.KnowledgeNode(id="b", name="Finance Plan"),
        )
    )
    search = kr.InMemorySemanticSearch(store)
    results = search.search(kr.RetrievalQuery(text="supplier risk"), ())
    assert [result.node.id for result in results] == ["a"]
    assert 0 < results[0].similarity <= 100


def test_semantic_retrieval_mode_returns_semantic_match():
    store = kr.InMemoryKnowledgeStore(
        nodes=(
            kr.KnowledgeNode(id="supplier", name="Supplier Risk", facts={"body": "factory continuity"}),
            kr.KnowledgeNode(id="finance", name="Finance Plan"),
        )
    )
    engine = kr.KnowledgeRetrievalEngine(store=store)
    context = engine.retrieve_context(kr.RetrievalQuery(text="supplier continuity", mode=kr.RetrievalMode.SEMANTIC))
    assert [node.id for node in context.facts] == ["supplier"]
