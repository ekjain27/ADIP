from __future__ import annotations

from typing import Any, Mapping

from platform_integration import (
    EnterpriseApiGateway,
    ObservabilityIntegrationLayer,
    PersistenceIntegrationLayer,
    create_config,
    create_runtime_registry_from_platform_layer,
)

from .baseline_snapshot import BaselineSnapshot, compare_snapshots, create_baseline_snapshot
from .regression_report import generate_report, summarize_report
from .validation_errors import IncompatibleContractError, NonDeterministicOutputError
from .workflow_runner import WorkflowRunner, create_validation_platform_layer


class EndToEndRegressionValidator:
    MODULE = "VB-001"

    def __init__(self, workflow_runner: WorkflowRunner | None = None) -> None:
        self.workflow_runner = workflow_runner or WorkflowRunner()
        self.platform_layer = self.workflow_runner.platform_layer
        self.runtime_registry = create_runtime_registry_from_platform_layer(self.platform_layer)
        self.api_gateway = EnterpriseApiGateway(platform_layer=self.platform_layer, runtime_registry=self.runtime_registry)
        self.persistence = PersistenceIntegrationLayer()
        self.observability = ObservabilityIntegrationLayer(
            platform_layer=self.platform_layer,
            runtime_registry=self.runtime_registry,
            api_gateway=self.api_gateway,
            persistence_layer=self.persistence,
        )
        self.config = create_config("test")
        self._last_results: tuple[dict[str, Any], ...] = ()

    def execute_full_regression(self) -> dict[str, Any]:
        results = tuple(self.execute_workflow(name) for name in self.workflow_runner.workflow_names())
        self._last_results = results
        self._validate_determinism(results)
        self._validate_contracts()
        self.observability.log_event("INFO", "full regression executed", {"workflow_count": len(results)})
        return self.generate_validation_report()

    def execute_workflow(self, name: str) -> dict[str, Any]:
        first = self.workflow_runner.execute_workflow(name).to_dict()
        second = self.workflow_runner.execute_workflow(name).to_dict()
        if first != second:
            raise NonDeterministicOutputError(f"workflow output is non-deterministic: {name}")
        return first

    def compare_against_baseline(self, baseline: BaselineSnapshot | None = None) -> dict[str, Any]:
        snapshot = self.export_regression_snapshot()
        expected = baseline or create_baseline_snapshot("vb-001-current", snapshot)
        return compare_snapshots(snapshot, expected)

    def generate_validation_report(self) -> dict[str, Any]:
        results = self._last_results or tuple(self.execute_workflow(name) for name in self.workflow_runner.workflow_names())
        return generate_report(results)

    def export_regression_snapshot(self) -> dict[str, Any]:
        report = self.generate_validation_report()
        return {
            "module": self.MODULE,
            "status": report["status"],
            "report": report,
            "runtime_registry": self.runtime_registry.export_registry_snapshot(),
            "api_gateway": self.api_gateway.export_gateway_snapshot(),
            "persistence": self.persistence.export_persistence_snapshot(),
            "observability": self.observability.export_observability_snapshot(),
            "baseline_ready": True,
        }

    def summarize_results(self) -> dict[str, Any]:
        return summarize_report(self.generate_validation_report())

    def _validate_determinism(self, results: tuple[Mapping[str, Any], ...]) -> None:
        names = tuple(result["name"] for result in results)
        if names != tuple(sorted(names)):
            raise NonDeterministicOutputError("workflow result ordering is non-deterministic")

    def _validate_contracts(self) -> None:
        validation = self.platform_layer.validate_platform(required_components=self.platform_layer.list_components())
        if validation["status"] != "valid":
            raise IncompatibleContractError("platform contracts are not valid")


def create_regression_validator() -> EndToEndRegressionValidator:
    return EndToEndRegressionValidator(WorkflowRunner(create_validation_platform_layer()))
