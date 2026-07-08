from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .performance_errors import (
    DuplicatePerformanceBenchmarkError,
    PerformanceBenchmarkDefinitionError,
    UnsupportedPerformanceMetricError,
)
from .performance_profiles import PERFORMANCE_METRICS

VALID_PERFORMANCE_TARGETS = ("module", "workflow", "platform_component")


@dataclass(frozen=True)
class PerformanceBenchmarkDefinition:
    benchmark_id: str
    name: str
    target_type: str
    target: str
    payload: Mapping[str, Any]
    metrics: tuple[str, ...] = PERFORMANCE_METRICS

    def __post_init__(self) -> None:
        if not isinstance(self.benchmark_id, str) or not self.benchmark_id.strip():
            raise PerformanceBenchmarkDefinitionError("benchmark_id is required")
        if not isinstance(self.name, str) or not self.name.strip():
            raise PerformanceBenchmarkDefinitionError("benchmark name is required")
        if self.target_type not in VALID_PERFORMANCE_TARGETS:
            raise PerformanceBenchmarkDefinitionError(f"invalid performance target_type: {self.target_type}")
        if not isinstance(self.target, str) or not self.target.strip():
            raise PerformanceBenchmarkDefinitionError("performance benchmark target is required")
        if not isinstance(self.payload, Mapping) or not self.payload:
            raise PerformanceBenchmarkDefinitionError("performance benchmark payload is required")
        unsupported = tuple(metric for metric in self.metrics if metric not in PERFORMANCE_METRICS)
        if unsupported:
            raise UnsupportedPerformanceMetricError(f"unsupported performance metric(s): {', '.join(unsupported)}")

    def snapshot(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "name": self.name,
            "target_type": self.target_type,
            "target": self.target,
            "payload": _normalize(self.payload),
            "metrics": tuple(sorted(self.metrics)),
        }


class PerformanceBenchmarkRegistry:
    def __init__(self) -> None:
        self._benchmarks: dict[str, PerformanceBenchmarkDefinition] = {}

    def register_performance_benchmark(self, benchmark: PerformanceBenchmarkDefinition) -> PerformanceBenchmarkDefinition:
        if not isinstance(benchmark, PerformanceBenchmarkDefinition):
            raise PerformanceBenchmarkDefinitionError("benchmark must be PerformanceBenchmarkDefinition")
        if benchmark.benchmark_id in self._benchmarks:
            raise DuplicatePerformanceBenchmarkError(f"performance benchmark already registered: {benchmark.benchmark_id}")
        self._benchmarks[benchmark.benchmark_id] = benchmark
        return benchmark

    def get_performance_benchmark(self, benchmark_id: str) -> PerformanceBenchmarkDefinition:
        if not isinstance(benchmark_id, str) or not benchmark_id.strip():
            raise PerformanceBenchmarkDefinitionError("benchmark_id is required")
        normalized = benchmark_id.strip()
        try:
            return self._benchmarks[normalized]
        except KeyError as exc:
            raise PerformanceBenchmarkDefinitionError(f"performance benchmark is not registered: {normalized}") from exc

    def list_performance_benchmarks(self) -> tuple[PerformanceBenchmarkDefinition, ...]:
        return tuple(self._benchmarks[key] for key in sorted(self._benchmarks))

    def export_registry_snapshot(self) -> dict[str, Any]:
        return {
            "module": "VB-003",
            "status": "exported",
            "benchmark_count": len(self._benchmarks),
            "benchmarks": tuple(benchmark.snapshot() for benchmark in self.list_performance_benchmarks()),
        }

    def benchmarks(self) -> Mapping[str, PerformanceBenchmarkDefinition]:
        return MappingProxyType(dict(sorted(self._benchmarks.items())))


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return tuple(_normalize(item) for item in value)
    return value
