from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .benchmark_errors import BenchmarkDefinitionError, DuplicateBenchmarkError


@dataclass(frozen=True)
class BenchmarkDefinition:
    benchmark_id: str
    name: str
    decision_input: Mapping[str, Any]
    expected_constraints: tuple[str, ...] = ()
    required_fields: tuple[str, ...] = ("decision", "stage")

    def __post_init__(self) -> None:
        if not isinstance(self.benchmark_id, str) or not self.benchmark_id.strip():
            raise BenchmarkDefinitionError("benchmark_id is required")
        if not isinstance(self.name, str) or not self.name.strip():
            raise BenchmarkDefinitionError("benchmark name is required")
        if not isinstance(self.decision_input, Mapping) or not self.decision_input:
            raise BenchmarkDefinitionError("decision_input is required")
        if not isinstance(self.expected_constraints, tuple):
            raise BenchmarkDefinitionError("expected_constraints must be a tuple")
        if not isinstance(self.required_fields, tuple) or not self.required_fields:
            raise BenchmarkDefinitionError("required_fields must be a non-empty tuple")

    def snapshot(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "name": self.name,
            "decision_input": _normalize(self.decision_input),
            "expected_constraints": tuple(sorted(self.expected_constraints)),
            "required_fields": tuple(sorted(self.required_fields)),
        }


class BenchmarkRegistry:
    def __init__(self) -> None:
        self._benchmarks: dict[str, BenchmarkDefinition] = {}

    def register_benchmark(self, benchmark: BenchmarkDefinition) -> BenchmarkDefinition:
        if not isinstance(benchmark, BenchmarkDefinition):
            raise BenchmarkDefinitionError("benchmark must be BenchmarkDefinition")
        if benchmark.benchmark_id in self._benchmarks:
            raise DuplicateBenchmarkError(f"benchmark already registered: {benchmark.benchmark_id}")
        self._benchmarks[benchmark.benchmark_id] = benchmark
        return benchmark

    def get_benchmark(self, benchmark_id: str) -> BenchmarkDefinition:
        normalized = _normalize_id(benchmark_id)
        try:
            return self._benchmarks[normalized]
        except KeyError as exc:
            raise BenchmarkDefinitionError(f"benchmark is not registered: {normalized}") from exc

    def list_benchmarks(self) -> tuple[BenchmarkDefinition, ...]:
        return tuple(self._benchmarks[key] for key in sorted(self._benchmarks))

    def export_registry_snapshot(self) -> dict[str, Any]:
        return {
            "module": "VB-002",
            "status": "exported",
            "benchmark_count": len(self._benchmarks),
            "benchmarks": tuple(benchmark.snapshot() for benchmark in self.list_benchmarks()),
        }

    def benchmarks(self) -> Mapping[str, BenchmarkDefinition]:
        return MappingProxyType(dict(sorted(self._benchmarks.items())))


def _normalize_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BenchmarkDefinitionError("benchmark_id is required")
    return value.strip()


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return tuple(_normalize(item) for item in value)
    return value
