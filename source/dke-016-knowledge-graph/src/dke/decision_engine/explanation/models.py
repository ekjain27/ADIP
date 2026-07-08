from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ExplanationSection:
    section_id: str
    title: str
    content: str
    evidence_refs: tuple[str, ...] = ()
    risk_refs: tuple[str, ...] = ()
    scenario_refs: tuple[str, ...] = ()
    confidence: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionExplanation:
    alternative_id: str
    summary: str
    reasoning: str
    evidence_explanation: str
    risk_explanation: str
    scenario_explanation: str
    recommendation_explanation: str
    assumptions: tuple[str, ...] = ()
    confidence: float = 0.0
    sections: tuple[ExplanationSection, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExplanationDecisionPackage:
    explanations: tuple[DecisionExplanation, ...]
    selected_explanation: DecisionExplanation | None
    total_explained: int
    explanation_strategy: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
