from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class AlternativeDecision:
    alternative_id: str
    title: str
    description: str
    supporting_evidence: tuple[str, ...] = ()
    supporting_goals: tuple[str, ...] = ()
    supporting_constraints: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    confidence: float = 0.0
    feasibility: float = 0.0
    risks: tuple[str, ...] = ()
    advantages: tuple[str, ...] = ()
    disadvantages: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AlternativeDecisionPackage:
    alternatives: tuple[AlternativeDecision, ...]
    total_generated: int
    generation_strategy: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
