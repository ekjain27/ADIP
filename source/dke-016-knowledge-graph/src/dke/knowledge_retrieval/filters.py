from __future__ import annotations

from typing import Sequence

from .models import RetrievalQuery, RetrievalResult


class RetrievalFilter:
    def filter(self, results: Sequence[RetrievalResult], query: RetrievalQuery) -> Sequence[RetrievalResult]:
        accepted: dict[str, RetrievalResult] = {}
        for result in results:
            node = result.node
            if result.score < query.min_confidence or node.confidence < query.min_confidence:
                continue
            if node.obsolete and not query.include_obsolete:
                continue
            if not node.complete or not node.supported:
                continue
            if any(item.obsolete for item in result.evidence) and not query.include_obsolete:
                continue
            current = accepted.get(node.id)
            if current is None or result.score > current.score:
                accepted[node.id] = result
        return tuple(sorted(accepted.values(), key=lambda item: (-item.score, item.node.id))[: query.max_results])
