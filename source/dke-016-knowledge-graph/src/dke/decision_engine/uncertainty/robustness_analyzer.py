from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.optimization import OptimizationResult

from .models import RobustnessResult, SensitivityResult


class RobustnessAnalyzer:
    def analyze(self, result: OptimizationResult, sensitivity: tuple[SensitivityResult, ...]) -> RobustnessResult:
        max_sensitivity = max((item.sensitivity_score for item in sensitivity), default=0.0)
        average_sensitivity = sum(item.sensitivity_score for item in sensitivity) / len(sensitivity) if sensitivity else 0.0
        confidence_stability = clamp_confidence(1.0 - average_sensitivity)
        robustness = clamp_confidence((result.confidence * 0.35) + (result.optimized_score * 0.35) + (confidence_stability * 0.3))
        failure_points = self._failure_points(result, max_sensitivity, confidence_stability)
        return RobustnessResult(
            robustness_score=robustness,
            stable_under_variation=robustness >= 0.6 and max_sensitivity <= 0.35,
            confidence_stability=confidence_stability,
            failure_points=failure_points,
            metadata={"max_sensitivity": max_sensitivity},
        )

    def _failure_points(
        self,
        result: OptimizationResult,
        max_sensitivity: float,
        confidence_stability: float,
    ) -> tuple[str, ...]:
        failures = []
        if max_sensitivity > 0.35:
            failures.append("High parameter sensitivity may change the optimized recommendation.")
        if confidence_stability < 0.6:
            failures.append("Confidence stability is below the desired threshold.")
        if result.metadata.get("constraint_violations"):
            failures.append("Constraint violations remain a robustness risk.")
        return tuple(failures)
