from __future__ import annotations

from .models import OptimizationObjective, OptimizationResult, OptimizedDecisionPackage


class OptimizationValidator:
    def validate_objectives(self, objectives: tuple[OptimizationObjective, ...]) -> None:
        if not objectives:
            raise ValueError("Optimization objectives are required")
        total = sum(objective.weight for objective in objectives)
        if abs(total - 1.0) > 0.00001:
            raise ValueError(f"Optimization objective weights must sum to 1.0, got {total:.6f}")
        for objective in objectives:
            if not objective.objective_id.strip() or not objective.name.strip():
                raise ValueError("OptimizationObjective id and name are required")
            if not 0.0 <= objective.weight <= 1.0:
                raise ValueError(f"Optimization objective weight must be between 0 and 1 for {objective.name}")

    def validate_result(self, result: OptimizationResult) -> None:
        if not result.alternative_id.strip():
            raise ValueError("OptimizationResult.alternative_id is required")
        for field_name in ("original_score", "optimized_score", "confidence"):
            value = getattr(result, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1 for {result.alternative_id}")
        if result.optimized_score < result.original_score:
            raise ValueError("optimized_score must be greater than or equal to original_score")
        for name, score in result.objective_results.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"objective result {name} must be between 0 and 1")

    def validate_package(self, package: OptimizedDecisionPackage) -> None:
        if not isinstance(package, OptimizedDecisionPackage):
            raise ValueError("Expected OptimizedDecisionPackage")
        if package.optimized_results and package.selected_result is None:
            raise ValueError("selected_result is required when optimized results exist")
        if not package.optimized_results and package.selected_result is not None:
            raise ValueError("selected_result must be None when no optimized results exist")
        for result in package.optimized_results:
            self.validate_result(result)
