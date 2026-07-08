from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from decision_engine.evaluation import EvaluatedAlternative


@dataclass(frozen=True)
class RankedAlternative:
    rank: int
    evaluated_alternative: EvaluatedAlternative
    alternative_id: str
    overall_score: float
    ranking_score: float
    selection_status: str
    tie_breaker_score: float
    explanation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RankedDecisionPackage:
    ranked_alternatives: tuple[RankedAlternative, ...]
    selected_alternative: RankedAlternative | None
    top_alternatives: tuple[RankedAlternative, ...]
    total_ranked: int
    ranking_strategy: str
    selection_strategy: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
