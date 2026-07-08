from __future__ import annotations

from dataclasses import replace

from decision_engine.core.models import clamp_confidence

from .models import ProvenanceEdge, ProvenanceNode


class ConfidencePropagator:
    def propagate(
        self,
        nodes: tuple[ProvenanceNode, ...],
        edges: tuple[ProvenanceEdge, ...],
    ) -> tuple[ProvenanceNode, ...]:
        by_id = {node.node_id: node for node in nodes}
        incoming: dict[str, list[ProvenanceEdge]] = {node.node_id: [] for node in nodes}
        for edge in edges:
            incoming.setdefault(edge.target_node, []).append(edge)
        propagated: dict[str, float] = {}
        ordered: list[ProvenanceNode] = []
        for node in nodes:
            parents = incoming.get(node.node_id, [])
            if not parents:
                propagated[node.node_id] = clamp_confidence(node.confidence)
            else:
                parent_scores = [
                    propagated.get(edge.source_node, by_id[edge.source_node].confidence) * edge.confidence * edge.weight
                    for edge in parents
                ]
                parent_confidence = sum(parent_scores) / len(parent_scores)
                propagated[node.node_id] = clamp_confidence((node.confidence * 0.55) + (parent_confidence * 0.45))
            ordered.append(replace(node, confidence=propagated[node.node_id]))
        return tuple(ordered)
