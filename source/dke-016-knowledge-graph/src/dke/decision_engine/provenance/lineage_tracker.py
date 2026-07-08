from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import DecisionLineage, DecisionProvenanceGraph


class LineageTracker:
    def track(self, alternative_id: str, graph: DecisionProvenanceGraph) -> DecisionLineage:
        ordered_nodes = self._ordered_nodes(graph)
        edge_by_path = {(edge.source_node, edge.target_node): edge.edge_id for edge in graph.edges}
        ordered_edges = tuple(
            edge_by_path[(source, target)]
            for source, target in zip(ordered_nodes, ordered_nodes[1:])
            if (source, target) in edge_by_path
        )
        node_confidences = {node.node_id: node.confidence for node in graph.nodes}
        confidence = clamp_confidence(sum(node_confidences[node] for node in ordered_nodes) / len(ordered_nodes)) if ordered_nodes else 0.0
        summary = f"Lineage for {alternative_id} traces {len(ordered_nodes)} nodes and {len(ordered_edges)} edges from research to final decision."
        return DecisionLineage(
            alternative_id=alternative_id,
            ordered_nodes=ordered_nodes,
            ordered_edges=ordered_edges,
            summary=summary,
            confidence=confidence,
            metadata={"root_node": graph.root_node, "terminal_node": graph.terminal_node},
        )

    def _ordered_nodes(self, graph: DecisionProvenanceGraph) -> tuple[str, ...]:
        adjacency: dict[str, list[str]] = {node.node_id: [] for node in graph.nodes}
        for edge in graph.edges:
            adjacency.setdefault(edge.source_node, []).append(edge.target_node)
        ordered: list[str] = []
        current = graph.root_node
        seen: set[str] = set()
        while current and current not in seen:
            ordered.append(current)
            seen.add(current)
            children = sorted(adjacency.get(current, ()))
            current = children[0] if children else ""
        return tuple(ordered)
