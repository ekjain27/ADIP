from __future__ import annotations

from dataclasses import dataclass

from .performance_errors import InvalidPerformanceProfileError

PERFORMANCE_METRICS = (
    "execution_time",
    "throughput",
    "latency",
    "memory_usage",
    "operation_counts",
    "workflow_duration",
)

VALID_PERFORMANCE_PROFILES = ("quick", "standard", "comprehensive")


@dataclass(frozen=True)
class PerformanceProfile:
    profile_id: str
    iterations: int
    workload_multiplier: int
    metric_thresholds: dict[str, float]

    def snapshot(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "iterations": self.iterations,
            "workload_multiplier": self.workload_multiplier,
            "metric_thresholds": tuple((metric, self.metric_thresholds[metric]) for metric in PERFORMANCE_METRICS),
        }


def get_performance_profile(profile: str | PerformanceProfile = "standard") -> PerformanceProfile:
    if isinstance(profile, PerformanceProfile):
        return validate_performance_profile(profile)
    if profile not in VALID_PERFORMANCE_PROFILES:
        raise InvalidPerformanceProfileError(f"invalid performance benchmark profile: {profile}")
    settings = {
        "quick": (1, 1),
        "standard": (3, 2),
        "comprehensive": (5, 4),
    }
    iterations, multiplier = settings[profile]
    thresholds = {
        "execution_time": 500.0 * multiplier,
        "throughput": 0.001,
        "latency": 500.0 * multiplier,
        "memory_usage": 2048.0 * multiplier,
        "operation_counts": 10000.0 * multiplier,
        "workflow_duration": 2000.0 * multiplier,
    }
    return PerformanceProfile(profile, iterations, multiplier, thresholds)


def validate_performance_profile(profile: PerformanceProfile) -> PerformanceProfile:
    if not isinstance(profile, PerformanceProfile):
        raise InvalidPerformanceProfileError("profile must be PerformanceProfile")
    if profile.profile_id not in VALID_PERFORMANCE_PROFILES:
        raise InvalidPerformanceProfileError(f"invalid performance benchmark profile: {profile.profile_id}")
    if not isinstance(profile.iterations, int) or profile.iterations <= 0:
        raise InvalidPerformanceProfileError("profile iterations must be positive")
    if not isinstance(profile.workload_multiplier, int) or profile.workload_multiplier <= 0:
        raise InvalidPerformanceProfileError("profile workload_multiplier must be positive")
    missing = tuple(metric for metric in PERFORMANCE_METRICS if metric not in profile.metric_thresholds)
    if missing:
        raise InvalidPerformanceProfileError(f"missing performance metric threshold(s): {', '.join(missing)}")
    return profile
