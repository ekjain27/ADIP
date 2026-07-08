from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class AssumptionImpact:
    assumption_id: str
    description: str
    influence_score: float
    confidence: float
    affected_components: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SensitivityResult:
    parameter: str
    baseline_value: float
    varied_value: float
    sensitivity_score: float
    explanation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RobustnessResult:
    robustness_score: float
    stable_under_variation: bool
    confidence_stability: float
    failure_points: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UncertaintyResult:
    alternative_id: str
    uncertainty_score: float
    reliability_score: float
    confidence_interval: tuple[float, float]
    robustness: RobustnessResult
    sensitivity: tuple[SensitivityResult, ...] = ()
    assumptions: tuple[AssumptionImpact, ...] = ()
    explanation: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UncertaintyDecisionPackage:
    uncertainty_results: tuple[UncertaintyResult, ...]
    selected_result: UncertaintyResult | None
    uncertainty_strategy: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
