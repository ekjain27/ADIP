from __future__ import annotations

from dataclasses import replace

from decision_engine.core.models import clamp_confidence
from decision_engine.temporal import TemporalDecision

from .adaptation_rule_engine import AdaptationRuleEngine
from .models import AdaptiveBehaviorProfile, BehaviorAdjustment
from .objective_priority_adapter import ObjectivePriorityAdapter
from .risk_tolerance_adapter import RiskToleranceAdapter
from .threshold_adapter import ThresholdAdapter


class AdaptiveBehaviorModel:
    def __init__(
        self,
        threshold_adapter: ThresholdAdapter | None = None,
        risk_tolerance_adapter: RiskToleranceAdapter | None = None,
        objective_priority_adapter: ObjectivePriorityAdapter | None = None,
        rule_engine: AdaptationRuleEngine | None = None,
    ) -> None:
        self.threshold_adapter = threshold_adapter or ThresholdAdapter()
        self.risk_tolerance_adapter = risk_tolerance_adapter or RiskToleranceAdapter()
        self.objective_priority_adapter = objective_priority_adapter or ObjectivePriorityAdapter()
        self.rule_engine = rule_engine or AdaptationRuleEngine()

    def default_profile(self, profile_id: str = "adaptive-default") -> AdaptiveBehaviorProfile:
        return AdaptiveBehaviorProfile(
            profile_id=profile_id,
            confidence_threshold=0.70,
            risk_tolerance=0.50,
            governance_sensitivity=0.70,
            objective_priorities=self.objective_priority_adapter.default_priorities(),
            checkpoint_frequency="medium",
            recommendation_mode="balanced",
            adjustments=(),
            metadata={"model": "Adaptive Decision Behavior Model"},
        )

    def adapt_profile(self, temporal_decision: TemporalDecision) -> AdaptiveBehaviorProfile:
        profile = self.default_profile(f"profile-{temporal_decision.alternative_id}")
        adjustments: list[BehaviorAdjustment] = []
        status = str(temporal_decision.metadata.get("governance_status", "approved"))
        threshold, adjustment = self.threshold_adapter.adjust(profile.confidence_threshold, temporal_decision.stability_score, temporal_decision.stability_score)
        if adjustment:
            adjustments.append(adjustment)
        risk_tolerance, adjustment = self.risk_tolerance_adapter.adjust(profile.risk_tolerance, temporal_decision.stability_score, status, temporal_decision.change_frequency)
        if adjustment:
            adjustments.append(adjustment)
        priorities, adjustment = self.objective_priority_adapter.adjust(dict(profile.objective_priorities), status, temporal_decision.stability_score)
        if adjustment:
            adjustments.append(adjustment)
        governance_sensitivity = profile.governance_sensitivity
        if temporal_decision.stability_score < 0.65 or status in {"conditional", "rejected"}:
            previous = governance_sensitivity
            governance_sensitivity = clamp_confidence(governance_sensitivity + 0.10)
            adjustments.append(BehaviorAdjustment("adj-governance-sensitivity", "governance_sensitivity", previous, governance_sensitivity, "Governance sensitivity increased due to instability or governance concern.", temporal_decision.stability_score))
        checkpoint_frequency = "high" if temporal_decision.change_frequency > 0.45 else profile.checkpoint_frequency
        if checkpoint_frequency != profile.checkpoint_frequency:
            adjustments.append(BehaviorAdjustment("adj-checkpoint-frequency", "checkpoint_frequency", profile.checkpoint_frequency, checkpoint_frequency, "Checkpoint frequency increased due to high change frequency.", clamp_confidence(1.0 - temporal_decision.change_frequency)))
        recommendation_mode = "conservative" if status in {"conditional", "rejected"} else ("confident" if temporal_decision.stability_score >= 0.80 else profile.recommendation_mode)
        if recommendation_mode != profile.recommendation_mode:
            adjustments.append(BehaviorAdjustment("adj-recommendation-mode", "recommendation_mode", profile.recommendation_mode, recommendation_mode, "Recommendation mode adapted from governance status and lineage stability.", temporal_decision.stability_score))
        return replace(
            profile,
            confidence_threshold=threshold,
            risk_tolerance=risk_tolerance,
            governance_sensitivity=governance_sensitivity,
            objective_priorities=priorities,
            checkpoint_frequency=checkpoint_frequency,
            recommendation_mode=recommendation_mode,
            adjustments=tuple(adjustments),
        )
