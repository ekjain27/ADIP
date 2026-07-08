from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol, Sequence

from .models import EvidenceItem, KnowledgeNode, KnowledgeRelationship


class DKE016KnowledgeGraphReader(Protocol):
    def getNodeById(self, node_id: str) -> Any | None: ...
    def getNodeByCanonicalName(self, canonical_name: str) -> Any | None: ...
    def getEdgesBySourceNode(self, source_node_id: str) -> Sequence[Any]: ...
    def getEdgesByTargetNode(self, target_node_id: str) -> Sequence[Any]: ...


class DKE016KnowledgeGraphAdapter:
    def __init__(self, graph: Any) -> None:
        self._graph = graph

    def all_nodes(self) -> Sequence[KnowledgeNode]:
        raw_nodes = self._call_first(("all_nodes", "list_nodes", "getAllNodes", "nodes"), default=())
        return tuple(sorted((self._map_node(node) for node in self._iter(raw_nodes)), key=lambda node: node.id))

    def all_relationships(self) -> Sequence[KnowledgeRelationship]:
        raw_relationships = self._call_first(("all_relationships", "list_edges", "getAllEdges", "edges", "relationships"), default=())
        return tuple(sorted((self._map_relationship(edge) for edge in self._iter(raw_relationships)), key=lambda edge: edge.id))

    def all_evidence(self) -> Sequence[EvidenceItem]:
        raw_evidence = self._call_first(("all_evidence", "list_evidence", "getAllEvidence", "evidence"), default=())
        return tuple(sorted((self._map_evidence(item) for item in self._iter(raw_evidence)), key=lambda item: item.id))

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        raw = self._call_first(("get_node", "getNodeById"), node_id, default=None)
        if raw is not None:
            return self._map_node(raw)
        for node in self.all_nodes():
            if node.id == node_id:
                return node
        return None

    def find_node_by_name(self, name: str) -> KnowledgeNode | None:
        raw = self._call_first(("find_node_by_name", "getNodeByCanonicalName"), name, default=None)
        if raw is not None:
            return self._map_node(raw)
        normalized = name.lower()
        for node in self.all_nodes():
            if normalized in {node.name.lower(), *(alias.lower() for alias in node.aliases)}:
                return node
        return None

    def relationships_for_node(self, node_id: str) -> Sequence[KnowledgeRelationship]:
        source_edges = self._call_first(("get_edges_by_source_node", "getEdgesBySourceNode"), node_id, default=())
        target_edges = self._call_first(("get_edges_by_target_node", "getEdgesByTargetNode"), node_id, default=())
        edges = {edge.id: edge for edge in (self._map_relationship(raw) for raw in (*self._iter(source_edges), *self._iter(target_edges)))}
        if edges:
            return tuple(sorted(edges.values(), key=lambda edge: edge.id))
        return tuple(edge for edge in self.all_relationships() if edge.source_id == node_id or edge.target_id == node_id)

    def evidence_for_node(self, node_id: str) -> Sequence[EvidenceItem]:
        raw = self._call_first(("get_evidence_by_node", "getEvidenceByNodeId", "evidenceForNode"), node_id, default=None)
        if raw is not None:
            return tuple(sorted((self._map_evidence(item, node_id=node_id) for item in self._iter(raw)), key=lambda item: item.id))
        return tuple(sorted((item for item in self.all_evidence() if item.node_id == node_id), key=lambda item: item.id))

    def evidence_for_relationship(self, relationship_id: str) -> Sequence[EvidenceItem]:
        raw = self._call_first(("get_evidence_by_relationship", "getEvidenceByRelationshipId", "evidenceForRelationship"), relationship_id, default=None)
        if raw is not None:
            return tuple(
                sorted((self._map_evidence(item, relationship_id=relationship_id) for item in self._iter(raw)), key=lambda item: item.id)
            )
        relationship = next((edge for edge in self.all_relationships() if edge.id == relationship_id), None)
        evidence_ids = set(relationship.evidence_ids if relationship is not None else ())
        return tuple(
            sorted(
                (item for item in self.all_evidence() if item.relationship_id == relationship_id or item.id in evidence_ids),
                key=lambda item: item.id,
            )
        )

    def _call_first(self, names: Sequence[str], *args: Any, default: Any) -> Any:
        for name in names:
            if not hasattr(self._graph, name):
                continue
            value = getattr(self._graph, name)
            return value(*args) if callable(value) else value
        return default

    def _map_node(self, raw: Any) -> KnowledgeNode:
        facts = dict(self._get(raw, "attributes", "properties", "facts", default={}) or {})
        metadata = dict(self._get(raw, "metadata", default={}) or {})
        source_ids = tuple(self._get(raw, "sourceIds", "source_ids", default=()) or ())
        if source_ids:
            metadata["source_ids"] = source_ids
        return KnowledgeNode(
            id=str(self._get(raw, "id")),
            name=str(self._get(raw, "canonicalName", "canonical_name", "name")),
            type=str(self._get(raw, "type", default="unknown")),
            aliases=tuple(self._get(raw, "aliases", "labels", default=()) or ()),
            facts=facts,
            confidence=self._score(self._get(raw, "confidence", default=100.0)),
            metadata=metadata,
        )

    def _map_relationship(self, raw: Any) -> KnowledgeRelationship:
        return KnowledgeRelationship(
            id=str(self._get(raw, "id")),
            source_id=str(self._get(raw, "sourceNodeId", "source_node_id", "source_id")),
            target_id=str(self._get(raw, "targetNodeId", "target_node_id", "target_id")),
            relationship_type=str(self._get(raw, "relationType", "relationship_type", "type", default="related_to")),
            confidence=self._score(self._get(raw, "confidence", default=100.0)),
            weight=float(self._get(raw, "weight", default=1.0)),
            evidence_ids=tuple(self._get(raw, "evidenceIds", "evidence_ids", default=()) or ()),
            metadata=dict(self._get(raw, "metadata", default={}) or {}),
        )

    def _map_evidence(self, raw: Any, node_id: str | None = None, relationship_id: str | None = None) -> EvidenceItem:
        mapped_node_id = self._get(raw, "nodeId", "node_id", default=node_id)
        mapped_relationship_id = self._get(raw, "relationshipId", "relationship_id", "edgeId", "edge_id", default=relationship_id)
        return EvidenceItem(
            id=str(self._get(raw, "id")),
            node_id=str(mapped_node_id) if mapped_node_id else None,
            relationship_id=str(mapped_relationship_id) if mapped_relationship_id else None,
            evidence_type=str(self._get(raw, "sourceType", "evidence_type", "type", default="unknown")),
            source=str(self._get(raw, "sourceId", "source", default="")),
            excerpt=str(self._get(raw, "excerpt", default="")),
            confidence=self._score(self._get(raw, "confidence", default=100.0)),
            metadata=dict(self._get(raw, "metadata", default={}) or {}),
        )

    def _get(self, raw: Any, *names: str, default: Any = None) -> Any:
        for name in names:
            if isinstance(raw, dict) and name in raw:
                return raw[name]
            if hasattr(raw, name):
                return getattr(raw, name)
        return default

    def _iter(self, value: Any) -> tuple[Any, ...]:
        if value is None:
            return ()
        if isinstance(value, dict):
            return tuple(value.values())
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            return tuple(value)
        return (value,)

    def _score(self, value: Any) -> float:
        score = float(value)
        return score * 100 if 0 <= score <= 1 else score
