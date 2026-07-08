from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .performance_profiles import PERFORMANCE_METRICS, PerformanceProfile


@dataclass(frozen=True)
class PerformanceScorecard:
    benchmark_id: str
    profile_id: str
    target_type: str
    target: str
    status: str
    metrics: Mapping[str, float]
    diagnostics: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "profile_id": self.profile_id,
            "target_type": self.target_type,
            "target": self.target,
            "status": self.status,
            "metrics": tuple((metric, round(float(self.metrics[metric]), 6)) for metric in PERFORMANCE_METRICS),
            "diagnostics": self.diagnostics,
        }


def generate_performance_scorecard(
    benchmark_id: str,
    profile: PerformanceProfile,
    target_type: str,
    target: str,
    metrics: Mapping[str, float],
) -> PerformanceScorecard:
    diagnostics = tuple(
        f"{metric}:threshold-exceeded"
        for metric in PERFORMANCE_METRICS
        if metric != "throughput" and metrics[metric] > profile.metric_thresholds[metric]
    )
    throughput_diagnostic = ("throughput:below-threshold",) if metrics["throughput"] < profile.metric_thresholds["throughput"] else ()
    all_diagnostics = tuple(sorted((*diagnostics, *throughput_diagnostic)))
    return PerformanceScorecard(
        benchmark_id=benchmark_id,
        profile_id=profile.profile_id,
        target_type=target_type,
        target=target,
        status="passed" if not all_diagnostics else "failed",
        metrics=dict(metrics),
        diagnostics=all_diagnostics,
    )


def generate_performance_report(scorecards: tuple[PerformanceScorecard, ...]) -> dict[str, Any]:
    passed = sum(1 for scorecard in scorecards if scorecard.status == "passed")
    average_execution_time = round(
        sum(scorecard.metrics["execution_time"] for scorecard in scorecards) / len(scorecards),
        6,
    ) if scorecards else 0.0
    return {
        "module": "VB-003",
        "report_type": "performance_benchmark",
        "status": "passed" if passed == len(scorecards) else "failed",
        "benchmark_count": len(scorecards),
        "passed_count": passed,
        "failed_count": len(scorecards) - passed,
        "average_execution_time": average_execution_time,
        "scorecards": tuple(scorecard.to_dict() for scorecard in scorecards),
    }
