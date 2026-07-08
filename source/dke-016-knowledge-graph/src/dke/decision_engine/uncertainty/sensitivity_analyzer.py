from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.optimization import OptimizationResult

from .models import SensitivityResult


class SensitivityAnalyzer:
    PARAMETERS = ("confidence", "risk", "constraints", "objective_weights", "assumptions")

    def analyze(self, result: OptimizationResult) -> tuple[SensitivityResult, ...]:
        return tuple(self._analyze_parameter(result, parameter) for parameter in self.PARAMETERS)

    def _analyze_parameter(self, result: OptimizationResult, parameter: str) -> SensitivityResult:
        baseline = self._baseline(result, parameter)
        varied = clamp_confidence(baseline + self._variation(parameter, result))
        sensitivity = clamp_confidence(abs(varied - baseline) * 2.5)
        return SensitivityResult(
            parameter=parameter,
            baseline_value=baseline,
            varied_value=varied,
            sensitivity_score=sensitivity,
            explanation=f"{parameter} variation changes the optimized decision signal by {sensitivity:.3f}.",
            metadata={"alternative_id": result.alternative_id},
        )

    def _baseline(self, result: OptimizationResult, parameter: str) -> float:
        if parameter == "confidence":
            return result.confidence
        if parameter == "risk":
            return clamp_confidence(1.0 - min(0.8, len(result.tradeoffs) * 0.12))
        if parameter == "constraints":
            return clamp_confidence(float(result.metadata.get("constraint_satisfaction_score", 0.6)))
        if parameter == "objective_weights":
            return clamp_confidence(sum(result.objective_results.values()) / len(result.objective_results)) if result.objective_results else 0.5
        return clamp_confidence(1.0 - min(0.7, len(result.improvements) * 0.04))

    def _variation(self, parameter: str, result: OptimizationResult) -> float:
        if parameter == "risk":
            return -min(0.12, len(result.tradeoffs) * 0.02)
        if parameter == "constraints":
            return 0.06 if not result.metadata.get("constraint_violations") else -0.08
        if parameter == "objective_weights":
            return 0.04
        if parameter == "assumptions":
            return -min(0.1, len(result.improvements) * 0.01)
        return 0.05
