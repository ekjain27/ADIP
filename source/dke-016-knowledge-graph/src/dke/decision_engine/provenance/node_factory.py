from __future__ import annotations

from decision_engine.core.models import clamp_confidence, utc_now
from decision_engine.strategic_planning import StrategicPlan

from .models import ProvenanceNode


class NodeFactory:
    STAGES = (
        ("research", "Research", "R-001:R-010", 0.78),
        ("knowledge", "Knowledge", "DKE-001:DKE-020", 0.80),
        ("evidence", "Evidence", "DKE-016", 0.82),
        ("decision_state", "Decision State", "DIE-001", 0.84),
        ("alternative", "Alternative", "DIE-002", 0.84),
        ("evaluation", "Evaluation", "DIE-003", 0.85),
        ("ranking", "Ranking", "DIE-004", 0.86),
        ("simulation", "Simulation", "DIE-005", 0.84),
        ("optimization", "Optimization", "DIE-007:DIE-011", 0.86),
        ("uncertainty", "Uncertainty", "DIE-008", 0.82),
        ("scenario", "Scenario Analysis", "DIE-009", 0.83),
        ("learning", "Learning", "DIE-010", 0.84),
        ("strategic_plan", "Strategic Plan", "DIE-012", 0.88),
        ("decision", "Final Decision", "DIE-013", 0.90),
    )

    def create_nodes(self, plan: StrategicPlan) -> tuple[ProvenanceNode, ...]:
        timestamp = utc_now().isoformat()
        plan_confidence = clamp_confidence(float(plan.planning_graph.metadata.get("balance_score", 0.75)))
        nodes: list[ProvenanceNode] = []
        for index, (node_type, title, source_module, base_confidence) in enumerate(self.STAGES):
            confidence = clamp_confidence((base_confidence * 0.65) + (plan_confidence * 0.35))
            nodes.append(
                ProvenanceNode(
                    node_id=f"prov-{self._clean(plan.alternative_id)}-{index + 1:02d}-{node_type}",
                    node_type=node_type,
                    title=title,
                    description=self._description(title, plan),
                    source_module=source_module,
                    confidence=confidence,
                    timestamp=timestamp,
                    metadata={
                        "origin": source_module,
                        "alternative_id": plan.alternative_id,
                        "sequence": index + 1,
                    },
                )
            )
        return tuple(nodes)

    def _description(self, title: str, plan: StrategicPlan) -> str:
        if title == "Strategic Plan":
            return plan.execution_summary
        if title == "Final Decision":
            return f"Terminal decision provenance for {plan.alternative_id}."
        return f"{title} contribution to the decision path for {plan.alternative_id}."

    def _clean(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("_", "-")
