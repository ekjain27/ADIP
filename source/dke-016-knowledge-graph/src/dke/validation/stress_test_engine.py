from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from platform_integration import PlatformIntegrationLayer, UnifiedPlatformRuntimeRegistry, create_runtime_registry_from_platform_layer

from .baseline_snapshot import BaselineSnapshot, compare_snapshots, create_baseline_snapshot
from .decision_quality_benchmark import DecisionQualityBenchmarkSuite, create_decision_quality_benchmark_suite
from .failure_simulator import FailureSimulator, SUPPORTED_FAILURE_MODES
from .governance_validator import GovernanceProvenanceValidationFramework, create_governance_validation_framework
from .performance_benchmark import PerformanceBenchmarkHarness, create_performance_benchmark_harness
from .resilience_scorecard import ResilienceScorecard, generate_resilience_scorecard
from .regression_validator import EndToEndRegressionValidator, create_regression_validator
from .stress_errors import (
    DuplicateStressScenarioError,
    MalformedWorkloadError,
    StressBaselineError,
    StressScenarioDefinitionError,
    UnsupportedFailureSimulationError,
)
from .stress_report import generate_stress_report
from .workflow_runner import create_validation_platform_layer

STRESS_BASELINE_VERSION = "VB-005.1"
STRESS_SCENARIO_TYPES = (
    "high_workflow_volume",
    "repeated_execution",
    "large_payload_handling",
    "concurrent_execution_simulation",
    "component_unavailability",
    "dependency_failure",
)


@dataclass(frozen=True)
class StressScenarioDefinition:
    scenario_id: str
    name: str
    scenario_type: str
    workload: Mapping[str, Any]
    target: str = "complete_platform_pipeline"
    failure_mode: str = "none"
    retry_attempts: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.scenario_id, str) or not self.scenario_id.strip():
            raise StressScenarioDefinitionError("scenario_id is required")
        if not isinstance(self.name, str) or not self.name.strip():
            raise StressScenarioDefinitionError("scenario name is required")
        if self.scenario_type not in STRESS_SCENARIO_TYPES:
            raise StressScenarioDefinitionError(f"invalid stress scenario type: {self.scenario_type}")
        if not isinstance(self.workload, Mapping) or not self.workload:
            raise MalformedWorkloadError("stress workload must be a non-empty mapping")
        if self.failure_mode not in SUPPORTED_FAILURE_MODES:
            raise UnsupportedFailureSimulationError(f"unsupported failure simulation: {self.failure_mode}")
        if not isinstance(self.retry_attempts, int) or self.retry_attempts < 0:
            raise StressScenarioDefinitionError("retry_attempts must be a non-negative integer")

    def snapshot(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "scenario_type": self.scenario_type,
            "workload": _normalize(self.workload),
            "target": self.target,
            "failure_mode": self.failure_mode,
            "retry_attempts": self.retry_attempts,
        }


