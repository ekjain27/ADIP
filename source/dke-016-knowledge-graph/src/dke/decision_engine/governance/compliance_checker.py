from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.provenance import DecisionProvenance

from .models import GovernancePolicy


class ComplianceChecker:
    def check(self, provenance: DecisionProvenance, policy: GovernancePolicy) -> dict:
        traceability = clamp_confidence(provenance.traceability_score)
        lineage_confidence = clamp_confidence(provenance.lineage.confidence)
        category = policy.category.lower()
        violations: list[str] = []
        recommendations: list[str] = []
        score = (traceability * 0.55) + (lineage_confidence * 0.45)
        if category == "risk":
            score = min(score, self._risk_score(provenance))
        elif category == "compliance":
            score = (score * 0.65) + (self._graph_integrity_score(provenance) * 0.35)
        elif category == "ethics":
            score = (score * 0.80) + (self._transparency_signal(provenance) * 0.20)
        elif category == "security":
            score = (score * 0.85) + (0.10 if provenance.graph.terminal_node else 0.0)
        elif category == "operational":
            score = (score * 0.75) + (self._planning_signal(provenance) * 0.25)
        else:
            score = (score * 0.85) + (0.10 if provenance.alternative_id else 0.0)
        score = clamp_confidence(score)
        if score < 0.60:
            violations.append(f"{policy.name} score below minimum governance threshold.")
            recommendations.append(f"Escalate {policy.category} review before approval.")
        elif score < 0.75:
            recommendations.append(f"Monitor {policy.category} controls during execution.")
        else:
            recommendations.append(f"{policy.category} controls satisfy governance requirements.")
        return {
            "score": score,
            "status": "violation" if violations else "pass",
            "violations": tuple(violations),
            "recommendations": tuple(recommendations),
        }

    def _risk_score(self, provenance: DecisionProvenance) -> float:
        risk_mentions = provenance.audit_summary.lower().count("risk")
        return clamp_confidence(provenance.traceability_score - (risk_mentions * 0.03) + 0.08)

    def _graph_integrity_score(self, provenance: DecisionProvenance) -> float:
        node_count = len(provenance.graph.nodes)
        edge_count = len(provenance.graph.edges)
        expected = max(0, node_count - 1)
        return clamp_confidence(1.0 - abs(expected - edge_count) * 0.08)

    def _transparency_signal(self, provenance: DecisionProvenance) -> float:
        return clamp_confidence(0.65 + (0.20 if provenance.lineage.ordered_nodes else 0.0) + (0.10 if provenance.audit_summary else 0.0))

    def _planning_signal(self, provenance: DecisionProvenance) -> float:
        has_plan = any(node.node_type == "strategic_plan" for node in provenance.graph.nodes)
        return 0.85 if has_plan else 0.45
