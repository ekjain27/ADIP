from __future__ import annotations

from collections import deque

from .interfaces import KnowledgeStore
from .models import KnowledgeNode, KnowledgeRelationship


class GraphTraversal:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    def related_nodes(self, node_id: str, max_depth: int = 1) -> tuple[KnowledgeNode, ...]:
        nodes, _ = self.subgraph(node_id, max_depth)
        return tuple(node for node in nodes if node.id != node_id)

    def subgraph(self, node_id: str, max_depth: int = 1) -> tuple[tuple[KnowledgeNode, ...], tuple[KnowledgeRelationship, ...]]:
        if max_depth < 0:
            raise ValueError("max_depth cannot be negative")
        visited_nodes: dict[str, KnowledgeNode] = {}
        visited_relationships: dict[str, KnowledgeRelationship] = {}
        start = self._store.get_node(node_id)
        if start is None:
            return (), ()
        queue: deque[tuple[str, int]] = deque([(node_id, 0)])
        visited_nodes[start.id] = start
        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for relationship in self._store.relationships_for_node(current_id):
                visited_relationships[relationship.id] = relationship
                neighbor_id = relationship.target_id if relationship.source_id == current_id else relationship.source_id
                if neighbor_id in visited_nodes:
                    continue
                neighbor = self._store.get_node(neighbor_id)
                if neighbor is not None:
                    visited_nodes[neighbor.id] = neighbor
                    queue.append((neighbor.id, depth + 1))
        return (
            tuple(sorted(visited_nodes.values(), key=lambda node: node.id)),
            tuple(sorted(visited_relationships.values(), key=lambda relationship: relationship.id)),
        )
