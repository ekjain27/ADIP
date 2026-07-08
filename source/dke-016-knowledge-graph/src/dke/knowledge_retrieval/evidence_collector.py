from __future__ import annotations

from typing import Sequence

from .interfaces import KnowledgeStore
from .models import EvidenceItem


class EvidenceCollector:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    def collect(self, node_ids: Sequence[str], relationship_ids: Sequence[str] = ()) -> Sequence[EvidenceItem]:
        evidence: dict[str, EvidenceItem] = {}
        for node_id in node_ids:
            for item in self._store.evidence_for_node(node_id):
                evidence[item.id] = item
        for relationship_id in relationship_ids:
            for item in self._store.evidence_for_relationship(relationship_id):
                evidence[item.id] = item
        return tuple(sorted(evidence.values(), key=lambda item: item.id))
