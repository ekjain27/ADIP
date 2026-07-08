from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.optimization import OptimizationResult


class UncertaintyEstimator:
    def estimate(self, result: OptimizationResult) -> float:
        confidence = result.confidence or result.optimized_score
        optimization_gain = float(result.metadata.get("optimization_gain", result.optimized_score - result.original_score))
        risk_count = self._risk_count(result)
        objective_count = len(result.objective_results)
        evidence_proxy = min(1.0, objective_count / 6.0)
        uncertainty = 1.0 - (confidence * 0.45) - (result.optimized_score * 0.25) - (evidence_proxy * 0.1)
        uncertainty += min(0.25, risk_count * 0.05)
        uncertainty -= min(0.1, max(0.0, optimization_gain) * 0.5)
        return clamp_confidence(uncertainty)

    def reliability(self, result: OptimizationResult, uncertainty_score: float) -> float:
        objective_average = (
            sum(result.objective_results.values()) / len(result.objective_results)
            if result.objective_results
            else result.optimized_score
        )
        reliability = (1.0 - uncertainty_score) * 0.55 + result.confidence * 0.25 + objective_average * 0.2
        return clamp_confidence(reliability)

    def confidence_interval(self, result: OptimizationResult, uncertainty_score: float) -> tuple[float, float]:
        radius = 0.05 + (uncertainty_score * 0.15)
        center = result.optimized_score
        lower = max(0.0, min(1.0, round(center - radius, 6)))
        upper = max(0.0, min(1.0, round(center + radius, 6)))
        return (lower, upper)

    def _risk_count(self, result: OptimizationResult) -> int:
        text = " ".join((*result.tradeoffs, *result.improvements)).lower()
        return sum(1 for token in ("risk", "failure", "deadline", "critical", "violation") if token in text)