class EnterpriseStressTestEngine:
    MODULE = "VB-005"

    def __init__(
        self,
        regression_validator: EndToEndRegressionValidator | None = None,
        quality_benchmark: DecisionQualityBenchmarkSuite | None = None,
        performance_harness: PerformanceBenchmarkHarness | None = None,
        governance_framework: GovernanceProvenanceValidationFramework | None = None,
        platform_layer: PlatformIntegrationLayer | None = None,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
    ) -> None:
        self.regression_validator = regression_validator or create_regression_validator()
        self.quality_benchmark = quality_benchmark or create_decision_quality_benchmark_suite()
        self.performance_harness = performance_harness or create_performance_benchmark_harness("quick")
        self.governance_framework = governance_framework or create_governance_validation_framework()
        self.platform_layer = platform_layer or self.regression_validator.platform_layer or create_validation_platform_layer()
        self.runtime_registry = runtime_registry or create_runtime_registry_from_platform_layer(self.platform_layer)
        self.failure_simulator = FailureSimulator()
        self._scenarios: dict[str, StressScenarioDefinition] = {}
        self._executions: dict[str, dict[str, Any]] = {}
        self._scorecards: dict[str, ResilienceScorecard] = {}

    def register_stress_scenario(self, scenario: StressScenarioDefinition) -> StressScenarioDefinition:
        if not isinstance(scenario, StressScenarioDefinition):
            raise StressScenarioDefinitionError("scenario must be StressScenarioDefinition")
        if scenario.scenario_id in self._scenarios:
            raise DuplicateStressScenarioError(f"stress scenario already registered: {scenario.scenario_id}")
        self._scenarios[scenario.scenario_id] = scenario
        return scenario

    def execute_stress_test(self, scenario_id: str) -> dict[str, Any]:
        scenario = self._get_scenario(scenario_id)
        failure = self.simulate_failure(scenario.failure_mode, scenario.target, scenario.retry_attempts)
        workload_units = self._workload_units(scenario)
        execution = {
            "scenario_id": scenario.scenario_id,
            "scenario_type": scenario.scenario_type,
            "target": scenario.target,
            "status": "completed",
            "workload_units": workload_units,
            "operation_count": workload_units * self._scenario_factor(scenario),
            "failure": failure,
            "platform_status": "stable" if failure["mode"] == "none" else "degraded",
            "recovered": failure["recovery_action"] in {"not_required", "fallback_route", "retry_then_recover"},
        }
        scorecard = self.evaluate_resilience(execution)
        self._executions[scenario.scenario_id] = execution
        self._scorecards[scenario.scenario_id] = scorecard
        return {**execution, "scorecard": scorecard.to_dict()}

    def simulate_failure(self, mode: str, target: str = "platform", retry_attempts: int = 1) -> dict[str, Any]:
        return self.failure_simulator.simulate_failure(mode, target, retry_attempts).to_dict()

    def evaluate_resilience(self, execution: Mapping[str, Any]) -> ResilienceScorecard:
        failure = execution["failure"]
        has_failure = failure["mode"] != "none"
        metrics = {
            "graceful_degradation": 1.0 if not has_failure or execution["platform_status"] == "degraded" else 0.0,
            "error_propagation": 1.0 if not has_failure or bool(failure["error"]) else 0.0,
            "recovery_behavior": 1.0 if execution["recovered"] else 0.0,
            "retry_policy_behavior": 1.0 if not has_failure or failure["retry_attempts"] >= 1 else 0.0,
            "platform_stability": 1.0 if execution["status"] == "completed" else 0.0,
        }
        return generate_resilience_scorecard(str(execution["scenario_id"]), metrics)

    def generate_resilience_scorecard(self, scenario_id: str) -> dict[str, Any]:
        if scenario_id not in self._scorecards:
            self.execute_stress_test(scenario_id)
        return self._scorecards[scenario_id].to_dict()

    def generate_stress_report(self) -> dict[str, Any]:
        self._ensure_all_executed()
        return generate_stress_report(
            tuple(self._scorecards[key] for key in sorted(self._scorecards)),
            tuple(self._executions[key] for key in sorted(self._executions)),
        )

    def compare_stress_baseline(self, baseline: BaselineSnapshot | None = None) -> dict[str, Any]:
        snapshot = self.export_stress_snapshot()
        expected = baseline or create_baseline_snapshot("vb-005-current", snapshot)
        if expected.payload.get("baseline_version") not in (None, STRESS_BASELINE_VERSION):
            raise StressBaselineError("inconsistent stress baseline version")
        try:
            return compare_snapshots(snapshot, expected)
        except Exception as exc:
            raise StressBaselineError(str(exc)) from exc

    def export_stress_snapshot(self) -> dict[str, Any]:
        report = self.generate_stress_report()
        return {
            "module": self.MODULE,
            "baseline_version": STRESS_BASELINE_VERSION,
            "status": report["status"],
            "scenarios": tuple(self._scenarios[key].snapshot() for key in sorted(self._scenarios)),
            "report": report,
            "regression_summary": self.regression_validator.summarize_results(),
            "quality_summary": self.quality_benchmark.summarize_results(),
            "performance_summary": self.performance_harness.generate_performance_report(),
            "governance_summary": self.governance_framework.generate_governance_report(),
            "runtime_registry": self.runtime_registry.export_registry_snapshot(),
            "validation_phase_complete": True,
        }

    def scenarios(self) -> Mapping[str, StressScenarioDefinition]:
        return MappingProxyType(dict(sorted(self._scenarios.items())))

    def _ensure_all_executed(self) -> None:
        for scenario_id in sorted(self._scenarios):
            if scenario_id not in self._executions:
                self.execute_stress_test(scenario_id)

    def _get_scenario(self, scenario_id: str) -> StressScenarioDefinition:
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            raise StressScenarioDefinitionError("scenario_id is required")
        try:
            return self._scenarios[scenario_id.strip()]
        except KeyError as exc:
            raise StressScenarioDefinitionError(f"stress scenario is not registered: {scenario_id}") from exc

    def _workload_units(self, scenario: StressScenarioDefinition) -> int:
        units = scenario.workload.get("units", 1)
        if not isinstance(units, int) or units <= 0:
            raise MalformedWorkloadError("stress workload units must be a positive integer")
        payload_size = scenario.workload.get("payload_size", 1)
        if not isinstance(payload_size, int) or payload_size <= 0:
            raise MalformedWorkloadError("stress workload payload_size must be a positive integer")
        return units * payload_size

    def _scenario_factor(self, scenario: StressScenarioDefinition) -> int:
        return {
            "high_workflow_volume": 5,
            "repeated_execution": 3,
            "large_payload_handling": 4,
            "concurrent_execution_simulation": 6,
            "component_unavailability": 2,
            "dependency_failure": 2,
        }[scenario.scenario_type]


def create_enterprise_stress_test_engine() -> EnterpriseStressTestEngine:
    engine = EnterpriseStressTestEngine()
    for scenario in (
        StressScenarioDefinition("high-volume", "High workflow volume", "high_workflow_volume", {"units": 10, "payload_size": 1}),
        StressScenarioDefinition("repeated-execution", "Repeated execution", "repeated_execution", {"units": 5, "payload_size": 1}),
        StressScenarioDefinition("large-payload", "Large payload handling", "large_payload_handling", {"units": 2, "payload_size": 8}),
        StressScenarioDefinition("concurrent-simulation", "Deterministic concurrent execution simulation", "concurrent_execution_simulation", {"units": 4, "payload_size": 2}),
        StressScenarioDefinition("component-unavailable", "Component unavailability", "component_unavailability", {"units": 1, "payload_size": 1}, target="DIE", failure_mode="component_unavailable"),
        StressScenarioDefinition("dependency-failure", "Dependency failure", "dependency_failure", {"units": 1, "payload_size": 1}, target="DKE", failure_mode="dependency_failure", retry_attempts=2),
    ):
        engine.register_stress_scenario(scenario)
    return engine


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return tuple(_normalize(item) for item in value)
    return value
