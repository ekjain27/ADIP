from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ProvenanceNode:
    node_id: str
    node_type: str
    title: str
    description: str
    source_module: str
    confidence: float
    timestamp: str
    parent_nodes: tuple[str, ...] = ()
    child_nodes: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProvenanceEdge:
    edge_id: str
    source_node: str
    target_node: str
    relationship: str
    weight: float
    confidence: float
    reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionLineage:
    alternative_id: str
    ordered_nodes: tuple[str, ...]
    ordered_edges: tuple[str, ...]
    summary: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionProvenanceGraph:
    nodes: tuple[ProvenanceNode, ...]
    edges: tuple[ProvenanceEdge, ...]
    root_node: str
    terminal_node: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionProvenance:
    alternative_id: str
    graph: DecisionProvenanceGraph
    lineage: DecisionLineage
    traceability_score: float
    audit_summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionProvenancePackage:
    provenance_results: tuple[DecisionProvenance, ...]
    selected_provenance: DecisionProvenance | None
    graph_statistics: Mapping[str, Any]
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
