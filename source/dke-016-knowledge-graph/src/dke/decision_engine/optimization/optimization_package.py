from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import OptimizationResult, OptimizedDecisionPackage
from .optimization_validator import OptimizationValidator


class OptimizationPackageBuilder:
    def __init__(self, validator: OptimizationValidator | None = None) -> None:
        self.validator = validator or OptimizationValidator()

    def build(
        self,
        optimized_results: tuple[OptimizationResult, ...],
        selected_result: OptimizationResult | None,
        optimization_strategy: str = "rule_based_multi_objective_optimization",
        optimization_summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> OptimizedDecisionPackage:
        summary = optimization_summary or self._summary(optimized_results, selected_result)
        package_metadata = {
            "module": "DIE-007",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.optimization",
        }
        package_metadata.update(metadata or {})
        package = OptimizedDecisionPackage(
            optimized_results=optimized_results,
            selected_result=selected_result,
            optimization_strategy=optimization_strategy,
            optimization_summary=summary,
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(
        self,
        results: tuple[OptimizationResult, ...],
        selected: OptimizationResult | None,
    ) -> str:
        if not results:
            return "No explanations were available for optimization."
        if selected is None:
            return f"Generated {len(results)} optimization result(s), but no selected result was available."
        gain = selected.optimized_score - selected.original_score
        return f"Optimized {len(results)} result(s); selected {selected.alternative_id} gained {gain:.3f}."
