from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.ranking import RankedAlternative

from .impact_analyzer import ImpactAnalyzer
from .models import Scenario, SimulatedOutcome
from .scenario_generator import ScenarioGenerator


class OutcomeSimulator:
    def __init__(
        self,
        scenario_generator: ScenarioGenerator | None = None,
        impact_analyzer: ImpactAnalyzer | None = None,
    ) -> None:
        self.scenario_generator = scenario_generator or ScenarioGenerator()
        self.impact_analyzer = impact_analyzer or ImpactAnalyzer()

    def simulate(self, ranked_alternative: RankedAlternative) -> SimulatedOutcome:
        scenarios = self.scenario_generator.generate(ranked_alternative)
        best_case = self._scenario_by_type(scenarios, "best_case")
        expected_outcome = self._scenario_by_type(scenarios, "expected_case")
        worst_case = self._scenario_by_type(scenarios, "worst_case")
        outcome_score = self._outcome_score(scenarios)
        risk_impact = self.impact_analyzer.risk_impact(ranked_alternative)
        confidence_impact = self.impact_analyzer.confidence_impact(ranked_alternative, scenarios)
        return SimulatedOutcome(
            alternative_id=ranked_alternative.alternative_id,
            ranked_alternative=ranked_alternative,
            scenarios=scenarios,
            expected_outcome=expected_outcome,
            best_case=best_case,
            worst_case=worst_case,
            risk_impact=risk_impact,
            confidence_impact=confidence_impact,
            outcome_score=outcome_score,
            explanation=self._explanation(ranked_alternative, outcome_score),
            metadata={"rank": ranked_alternative.rank, "selection_status": ranked_alternative.selection_status},
        )

    def _outcome_score(self, scenarios: tuple[Scenario, ...]) -> float:
        return clamp_confidence(sum(item.impact_score * item.probability for item in scenarios))

    def _scenario_by_type(self, scenarios: tuple[Scenario, ...], scenario_type: str) -> Scenario:
        for scenario in scenarios:
            if scenario.scenario_type == scenario_type:
                return scenario
        raise ValueError(f"Missing required scenario type: {scenario_type}")

    def _explanation(self, ranked_alternative: RankedAlternative, outcome_score: float) -> str:
        return (
            f"Alternative {ranked_alternative.alternative_id} simulated with outcome score "
            f"{outcome_score:.3f} from deterministic best/expected/worst scenarios."
        )
