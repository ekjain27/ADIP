from __future__ import annotations

from typing import Any, Mapping

from platform_integration import (
    DeploymentReadinessLayer,
    EnterpriseApiGateway,
    ObservabilityIntegrationLayer,
    PersistenceIntegrationLayer,
    PlatformIntegrationLayer,
    UnifiedPlatformRuntimeRegistry,
    create_config,
    create_runtime_registry_from_platform_layer,
)

from .baseline_snapshot import BaselineSnapshot, compare_snapshots, create_baseline_snapshot
from .decision_quality_benchmark import DecisionQualityBenchmarkSuite, create_decision_quality_benchmark_suite
from .performance_errors import PerformanceBaselineError, PerformanceBenchmarkDefinitionError
from .performance_profiles import PERFORMANCE_METRICS, PerformanceProfile, get_performance_profile
from .performance_registry import PerformanceBenchmarkDefinition, PerformanceBenchmarkRegistry
from .performance_report import PerformanceScorecard, generate_performance_report, generate_performance_scorecard
from .regression_validator import EndToEndRegressionValidator, create_regression_validator
from .workflow_runner import create_validation_platform_layer

PERFORMANCE_BASELINE_VERSION = "VB-003.1"


class PerformanceBenchmarkHarness:
    MODULE = "VB-003"

    def __init__(
        self,
        profile: str | PerformanceProfile = "standard",
        regression_validator: EndToEndRegressionValidator | None = None,
        quality_benchmark: DecisionQualityBenchmarkSuite | None = None,
        platform_layer: PlatformIntegrationLayer | None = None,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
    ) -> None:
        self.profile = get_performance_profile(profile)
        self.regression_validator = regression_validator or create_regression_validator()
        self.quality_benchmark = quality_benchmark or create_decision_quality_benchmark_suite()
        self.platform_layer = platform_layer or self.regression_validator.platform_layer or create_validation_platform_layer()
        self.runtime_registry = runtime_registry or create_runtime_registry_from_platform_layer(self.platform_layer)
        self.api_gateway = EnterpriseApiGateway(platform_layer=self.platform_layer, runtime_registry=self.runtime_registry)
        self.persistence = PersistenceIntegrationLayer()
        self.observability = ObservabilityIntegrationLayer(
            platform_layer=self.platform_layer,
            runtime_registry=self.runtime_registry,
            api_gateway=self.api_gateway,
            persistence_layer=self.persistence,
        )
        self.deployment = DeploymentReadinessLayer(
            platform_layer=self.platform_layer,
            runtime_registry=self.runtime_registry,
            api_gateway=self.api_gateway,
            config=create_config("test"),
            persistence_layer=self.persistence,
            observability_layer=self.observability,
        )
        self.registry = PerformanceBenchmarkRegistry()
        self._last_scorecards: tuple[PerformanceScorecard, ...] = ()

    def register_performance_benchmark(self, benchmark: PerformanceBenchmarkDefinition) -> PerformanceBenchmarkDefinition:
        return self.registry.register_performance_benchmark(benchmark)

    def execute_performance_benchmark(self, benchmark_id: str, profile: str | PerformanceProfile | None = None) -> dict[str, Any]:
        benchmark = self.registry.get_performance_benchmark(benchmark_id)
        active_profile = get_performance_profile(profile or self.profile)
        execution_output = self._execute_target(benchmark)
        metrics = self.collect_metrics(benchmark, execution_output, active_profile)
        scorecard = generate_performance_scorecard(
            benchmark.benchmark_id,
            active_profile,
            benchmark.target_type,
            benchmark.target,
            metrics,
        )
        self._last_scorecards = tuple(
            sorted(
                tuple(card for card in self._last_scorecards if card.benchmark_id != scorecard.benchmark_id) + (scorecard,),
                key=lambda card: card.benchmark_id,
            )
        )
        return scorecard.to_dict()

    def collect_metrics(
        self,
        benchmark: PerformanceBenchmarkDefinition,
        execution_output: Mapping[str, Any],
        profile: str | PerformanceProfile | None = None,
    ) -> dict[str, float]:
        active_profile = get_performance_profile(profile or self.profile)
        if not isinstance(execution_output, Mapping) or not execution_output:
            raise PerformanceBenchmarkDefinitionError("execution output must be a non-empty mapping")
        complexity = self._payload_complexity(benchmark.payload) + self._payload_complexity(execution_output)
        target_factor = {"module": 1, "platform_component": 2, "workflow": 3}[benchmark.target_type]
        operations = complexity * target_factor * active_profile.iterations * active_profile.workload_multiplier
        execution_time = round(operations / 10.0, 6)
        latency = round(execution_time / active_profile.iterations, 6)
        throughput = round(active_profile.iterations / execution_time, 6) if execution_time else 0.0
        memory_usage = round((complexity + len(str(benchmark.target))) * active_profile.workload_multiplier, 6)
        workflow_duration = round(execution_time * target_factor, 6)
        metrics = {
            "execution_time": execution_time,
            "throughput": throughput,
            "latency": latency,
            "memory_usage": memory_usage,
            "operation_counts": float(operations),
            "workflow_duration": workflow_duration,
        }
        missing = tuple(metric for metric in benchmark.metrics if metric not in metrics)
        if missing:
            raise PerformanceBenchmarkDefinitionError(f"missing collected performance metric(s): {', '.join(missing)}")
        return {metric: metrics[metric] for metric in PERFORMANCE_METRICS}

    def compare_performance_baseline(self, baseline: BaselineSnapshot | None = None) -> dict[str, Any]:
        snapshot = self.export_performance_snapshot()
        expected = baseline or create_baseline_snapshot("vb-003-current", snapshot)
        if expected.payload.get("baseline_version") not in (None, PERFORMANCE_BASELINE_VERSION):
            raise PerformanceBaselineError("incompatible performance baseline version")
        try:
            return compare_snapshots(snapshot, expected)
        except Exception as exc:
            raise PerformanceBaselineError(str(exc)) from exc

    def generate_performance_report(self) -> dict[str, Any]:
        return generate_performance_report(self._scorecards_for_snapshot())

    def export_performance_snapshot(self) -> dict[str, Any]:
        report = self.generate_performance_report()
        return {
            "module": self.MODULE,
            "baseline_version": PERFORMANCE_BASELINE_VERSION,
            "status": report["status"],
            "profile": self.profile.snapshot(),
            "registry": self.registry.export_registry_snapshot(),
            "report": report,
            "regression_summary": self.regression_validator.summarize_results(),
            "quality_summary": self.quality_benchmark.summarize_results(),
            "runtime_registry": self.runtime_registry.export_registry_snapshot(),
            "deployment_snapshot": self.deployment.export_deployment_snapshot(),
        }

    def _scorecards_for_snapshot(self) -> tuple[PerformanceScorecard, ...]:
        if not self._last_scorecards:
            for benchmark in self.registry.list_performance_benchmarks():
                self.execute_performance_benchmark(benchmark.benchmark_id)
        return tuple(sorted(self._last_scorecards, key=lambda card: card.benchmark_id))

    def _execute_target(self, benchmark: PerformanceBenchmarkDefinition) -> Mapping[str, Any]:
        payload = dict(benchmark.payload)
        if benchmark.target_type == "module":
            if benchmark.target == "VB-001":
                return self.regression_validator.execute_workflow("complete_platform_pipeline")
            if benchmark.target == "VB-002":
                return self.quality_benchmark.execute_benchmark("decision-quality-default")
            return self.platform_layer.execute_component(benchmark.target, payload).output_payload
        if benchmark.target_type == "workflow":
            return self.regression_validator.execute_workflow(benchmark.target)
        if benchmark.target_type == "platform_component":
            return self.platform_layer.execute_component(benchmark.target, payload).output_payload
        raise PerformanceBenchmarkDefinitionError(f"invalid performance target_type: {benchmark.target_type}")

    def _payload_complexity(self, value: Any) -> int:
        if isinstance(value, Mapping):
            return 1 + sum(len(str(key)) + self._payload_complexity(item) for key, item in value.items())
        if isinstance(value, (list, tuple)):
            return 1 + sum(self._payload_complexity(item) for item in value)
        return max(1, len(str(value)))


def create_performance_benchmark_harness(profile: str | PerformanceProfile = "standard") -> PerformanceBenchmarkHarness:
    harness = PerformanceBenchmarkHarness(profile=profile)
    harness.register_performance_benchmark(
        PerformanceBenchmarkDefinition(
            benchmark_id="platform-component-die",
            name="DIE platform component performance benchmark",
            target_type="platform_component",
            target="DIE",
            payload={"query": "Measure DIE component", "research": ("R-001", "R-010")},
        )
    )
    harness.register_performance_benchmark(
        PerformanceBenchmarkDefinition(
            benchmark_id="workflow-complete-platform",
            name="Complete platform workflow performance benchmark",
            target_type="workflow",
            target="complete_platform_pipeline",
            payload={"query": "Measure complete platform workflow"},
        )
    )
    harness.register_performance_benchmark(
        PerformanceBenchmarkDefinition(
            benchmark_id="module-quality-suite",
            name="Decision quality suite performance benchmark",
            target_type="module",
            target="VB-002",
            payload={"query": "Measure benchmark module"},
        )
    )
    return harness
