from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.provenance import DecisionProvenance

from .models import EthicsAssessment


class EthicsEvaluator:
    def evaluate(self, provenance: DecisionProvenance) -> EthicsAssessment:
        node_types = {node.node_type for node in provenance.graph.nodes}
        fairness_score = clamp_confidence(0.70 + (0.08 if "evaluation" in node_types else 0.0) + (0.06 if "scenario" in node_types else 0.0))
        transparency_score = clamp_confidence(0.62 + (provenance.traceability_score * 0.28) + (0.08 if provenance.lineage.summary else 0.0))
        accountability_score = clamp_confidence(0.68 + (0.10 if "strategic_plan" in node_types else 0.0) + (0.08 if "decision" in node_types else 0.0))
        bias_risk = clamp_confidence(1.0 - ((fairness_score * 0.45) + (transparency_score * 0.25) + (accountability_score * 0.30)))
        return EthicsAssessment(
            fairness_score=fairness_score,
            transparency_score=transparency_score,
            accountability_score=accountability_score,
            bias_risk=bias_risk,
            explanation=(
                f"Ethics assessment for {provenance.alternative_id} used deterministic fairness, "
                "transparency, accountability, and bias-risk signals from the provenance graph."
            ),
            metadata={"node_type_count": len(node_types)},
        )
