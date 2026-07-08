from __future__ import annotations

import logging

from decision_engine.ranking import RankedDecisionPackage

from .models import SimulatedOutcome, SimulationDecisionPackage
from .outcome_simulator import OutcomeSimulator
from .simulation_package import SimulationPackageBuilder

logger = logging.getLogger(__name__)


class DecisionSimulator:
    STRATEGY = "deterministic_scenario_simulation"

    def __init__(
        self,
        outcome_simulator: OutcomeSimulator | None = None,
        package_builder: SimulationPackageBuilder | None = None,
    ) -> None:
        self.outcome_simulator = outcome_simulator or OutcomeSimulator()
        self.package_builder = package_builder or SimulationPackageBuilder()

    def simulate(self, ranked_package: RankedDecisionPackage) -> SimulationDecisionPackage:
        if not isinstance(ranked_package, RankedDecisionPackage):
            raise ValueError("DecisionSimulator.simulate requires a RankedDecisionPackage")
        logger.info("Simulating ranked decision alternatives")
        outcomes = tuple(self.outcome_simulator.simulate(ranked) for ranked in ranked_package.ranked_alternatives)
        sorted_outcomes = tuple(sorted(outcomes, key=lambda item: item.outcome_score, reverse=True))
        selected = self._selected_outcome(sorted_outcomes, ranked_package)
        return self.package_builder.build(
            sorted_outcomes,
            selected,
            ranked_package=ranked_package,
            simulation_strategy=self.STRATEGY,
            metadata={"source_ranking_strategy": ranked_package.ranking_strategy},
        )

    def _selected_outcome(
        self,
        outcomes: tuple[SimulatedOutcome, ...],
        ranked_package: RankedDecisionPackage,
    ) -> SimulatedOutcome | None:
        if not outcomes:
            return None
        if ranked_package.selected_alternative is not None:
            selected_id = ranked_package.selected_alternative.alternative_id
            for outcome in outcomes:
                if outcome.alternative_id == selected_id:
                    return outcome
        return outcomes[0]
