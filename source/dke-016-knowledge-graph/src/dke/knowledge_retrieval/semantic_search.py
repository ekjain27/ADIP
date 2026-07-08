from __future__ import annotations

import re
from collections import Counter
from math import sqrt
from typing import Sequence

from .interfaces import KnowledgeStore
from .models import KnowledgeNode, RetrievalQuery, RetrievalResult, clamp_score

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(TOKEN_RE.findall(text.lower()))


def cosine_similarity(left: Sequence[str], right: Sequence[str]) -> float:
    if not left or not right:
        return 0.0
    a = Counter(left)
    b = Counter(right)
    common = set(a) & set(b)
    numerator = sum(a[token] * b[token] for token in common)
    left_norm = sqrt(sum(value * value for value in a.values()))
    right_norm = sqrt(sum(value * value for value in b.values()))
    return 0.0 if left_norm == 0 or right_norm == 0 else numerator / (left_norm * right_norm)


class InMemorySemanticSearch:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    def search(self, query: RetrievalQuery, entities: Sequence[str]) -> Sequence[RetrievalResult]:
        query_terms = tokenize(" ".join((query.text, *entities)))
        results: list[RetrievalResult] = []
        for node in self._store.all_nodes():
            similarity = self._score_node(node, query_terms, entities)
            if similarity > 0:
                results.append(
                    RetrievalResult(
                        node=node,
                        score=clamp_score(similarity),
                        similarity=clamp_score(similarity),
                        confidence=node.confidence,
                        authority=node.authority,
                        freshness=node.freshness,
                        usage_frequency=node.usage_frequency,
                    )
                )
        return sorted(results, key=lambda result: (-result.similarity, result.node.id))

    def _score_node(self, node: KnowledgeNode, query_terms: Sequence[str], entities: Sequence[str]) -> float:
        searchable = " ".join(
            [
                node.name,
                *node.aliases,
                node.type,
                " ".join(str(value) for value in node.facts.values()),
            ]
        )
        score = cosine_similarity(query_terms, tokenize(searchable)) * 100
        lowered_names = {node.name.lower(), *(alias.lower() for alias in node.aliases)}
        if any(entity.lower() in lowered_names for entity in entities):
            score = max(score, 100.0)
        return clamp_score(score)
