from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class OptimizationObjective:
    objective_id: str
    name: str
    weight: float
    target: str = "maximize"
    priority: str = "medium"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OptimizationResult:
    alternative_id: str
    original_score: float
    optimized_score: float
    improvements: tuple[str, ...] = ()
    tradeoffs: tuple[str, ...] = ()
    objective_results: Mapping[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OptimizedDecisionPackage:
    optimized_results: tuple[OptimizationResult, ...]
    selected_result: OptimizationResult | None
    optimization_strategy: str
    optimization_summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
