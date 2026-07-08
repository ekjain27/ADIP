from __future__ import annotations

import logging

from decision_engine.core.models import clamp_confidence
from decision_engine.temporal import TemporalDecision, TemporalDecisionPackage

from .adaptation_rule_engine import AdaptationRuleEngine
from .adaptive_package import AdaptivePackageBuilder
from .behavior_model import AdaptiveBehaviorModel
from .models import AdaptiveDecision

logger = logging.getLogger(__name__)


class AdaptiveDecisionEngine:
    STRATEGY = "deterministic_adaptive_decision_behavior_model"

    def __init__(
        self,
        behavior_model: AdaptiveBehaviorModel | None = None,
        rule_engine: AdaptationRuleEngine | None = None,
        package_builder: AdaptivePackageBuilder | None = None,
    ) -> None:
        self.rule_engine = rule_engine or AdaptationRuleEngine()
        self.behavior_model = behavior_model or AdaptiveBehaviorModel(rule_engine=self.rule_engine)
        self.package_builder = package_builder or AdaptivePackageBuilder()

    def adapt(self, temporal_package: TemporalDecisionPackage):
        if not isinstance(temporal_package, TemporalDecisionPackage):
            raise ValueError("AdaptiveDecisionEngine.adapt requires a TemporalDecisionPackage")
        logger.info("Running deterministic adaptive decision behavior modeling")
        results = tuple(self._adapt_decision(result) for result in temporal_package.temporal_results)
        selected = self._selected_result(results, temporal_package.selected_result)
        return self.package_builder.build(
            results,
            selected,
            adaptation_strategy=self.STRATEGY,
            metadata={
                "source_module": temporal_package.metadata.get("module", "DIE-015"),
                "temporal_result_count": len(temporal_package.temporal_results),
            },
        )

    def _adapt_decision(self, temporal_decision: TemporalDecision) -> AdaptiveDecision:
        profile = self.behavior_model.adapt_profile(temporal_decision)
        rules = self.rule_engine.applicable_rules(temporal_decision)
        adaptation_score = self._adaptation_score(temporal_decision, profile, rules)
        confidence = clamp_confidence((temporal_decision.stability_score * 0.55) + (adaptation_score * 0.45))
        return AdaptiveDecision(
            alternative_id=temporal_decision.alternative_id,
            behavior_profile=profile,
            applied_rules=rules,
            adaptation_summary=(
                f"Applied {len(rules)} adaptive rule(s) and {len(profile.adjustments)} behavior adjustment(s) "
                f"for {temporal_decision.alternative_id}."
            ),
            adaptation_score=adaptation_score,
            confidence=confidence,
            metadata={"source_active_version": temporal_decision.ledger.active_version},
        )

    def _selected_result(self, results: tuple[AdaptiveDecision, ...], selected_temporal: TemporalDecision | None) -> AdaptiveDecision | None:
        if not results:
            return None
        if selected_temporal is not None:
            for result in results:
                if result.alternative_id == selected_temporal.alternative_id:
                    return result
        return max(results, key=lambda result: (result.adaptation_score, result.confidence, result.alternative_id))

    def _adaptation_score(self, temporal_decision: TemporalDecision, profile, rules) -> float:
        adjustment_signal = min(1.0, len(profile.adjustments) / 6.0)
        rule_signal = min(1.0, len(rules) / 6.0)
        threshold_fit = 1.0 - abs(profile.confidence_threshold - temporal_decision.stability_score)
        score = (temporal_decision.stability_score * 0.35) + (threshold_fit * 0.25) + (adjustment_signal * 0.20) + (rule_signal * 0.20)
        return clamp_confidence(score)
