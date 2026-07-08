from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import ProvenanceEdge, ProvenanceNode


class EdgeFactory:
    RELATIONSHIPS = (
        ("generated_from", "Knowledge was generated from research foundations."),
        ("supported_by", "Evidence supports the knowledge context."),
        ("derived_from", "Decision state is derived from evidence."),
        ("generated_from", "Alternatives are generated from the decision state."),
        ("evaluated_using", "Evaluation scores each alternative."),
        ("derived_from", "Ranking derives priority order from evaluation."),
        ("scenario_tested", "Simulation tests ranked alternatives."),
        ("optimized_by", "Optimization balances simulated outcomes."),
        ("uncertainty_adjusted", "Uncertainty analysis adjusts confidence."),
        ("scenario_tested", "Scenario analysis compares strategic outcomes."),
        ("learned_from", "Learning captures feedback and patterns."),
        ("planned_by", "Strategic planning converts learning into execution."),
        ("derived_from", "Final decision is derived from the strategic plan."),
    )

    def create_edges(self, nodes: tuple[ProvenanceNode, ...]) -> tuple[ProvenanceEdge, ...]:
        edges: list[ProvenanceEdge] = []
        for index, (source, target) in enumerate(zip(nodes, nodes[1:]), start=1):
            relationship, reason = self.RELATIONSHIPS[index - 1]
            confidence = clamp_confidence((source.confidence + target.confidence) / 2.0)
            weight = clamp_confidence(0.72 + (index * 0.015))
            edges.append(
                ProvenanceEdge(
                    edge_id=f"edge-{index:02d}-{source.node_type}-to-{target.node_type}",
                    source_node=source.node_id,
                    target_node=target.node_id,
                    relationship=relationship,
                    weight=weight,
                    confidence=confidence,
                    reason=reason,
                    metadata={"sequence": index, "confidence_propagation": "weighted_parent_average"},
                )
            )
        return tuple(edges)
