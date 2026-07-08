from __future__ import annotations

from .models import DecisionProvenance, DecisionProvenanceGraph


class GraphValidator:
    def validate_graph(self, graph: DecisionProvenanceGraph) -> None:
        node_ids = tuple(node.node_id for node in graph.nodes)
        edge_ids = tuple(edge.edge_id for edge in graph.edges)
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("provenance graph contains duplicate nodes")
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("provenance graph contains duplicate edges")
        if graph.root_node not in node_ids:
            raise ValueError("provenance graph root node is missing")
        if graph.terminal_node not in node_ids:
            raise ValueError("provenance graph terminal node is missing")
        for node in graph.nodes:
            self._validate_unit(node.confidence, f"node confidence {node.node_id}")
        for edge in graph.edges:
            if edge.source_node not in node_ids or edge.target_node not in node_ids:
                raise ValueError("provenance graph contains an edge with missing node reference")
            self._validate_unit(edge.confidence, f"edge confidence {edge.edge_id}")
            self._validate_unit(edge.weight, f"edge weight {edge.edge_id}")
        if self.has_cycle(graph):
            raise ValueError("provenance graph contains a cycle")
        if not self.is_connected(graph):
            raise ValueError("provenance graph is disconnected")
        self._validate_single_root_terminal(graph)

    def validate_provenance(self, provenance: DecisionProvenance) -> None:
        if not provenance.alternative_id.strip():
            raise ValueError("DecisionProvenance.alternative_id is required")
        self.validate_graph(provenance.graph)
        self._validate_unit(provenance.traceability_score, "traceability score")
        if provenance.lineage.alternative_id != provenance.alternative_id:
            raise ValueError("lineage alternative_id must match provenance alternative_id")

    def has_cycle(self, graph: DecisionProvenanceGraph) -> bool:
        adjacency = self._adjacency(graph)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> bool:
            if node in visiting:
                return True
            if node in visited:
                return False
            visiting.add(node)
            for child in adjacency.get(node, ()):
                if visit(child):
                    return True
            visiting.remove(node)
            visited.add(node)
            return False

        return any(visit(node.node_id) for node in graph.nodes)

    def is_connected(self, graph: DecisionProvenanceGraph) -> bool:
        undirected: dict[str, set[str]] = {node.node_id: set() for node in graph.nodes}
        for edge in graph.edges:
            undirected.setdefault(edge.source_node, set()).add(edge.target_node)
            undirected.setdefault(edge.target_node, set()).add(edge.source_node)
        seen: set[str] = set()
        stack = [graph.root_node]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(sorted(undirected.get(current, set()) - seen))
        return len(seen) == len(graph.nodes)

    def _validate_single_root_terminal(self, graph: DecisionProvenanceGraph) -> None:
        targets = {edge.target_node for edge in graph.edges}
        sources = {edge.source_node for edge in graph.edges}
        roots = [node.node_id for node in graph.nodes if node.node_id not in targets]
        terminals = [node.node_id for node in graph.nodes if node.node_id not in sources]
        if roots != [graph.root_node]:
            raise ValueError("provenance graph must have a single root")
        if terminals != [graph.terminal_node]:
            raise ValueError("provenance graph must have a single terminal node")

    def _adjacency(self, graph: DecisionProvenanceGraph) -> dict[str, tuple[str, ...]]:
        adjacency: dict[str, list[str]] = {node.node_id: [] for node in graph.nodes}
        for edge in graph.edges:
            adjacency.setdefault(edge.source_node, []).append(edge.target_node)
        return {node: tuple(children) for node, children in adjacency.items()}

    def _validate_unit(self, value: float, field_name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field_name} must be between 0 and 1")


