from __future__ import annotations

from decision_engine.ranking import RankedDecisionPackage

from .models import Scenario, SimulatedOutcome, SimulationDecisionPackage


class SimulationValidator:
    REQUIRED_SCENARIOS = {"best_case", "expected_case", "worst_case"}

    def validate(
        self,
        package: SimulationDecisionPackage,
        ranked_package: RankedDecisionPackage | None = None,
    ) -> None:
        if not isinstance(package, SimulationDecisionPackage):
            raise ValueError("Expected SimulationDecisionPackage")
        if package.total_simulated != len(package.simulated_outcomes):
            raise ValueError("total_simulated does not match simulated outcome count")
        source_ids = {item.alternative_id for item in ranked_package.ranked_alternatives} if ranked_package else set()
        for outcome in package.simulated_outcomes:
            self.validate_outcome(outcome, source_ids)
        if package.simulated_outcomes and package.selected_outcome is None:
            raise ValueError("selected_outcome is required when simulated outcomes exist")
        if not package.simulated_outcomes and package.selected_outcome is not None:
            raise ValueError("selected_outcome must be None when no simulated outcomes exist")

    def validate_outcome(self, outcome: SimulatedOutcome, source_ids: set[str] | None = None) -> None:
        if not outcome.ranked_alternative:
            raise ValueError("SimulatedOutcome must link to a ranked alternative")
        if outcome.alternative_id != outcome.ranked_alternative.alternative_id:
            raise ValueError("SimulatedOutcome alternative_id does not match ranked alternative")
        if source_ids is not None and source_ids and outcome.alternative_id not in source_ids:
            raise ValueError(f"Simulated outcome {outcome.alternative_id} is not linked to the ranked package")
        for field_name in ("risk_impact", "confidence_impact", "outcome_score"):
            value = getattr(outcome, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
        scenario_types = {item.scenario_type for item in outcome.scenarios}
        missing = self.REQUIRED_SCENARIOS - scenario_types
        if missing:
            raise ValueError(f"Missing required scenario types: {', '.join(sorted(missing))}")
        for scenario in outcome.scenarios:
            self.validate_scenario(scenario)
        total_probability = sum(item.probability for item in outcome.scenarios)
        if abs(total_probability - 1.0) > 0.00001:
            raise ValueError(f"Scenario probabilities must sum to 1.0, got {total_probability:.6f}")

    def validate_scenario(self, scenario: Scenario) -> None:
        if not scenario.scenario_id.strip():
            raise ValueError("Scenario.scenario_id is required")
        if scenario.scenario_type not in self.REQUIRED_SCENARIOS:
            raise ValueError(f"Invalid scenario_type: {scenario.scenario_type}")
        if not 0.0 <= scenario.probability <= 1.0:
            raise ValueError(f"Scenario probability must be between 0 and 1 for {scenario.scenario_id}")
        if not 0.0 <= scenario.impact_score <= 1.0:
            raise ValueError(f"Scenario impact_score must be between 0 and 1 for {scenario.scenario_id}")
        if not 0.0 <= scenario.confidence <= 1.0:
            raise ValueError(f"Scenario confidence must be between 0 and 1 for {scenario.scenario_id}")
