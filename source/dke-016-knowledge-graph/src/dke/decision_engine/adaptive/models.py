from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class AdaptiveRule:
    rule_id: str
    name: str
    trigger: str
    action: str
    priority: str
    enabled: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BehaviorAdjustment:
    adjustment_id: str
    adjustment_type: str
    previous_value: Any
    new_value: Any
    reason: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdaptiveBehaviorProfile:
    profile_id: str
    confidence_threshold: float
    risk_tolerance: float
    governance_sensitivity: float
    objective_priorities: Mapping[str, float]
    checkpoint_frequency: str
    recommendation_mode: str
    adjustments: tuple[BehaviorAdjustment, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdaptiveDecision:
    alternative_id: str
    behavior_profile: AdaptiveBehaviorProfile
    applied_rules: tuple[AdaptiveRule, ...]
    adaptation_summary: str
    adaptation_score: float
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdaptiveDecisionPackage:
    adaptive_results: tuple[AdaptiveDecision, ...]
    selected_adaptive_result: AdaptiveDecision | None
    adaptation_strategy: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
