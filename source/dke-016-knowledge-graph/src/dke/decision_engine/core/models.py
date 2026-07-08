from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def clamp_confidence(value: Any, default: float = 0.0) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        confidence = default
    if confidence > 1.0:
        confidence = confidence / 100.0
    return max(0.0, min(1.0, round(confidence, 6)))


@dataclass(frozen=True)
class Evidence:
    id: str
    source: str = "unknown"
    text: str = ""
    confidence: float = 0.0
    score: float = 0.0
    timestamp: datetime = field(default_factory=utc_now)
    domain: str = "general"
    relationships: tuple[Any, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Evidence.id is required")
        object.__setattr__(self, "confidence", clamp_confidence(self.confidence))
        object.__setattr__(self, "score", clamp_confidence(self.score))


@dataclass(frozen=True)
class Goal:
    objective: str
    priority: str = "primary"
    measurable: bool = False
    dependencies: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("Goal.objective is required")


@dataclass(frozen=True)
class Constraint:
    type: str
    severity: str = "medium"
    source: str = "unknown"
    parameters: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.type.strip():
            raise ValueError("Constraint.type is required")


@dataclass(frozen=True)
class DecisionState:
    evidence: tuple[Evidence, ...] = ()
    goals: tuple[Goal, ...] = ()
    constraints: tuple[Constraint, ...] = ()
    assumptions: tuple[str, ...] = ()
    uncertainty: float = 1.0
    confidence: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", clamp_confidence(self.confidence))
        object.__setattr__(self, "uncertainty", clamp_confidence(self.uncertainty, default=1.0))


@dataclass(frozen=True)
class DecisionPackage:
    decision_state: DecisionState
    evidence_set: tuple[Evidence, ...]
    goal_set: tuple[Goal, ...]
    constraint_set: tuple[Constraint, ...]
    confidence: float
    processing_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.decision_state, DecisionState):
            raise ValueError("DecisionPackage.decision_state must be a DecisionState")
        object.__setattr__(self, "confidence", clamp_confidence(self.confidence))
