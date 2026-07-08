import time

import knowledge_retrieval as kr


def test_cache_returns_values_and_expires():
    cache = kr.RetrievalCache[str](ttl_seconds=0.01)
    cache.set("query", "context")
    assert cache.get("query") == "context"
    time.sleep(0.02)
    assert cache.get("query") is None
    assert len(cache) == 0
