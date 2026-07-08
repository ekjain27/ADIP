from __future__ import annotations

from decision_engine.simulation import SimulatedOutcome


class ScenarioExplainer:
    def explain(self, outcome: SimulatedOutcome) -> str:
        best = outcome.best_case
        expected = outcome.expected_outcome
        worst = outcome.worst_case
        return (
            f"Best case '{best.title}' has probability {best.probability:.3f} and impact {best.impact_score:.3f}. "
            f"Expected case '{expected.title}' has probability {expected.probability:.3f} and impact {expected.impact_score:.3f}. "
            f"Worst case '{worst.title}' has probability {worst.probability:.3f} and impact {worst.impact_score:.3f}. "
            f"The combined outcome score is {outcome.outcome_score:.3f}."
        )

    def scenario_refs(self, outcome: SimulatedOutcome) -> tuple[str, ...]:
        return tuple(scenario.scenario_id for scenario in outcome.scenarios)
