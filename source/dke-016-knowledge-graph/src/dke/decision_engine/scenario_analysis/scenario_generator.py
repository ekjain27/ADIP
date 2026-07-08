from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import ScenarioDefinition
from .scenario_library import ScenarioLibrary


class ScenarioGenerator:
    def __init__(self, library: ScenarioLibrary | None = None) -> None:
        self.library = library or ScenarioLibrary()

    def generate(self, custom_scenarios: tuple[ScenarioDefinition, ...] = ()) -> tuple[ScenarioDefinition, ...]:
        scenarios = (*self.library.default_scenarios(), *custom_scenarios)
        return self._normalize_probabilities(self._deduplicate(scenarios))

    def _deduplicate(self, scenarios: tuple[ScenarioDefinition, ...]) -> tuple[ScenarioDefinition, ...]:
        seen: set[str] = set()
        unique = []
        for scenario in scenarios:
            if scenario.scenario_id in seen:
                continue
            seen.add(scenario.scenario_id)
            unique.append(scenario)
        return tuple(unique)

    def _normalize_probabilities(self, scenarios: tuple[ScenarioDefinition, ...]) -> tuple[ScenarioDefinition, ...]:
        if not scenarios:
            return ()
        total = sum(max(0.0, scenario.probability) for scenario in scenarios)
        if total <= 0:
            total = float(len(scenarios))
            raw = [1.0 for _ in scenarios]
        else:
            raw = [max(0.0, scenario.probability) for scenario in scenarios]
        normalized = []
        for scenario, probability in zip(scenarios, raw):
            normalized.append(
                ScenarioDefinition(
                    scenario.scenario_id,
                    scenario.name,
                    scenario.description,
                    scenario.category,
                    scenario.assumptions,
                    clamp_confidence(probability / total),
                    scenario.metadata,
                )
            )
        drift = round(1.0 - sum(item.probability for item in normalized), 6)
        if normalized:
            last = normalized[-1]
            normalized[-1] = ScenarioDefinition(
                last.scenario_id,
                last.name,
                last.description,
                last.category,
                last.assumptions,
                clamp_confidence(last.probability + drift),
                last.metadata,
            )
        return tuple(normalized)
