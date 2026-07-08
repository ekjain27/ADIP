from __future__ import annotations

from .models import AdaptiveBehaviorProfile, AdaptiveDecision, AdaptiveDecisionPackage, AdaptiveRule


class AdaptiveValidator:
    def validate_rules(self, rules: tuple[AdaptiveRule, ...]) -> None:
        rule_ids = tuple(rule.rule_id for rule in rules)
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("adaptive rule IDs must be unique")
        for rule in rules:
            if not rule.rule_id.strip() or not rule.name.strip():
                raise ValueError("adaptive rule id and name are required")

    def validate_profile(self, profile: AdaptiveBehaviorProfile) -> None:
        self._validate_unit(profile.confidence_threshold, "confidence threshold")
        self._validate_unit(profile.risk_tolerance, "risk tolerance")
        self._validate_unit(profile.governance_sensitivity, "governance sensitivity")
        total = sum(profile.objective_priorities.values())
        if abs(total - 1.0) > 0.00001:
            raise ValueError(f"objective priorities must sum to 1.0, got {total:.6f}")
        for name, value in profile.objective_priorities.items():
            if not name.strip():
                raise ValueError("objective priority name is required")
            self._validate_unit(value, f"objective priority {name}")
        for adjustment in profile.adjustments:
            self._validate_unit(adjustment.confidence, "adjustment confidence")

    def validate_decision(self, decision: AdaptiveDecision) -> None:
        if not decision.alternative_id.strip():
            raise ValueError("AdaptiveDecision.alternative_id is required")
        self.validate_profile(decision.behavior_profile)
        self.validate_rules(decision.applied_rules)
        self._validate_unit(decision.adaptation_score, "adaptation score")
        self._validate_unit(decision.confidence, "adaptive confidence")

    def validate_package(self, package: AdaptiveDecisionPackage) -> None:
        if not isinstance(package, AdaptiveDecisionPackage):
            raise ValueError("Expected AdaptiveDecisionPackage")
        for result in package.adaptive_results:
            self.validate_decision(result)
        if package.adaptive_results and package.selected_adaptive_result is None:
            raise ValueError("selected adaptive result is required when adaptive results exist")
        if not package.adaptive_results and package.selected_adaptive_result is not None:
            raise ValueError("selected adaptive result must be None when no adaptive results exist")
        if package.selected_adaptive_result is not None and package.selected_adaptive_result not in package.adaptive_results:
            raise ValueError("selected adaptive result must be present in adaptive results")

    def _validate_unit(self, value: float, field_name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field_name} must be between 0 and 1")
