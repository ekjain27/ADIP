import knowledge_retrieval as kr


def test_ranking_score_is_zero_to_one_hundred_and_ordered():
    node_a = kr.KnowledgeNode(id="a", name="A", confidence=100, authority=100, freshness=100, usage_frequency=100)
    node_b = kr.KnowledgeNode(id="b", name="B", confidence=10, authority=10, freshness=10, usage_frequency=10)
    ranked = kr.WeightedRanker().rank(
        (
            kr.RetrievalResult(node=node_b, score=0, similarity=10, confidence=10, authority=10, freshness=10, connectivity=10, usage_frequency=10),
            kr.RetrievalResult(node=node_a, score=0, similarity=100, confidence=100, authority=100, freshness=100, connectivity=100, usage_frequency=100),
        )
    )
    assert ranked[0].node.id == "a"
    assert 0 <= ranked[0].score <= 100
