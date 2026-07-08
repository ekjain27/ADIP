from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from decision_engine.ranking import RankedAlternative


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    scenario_type: str
    title: str
    description: str
    assumptions: tuple[str, ...] = ()
    probability: float = 0.0
    impact_score: float = 0.0
    confidence: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulatedOutcome:
    alternative_id: str
    ranked_alternative: RankedAlternative
    scenarios: tuple[Scenario, ...]
    expected_outcome: Scenario
    best_case: Scenario
    worst_case: Scenario
    risk_impact: float
    confidence_impact: float
    outcome_score: float
    explanation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulationDecisionPackage:
    simulated_outcomes: tuple[SimulatedOutcome, ...]
    selected_outcome: SimulatedOutcome | None
    total_simulated: int
    simulation_strategy: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
