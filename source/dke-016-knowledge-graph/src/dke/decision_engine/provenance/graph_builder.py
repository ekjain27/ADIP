from __future__ import annotations

from dataclasses import replace

from decision_engine.strategic_planning import StrategicPlan

from .confidence_propagator import ConfidencePropagator
from .edge_factory import EdgeFactory
from .graph_validator import GraphValidator
from .models import DecisionProvenanceGraph, ProvenanceEdge, ProvenanceNode
from .node_factory import NodeFactory


class GraphBuilder:
    def __init__(
        self,
        node_factory: NodeFactory | None = None,
        edge_factory: EdgeFactory | None = None,
        confidence_propagator: ConfidencePropagator | None = None,
        validator: GraphValidator | None = None,
    ) -> None:
        self.node_factory = node_factory or NodeFactory()
        self.edge_factory = edge_factory or EdgeFactory()
        self.confidence_propagator = confidence_propagator or ConfidencePropagator()
        self.validator = validator or GraphValidator()

    def build(self, plan: StrategicPlan) -> DecisionProvenanceGraph:
        nodes = self.node_factory.create_nodes(plan)
        edges = self.edge_factory.create_edges(nodes)
        nodes = self.confidence_propagator.propagate(nodes, edges)
        nodes = self._attach_references(nodes, edges)
        graph = DecisionProvenanceGraph(
            nodes=nodes,
            edges=edges,
            root_node=nodes[0].node_id if nodes else "",
            terminal_node=nodes[-1].node_id if nodes else "",
            metadata={
                "alternative_id": plan.alternative_id,
                "graph_type": "Decision Provenance Graph",
                "dag": True,
            },
        )
        self.validator.validate_graph(graph)
        return graph

    def _attach_references(
        self,
        nodes: tuple[ProvenanceNode, ...],
        edges: tuple[ProvenanceEdge, ...],
    ) -> tuple[ProvenanceNode, ...]:
        parents: dict[str, list[str]] = {node.node_id: [] for node in nodes}
        children: dict[str, list[str]] = {node.node_id: [] for node in nodes}
        for edge in edges:
            parents.setdefault(edge.target_node, []).append(edge.source_node)
            children.setdefault(edge.source_node, []).append(edge.target_node)
        return tuple(
            replace(node, parent_nodes=tuple(parents[node.node_id]), child_nodes=tuple(children[node.node_id]))
            for node in nodes
        )
