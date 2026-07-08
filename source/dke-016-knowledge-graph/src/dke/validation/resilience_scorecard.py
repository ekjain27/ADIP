from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

RESILIENCE_METRICS = (
    "graceful_degradation",
    "error_propagation",
    "recovery_behavior",
    "retry_policy_behavior",
    "platform_stability",
)


@dataclass(frozen=True)
class ResilienceScorecard:
    scenario_id: str
    status: str
    metrics: Mapping[str, float]
    score: float
    diagnostics: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "status": self.status,
            "metrics": tuple((metric, round(float(self.metrics[metric]), 6)) for metric in RESILIENCE_METRICS),
            "score": round(float(self.score), 6),
            "diagnostics": self.diagnostics,
        }


def generate_resilience_scorecard(scenario_id: str, metrics: Mapping[str, float]) -> ResilienceScorecard:
    normalized = {metric: round(float(metrics.get(metric, 0.0)), 6) for metric in RESILIENCE_METRICS}
    score = round(sum(normalized.values()) / len(RESILIENCE_METRICS), 6)
    diagnostics = tuple(f"{metric}:failed" for metric in RESILIENCE_METRICS if normalized[metric] < 1.0)
    return ResilienceScorecard(
        scenario_id=scenario_id,
        status="passed" if not diagnostics else "failed",
        metrics=normalized,
        score=score,
        diagnostics=diagnostics,
    )
