from __future__ import annotations

from typing import Sequence

from .interfaces import KnowledgeStore
from .models import KnowledgeNode, KnowledgeRelationship, RetrievalResult, clamp_score
from .traversal import GraphTraversal


class InMemoryGraphSearch:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store
        self._traversal = GraphTraversal(store)

    def search(self, entities: Sequence[str], max_depth: int) -> Sequence[RetrievalResult]:
        results: dict[str, RetrievalResult] = {}
        for entity in entities:
            root = self._store.find_node_by_name(entity)
            if root is None:
                continue
            nodes, relationships = self._traversal.subgraph(root.id, max_depth)
            connectivity = min(100.0, len(relationships) * 20.0)
            rels_by_node = {
                node.id: tuple(rel for rel in relationships if rel.source_id == node.id or rel.target_id == node.id)
                for node in nodes
            }
            for node in nodes:
                distance_bonus = 100.0 if node.id == root.id else 70.0
                score = clamp_score((distance_bonus * 0.6) + (connectivity * 0.4))
                current = results.get(node.id)
                if current is None or score > current.score:
                    results[node.id] = RetrievalResult(
                        node=node,
                        score=score,
                        confidence=node.confidence,
                        authority=node.authority,
                        freshness=node.freshness,
                        connectivity=connectivity,
                        usage_frequency=node.usage_frequency,
                        relationships=rels_by_node[node.id],
                    )
        return tuple(sorted(results.values(), key=lambda result: (-result.score, result.node.id)))

    def related(self, node_id: str, max_depth: int = 1) -> Sequence[KnowledgeNode]:
        return self._traversal.related_nodes(node_id, max_depth)

    def subgraph(self, node_id: str, max_depth: int = 1) -> tuple[Sequence[KnowledgeNode], Sequence[KnowledgeRelationship]]:
        return self._traversal.subgraph(node_id, max_depth)
