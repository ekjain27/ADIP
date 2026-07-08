from __future__ import annotations

from .models import (
    AssumptionImpact,
    RobustnessResult,
    SensitivityResult,
    UncertaintyDecisionPackage,
    UncertaintyResult,
)


class UncertaintyValidator:
    def validate_package(self, package: UncertaintyDecisionPackage) -> None:
        if not isinstance(package, UncertaintyDecisionPackage):
            raise ValueError("Expected UncertaintyDecisionPackage")
        if package.uncertainty_results and package.selected_result is None:
            raise ValueError("selected_result is required when uncertainty results exist")
        if not package.uncertainty_results and package.selected_result is not None:
            raise ValueError("selected_result must be None when no uncertainty results exist")
        for result in package.uncertainty_results:
            self.validate_result(result)

    def validate_result(self, result: UncertaintyResult) -> None:
        if not result.alternative_id.strip():
            raise ValueError("UncertaintyResult.alternative_id is required")
        self._validate_unit(result.uncertainty_score, "uncertainty_score")
        self._validate_unit(result.reliability_score, "reliability_score")
        if len(result.confidence_interval) != 2:
            raise ValueError("confidence_interval must contain lower and upper bounds")
        lower, upper = result.confidence_interval
        self._validate_unit(lower, "confidence_interval lower bound")
        self._validate_unit(upper, "confidence_interval upper bound")
        if lower > upper:
            raise ValueError("confidence_interval lower bound cannot exceed upper bound")
        self.validate_robustness(result.robustness)
        for sensitivity in result.sensitivity:
            self.validate_sensitivity(sensitivity)
        for assumption in result.assumptions:
            self.validate_assumption(assumption)

    def validate_robustness(self, robustness: RobustnessResult) -> None:
        self._validate_unit(robustness.robustness_score, "robustness_score")
        self._validate_unit(robustness.confidence_stability, "confidence_stability")

    def validate_sensitivity(self, sensitivity: SensitivityResult) -> None:
        if not sensitivity.parameter.strip():
            raise ValueError("SensitivityResult.parameter is required")
        self._validate_unit(sensitivity.baseline_value, "baseline_value")
        self._validate_unit(sensitivity.varied_value, "varied_value")
        self._validate_unit(sensitivity.sensitivity_score, "sensitivity_score")

    def validate_assumption(self, assumption: AssumptionImpact) -> None:
        if not assumption.assumption_id.strip():
            raise ValueError("AssumptionImpact.assumption_id is required")
        if not assumption.description.strip():
            raise ValueError("AssumptionImpact.description is required")
        self._validate_unit(assumption.influence_score, "influence_score")
        self._validate_unit(assumption.confidence, "assumption confidence")

    def _validate_unit(self, value: float, field_name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field_name} must be between 0 and 1")
