from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from decision_engine.alternatives import AlternativeDecision


@dataclass(frozen=True)
class EvaluationCriteria:
    name: str
    weight: float
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationScore:
    criterion: str
    score: float
    weight: float
    weighted_score: float
    explanation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluatedAlternative:
    alternative: AlternativeDecision
    scores: tuple[EvaluationScore, ...]
    overall_score: float
    confidence: float
    recommendation_level: str
    explanation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluatedDecisionPackage:
    evaluated_alternatives: tuple[EvaluatedAlternative, ...]
    total_evaluated: int
    evaluation_strategy: str
    criteria: tuple[EvaluationCriteria, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)
