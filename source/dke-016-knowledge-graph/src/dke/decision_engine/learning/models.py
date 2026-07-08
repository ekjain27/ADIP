from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class DecisionFeedback:
    feedback_id: str
    alternative_id: str
    predicted_score: float
    actual_score: float
    difference: float
    feedback_type: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningPattern:
    pattern_id: str
    name: str
    description: str
    frequency: int
    confidence: float
    affected_components: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConfidenceUpdate:
    old_confidence: float
    new_confidence: float
    adjustment: float
    reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningResult:
    alternative_id: str
    feedback: DecisionFeedback
    patterns: tuple[LearningPattern, ...]
    confidence_update: ConfidenceUpdate
    learning_score: float
    recommendations: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningDecisionPackage:
    learning_results: tuple[LearningResult, ...]
    selected_learning: LearningResult | None
    history: Mapping[str, Any]
    summary: str
    learning_strategy: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
