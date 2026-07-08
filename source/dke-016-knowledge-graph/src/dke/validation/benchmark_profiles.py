from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .benchmark_errors import BenchmarkProfileError, MissingBenchmarkMetricError

QUALITY_METRICS = (
    "completeness",
    "consistency",
    "constraint_satisfaction",
    "explainability_coverage",
    "provenance_completeness",
    "governance_compliance",
    "robustness",
)


@dataclass(frozen=True)
class BenchmarkProfile:
    profile_id: str
    weights: Mapping[str, float]

    def normalized_weights(self) -> dict[str, float]:
        validate_profile(self)
        total = sum(float(self.weights[metric]) for metric in QUALITY_METRICS)
        return {metric: round(float(self.weights[metric]) / total, 6) for metric in QUALITY_METRICS}

    def snapshot(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "weights": tuple((metric, self.normalized_weights()[metric]) for metric in QUALITY_METRICS),
        }


def create_equal_weight_profile(profile_id: str = "equal_quality") -> BenchmarkProfile:
    return BenchmarkProfile(profile_id=profile_id, weights={metric: 1.0 for metric in QUALITY_METRICS})


def create_weighted_profile(profile_id: str, weights: Mapping[str, float]) -> BenchmarkProfile:
    return BenchmarkProfile(profile_id=profile_id, weights=dict(weights))


def validate_profile(profile: BenchmarkProfile) -> dict[str, object]:
    if not isinstance(profile, BenchmarkProfile):
        raise BenchmarkProfileError("profile must be BenchmarkProfile")
    if not isinstance(profile.profile_id, str) or not profile.profile_id.strip():
        raise BenchmarkProfileError("profile_id is required")
    missing = tuple(metric for metric in QUALITY_METRICS if metric not in profile.weights)
    if missing:
        raise MissingBenchmarkMetricError(f"missing benchmark metric weight(s): {', '.join(missing)}")
    unknown = tuple(metric for metric in profile.weights if metric not in QUALITY_METRICS)
    if unknown:
        raise BenchmarkProfileError(f"unknown benchmark metric weight(s): {', '.join(sorted(unknown))}")
    for metric, value in profile.weights.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise BenchmarkProfileError(f"invalid benchmark metric weight: {metric}")
    if sum(float(profile.weights[metric]) for metric in QUALITY_METRICS) <= 0:
        raise BenchmarkProfileError("benchmark profile total weight must be positive")
    return {"status": "valid", "profile_id": profile.profile_id, "metrics": QUALITY_METRICS}
