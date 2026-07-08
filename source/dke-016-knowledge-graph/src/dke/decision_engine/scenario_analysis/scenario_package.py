from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import ScenarioAnalysisDecisionPackage, ScenarioComparison
from .scenario_validator import ScenarioValidator


class ScenarioPackageBuilder:
    def __init__(self, validator: ScenarioValidator | None = None) -> None:
        self.validator = validator or ScenarioValidator()

    def build(
        self,
        comparisons: tuple[ScenarioComparison, ...],
        selected_comparison: ScenarioComparison | None,
        scenario_strategy: str = "deterministic_multi_scenario_analysis",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ScenarioAnalysisDecisionPackage:
        package_metadata = {
            "module": "DIE-009",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.scenario_analysis",
        }
        package_metadata.update(metadata or {})
        package = ScenarioAnalysisDecisionPackage(
            scenario_comparisons=comparisons,
            selected_comparison=selected_comparison,
            scenario_strategy=scenario_strategy,
            summary=summary or self._summary(comparisons, selected_comparison),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, comparisons: tuple[ScenarioComparison, ...], selected: ScenarioComparison | None) -> str:
        if not comparisons:
            return "No uncertainty results were available for scenario analysis."
        if selected is None:
            return f"Analyzed {len(comparisons)} comparison(s), but no selected comparison is available."
        return f"Selected {selected.alternative_id} has average scenario score {selected.average_score:.3f} and stability {selected.stability_score:.3f}."
