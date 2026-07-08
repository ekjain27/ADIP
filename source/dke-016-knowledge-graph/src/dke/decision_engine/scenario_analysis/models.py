from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    name: str
    description: str
    category: str
    assumptions: tuple[str, ...] = ()
    probability: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScenarioEvaluation:
    scenario: ScenarioDefinition
    alternative_id: str
    decision_score: float
    risk_score: float
    confidence: float
    robustness: float
    explanation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScenarioComparison:
    alternative_id: str
    evaluations: tuple[ScenarioEvaluation, ...]
    average_score: float
    best_score: float
    worst_score: float
    stability_score: float
    recommendation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScenarioAnalysisDecisionPackage:
    scenario_comparisons: tuple[ScenarioComparison, ...]
    selected_comparison: ScenarioComparison | None
    scenario_strategy: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
