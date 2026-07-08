from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now
from decision_engine.ranking import RankedDecisionPackage

from .models import SimulatedOutcome, SimulationDecisionPackage
from .simulation_validator import SimulationValidator


class SimulationPackageBuilder:
    def __init__(self, validator: SimulationValidator | None = None) -> None:
        self.validator = validator or SimulationValidator()

    def build(
        self,
        simulated_outcomes: tuple[SimulatedOutcome, ...],
        selected_outcome: SimulatedOutcome | None,
        ranked_package: RankedDecisionPackage | None = None,
        simulation_strategy: str = "deterministic_scenario_simulation",
        metadata: dict[str, Any] | None = None,
    ) -> SimulationDecisionPackage:
        package_metadata = {
            "module": "DIE-005",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.simulation",
        }
        package_metadata.update(metadata or {})
        package = SimulationDecisionPackage(
            simulated_outcomes=simulated_outcomes,
            selected_outcome=selected_outcome,
            total_simulated=len(simulated_outcomes),
            simulation_strategy=simulation_strategy,
            metadata=package_metadata,
        )
        self.validator.validate(package, ranked_package)
        return package
