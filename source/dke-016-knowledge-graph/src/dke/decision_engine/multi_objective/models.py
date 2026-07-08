from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class MultiObjective:
    objective_id: str
    name: str
    weight: float
    target: str = "maximize"
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ObjectiveScore:
    alternative_id: str
    scores: Mapping[str, float]
    weighted_score: float
    source_learning_score: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParetoResult:
    alternative_id: str
    dominates: tuple[str, ...]
    dominated_by: tuple[str, ...]
    is_pareto_optimal: bool
    pareto_rank: int
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TradeoffMatrix:
    alternatives: tuple[str, ...]
    objectives: tuple[str, ...]
    matrix: Mapping[str, Mapping[str, float]]
    pairwise_tradeoffs: Mapping[str, Mapping[str, float]]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BalancedResult:
    alternative_id: str
    objective_score: ObjectiveScore
    pareto_result: ParetoResult
    balance_score: float
    tradeoff_score: float
    selected_reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MultiObjectiveDecisionPackage:
    objectives: tuple[MultiObjective, ...]
    objective_scores: tuple[ObjectiveScore, ...]
    pareto_results: tuple[ParetoResult, ...]
    tradeoff_matrix: TradeoffMatrix
    balanced_results: tuple[BalancedResult, ...]
    selected_result: BalancedResult | None
    optimization_strategy: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
