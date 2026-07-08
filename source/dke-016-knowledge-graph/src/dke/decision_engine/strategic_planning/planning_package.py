from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import StrategicPlan, StrategicPlanDecisionPackage
from .planning_validator import PlanningValidator


class PlanningPackageBuilder:
    def __init__(self, validator: PlanningValidator | None = None) -> None:
        self.validator = validator or PlanningValidator()

    def build(
        self,
        strategic_plans: tuple[StrategicPlan, ...],
        selected_plan: StrategicPlan | None,
        planning_strategy: str = "deterministic_hierarchical_strategic_planning_graph",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> StrategicPlanDecisionPackage:
        package_metadata = {
            "module": "DIE-012",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.strategic_planning",
        }
        package_metadata.update(metadata or {})
        package = StrategicPlanDecisionPackage(
            strategic_plans=strategic_plans,
            selected_plan=selected_plan,
            planning_strategy=planning_strategy,
            summary=summary or self._summary(strategic_plans, selected_plan),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, plans: tuple[StrategicPlan, ...], selected: StrategicPlan | None) -> str:
        if not plans:
            return "No optimized decision results were available for strategic planning."
        if selected is None:
            return f"Generated {len(plans)} strategic plan(s), but no selected plan is available."
        return f"Selected strategic plan for {selected.alternative_id} with {len(selected.planning_graph.execution_phases)} execution phases."
