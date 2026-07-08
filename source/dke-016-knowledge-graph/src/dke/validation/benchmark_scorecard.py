from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .benchmark_profiles import BenchmarkProfile, QUALITY_METRICS


@dataclass(frozen=True)
class BenchmarkScorecard:
    benchmark_id: str
    profile_id: str
    status: str
    metrics: Mapping[str, float]
    weighted_score: float
    diagnostics: tuple[str, ...]
    decision_output: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "profile_id": self.profile_id,
            "status": self.status,
            "metrics": tuple((metric, round(float(self.metrics[metric]), 6)) for metric in QUALITY_METRICS),
            "weighted_score": round(float(self.weighted_score), 6),
            "diagnostics": self.diagnostics,
            "decision_output": _normalize(self.decision_output),
        }


def generate_scorecard(
    benchmark_id: str,
    profile: BenchmarkProfile,
    metrics: Mapping[str, float],
    decision_output: Mapping[str, Any],
    diagnostics: tuple[str, ...] = (),
) -> BenchmarkScorecard:
    total_weight = sum(float(profile.weights[metric]) for metric in QUALITY_METRICS)
    score = sum(float(metrics[metric]) * float(profile.weights[metric]) for metric in QUALITY_METRICS) / total_weight
    status = "passed" if score >= 0.75 and not diagnostics else "failed"
    return BenchmarkScorecard(
        benchmark_id=benchmark_id,
        profile_id=profile.profile_id,
        status=status,
        metrics=dict(metrics),
        weighted_score=round(score, 6),
        diagnostics=tuple(sorted(diagnostics)),
        decision_output=dict(decision_output),
    )


def summarize_scorecards(scorecards: tuple[BenchmarkScorecard, ...]) -> dict[str, Any]:
    total = len(scorecards)
    passed = sum(1 for scorecard in scorecards if scorecard.status == "passed")
    average = round(sum(scorecard.weighted_score for scorecard in scorecards) / total, 6) if total else 0.0
    return {
        "module": "VB-002",
        "status": "passed" if passed == total else "failed",
        "benchmark_count": total,
        "passed_count": passed,
        "failed_count": total - passed,
        "average_score": average,
    }


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return tuple(_normalize(item) for item in value)
    return value

