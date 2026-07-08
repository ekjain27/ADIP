from __future__ import annotations

from decision_engine.temporal import TemporalDecision

from .models import AdaptiveRule


class AdaptationRuleEngine:
    DEFAULT_RULES = (
        ("rule-low-stability-governance", "Low stability increases governance sensitivity", "stability_score < 0.65", "increase_governance_sensitivity", "critical"),
        ("rule-high-change-checkpoints", "High change frequency increases checkpoint frequency", "change_frequency > 0.45", "increase_checkpoint_frequency", "high"),
        ("rule-low-confidence-threshold", "Low confidence increases confidence threshold", "confidence < threshold", "increase_confidence_threshold", "high"),
        ("rule-high-risk-tolerance", "High risk lowers risk tolerance", "governance_status != approved", "lower_risk_tolerance", "high"),
        ("rule-stable-lineage-confidence", "Stable lineage increases recommendation confidence", "stability_score >= 0.80", "increase_recommendation_confidence", "medium"),
        ("rule-governance-conservative", "Governance concern switches recommendation mode to conservative", "governance_status in conditional/rejected", "set_conservative_mode", "critical"),
    )

    def default_rules(self) -> tuple[AdaptiveRule, ...]:
        return tuple(
            AdaptiveRule(rule_id, name, trigger, action, priority, True, {"source": "ADBM"})
            for rule_id, name, trigger, action, priority in self.DEFAULT_RULES
        )

    def applicable_rules(self, temporal_decision: TemporalDecision, rules: tuple[AdaptiveRule, ...] | None = None) -> tuple[AdaptiveRule, ...]:
        active_rules = tuple(rule for rule in (rules or self.default_rules()) if rule.enabled)
        status = str(temporal_decision.metadata.get("governance_status", "approved"))
        confidence = self._confidence(temporal_decision)
        applicable: list[AdaptiveRule] = []
        for rule in active_rules:
            if rule.action == "increase_governance_sensitivity" and temporal_decision.stability_score < 0.65:
                applicable.append(rule)
            elif rule.action == "increase_checkpoint_frequency" and temporal_decision.change_frequency > 0.45:
                applicable.append(rule)
            elif rule.action == "increase_confidence_threshold" and confidence < 0.70:
                applicable.append(rule)
            elif rule.action == "lower_risk_tolerance" and status != "approved":
                applicable.append(rule)
            elif rule.action == "increase_recommendation_confidence" and temporal_decision.stability_score >= 0.80:
                applicable.append(rule)
            elif rule.action == "set_conservative_mode" and status in {"conditional", "rejected"}:
                applicable.append(rule)
        return tuple(applicable)

    def _confidence(self, temporal_decision: TemporalDecision) -> float:
        return temporal_decision.stability_score
