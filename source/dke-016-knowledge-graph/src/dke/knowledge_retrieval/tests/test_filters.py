import knowledge_retrieval as kr


def test_filters_remove_low_confidence_duplicate_obsolete_incomplete_unsupported():
    query = kr.RetrievalQuery(text="risk", min_confidence=50, max_results=10)
    keep = kr.RetrievalResult(node=kr.KnowledgeNode(id="keep", name="Keep", confidence=80), score=80)
    duplicate = kr.RetrievalResult(node=kr.KnowledgeNode(id="keep", name="Keep", confidence=80), score=60)
    bad = [
        kr.RetrievalResult(node=kr.KnowledgeNode(id="low", name="Low", confidence=40), score=40),
        kr.RetrievalResult(node=kr.KnowledgeNode(id="old", name="Old", obsolete=True), score=80),
        kr.RetrievalResult(node=kr.KnowledgeNode(id="incomplete", name="Incomplete", complete=False), score=80),
        kr.RetrievalResult(node=kr.KnowledgeNode(id="unsupported", name="Unsupported", supported=False), score=80),
    ]
    filtered = kr.RetrievalFilter().filter((duplicate, keep, *bad), query)
    assert [result.node.id for result in filtered] == ["keep"]
    assert filtered[0].score == 80


def test_obsolete_exclusion_can_be_overridden_by_query():
    old = kr.RetrievalResult(node=kr.KnowledgeNode(id="old", name="Old", obsolete=True), score=80)
    excluded = kr.RetrievalFilter().filter((old,), kr.RetrievalQuery(text="old"))
    included = kr.RetrievalFilter().filter((old,), kr.RetrievalQuery(text="old", include_obsolete=True))
    assert excluded == ()
    assert included == (old,)


def test_duplicate_merge_keeps_highest_scored_result():
    low = kr.RetrievalResult(node=kr.KnowledgeNode(id="same", name="Same"), score=20)
    high = kr.RetrievalResult(node=kr.KnowledgeNode(id="same", name="Same"), score=90)
    filtered = kr.RetrievalFilter().filter((low, high), kr.RetrievalQuery(text="same"))
    assert filtered == (high,)
