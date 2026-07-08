from __future__ import annotations

from typing import Any

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
from validation import (
    create_decision_quality_benchmark_suite,
    create_enterprise_stress_test_engine,
    create_governance_validation_framework,
    create_performance_benchmark_harness,
    create_regression_validator,
    create_validation_platform_layer,
)

from .api_catalog import generate_api_catalog
from .architecture_documenter import generate_architecture_summary, generate_dependency_graph, generate_integration_catalog
from .documentation_manifest import DOCUMENTATION_BASELINE_VERSION, DocumentationManifest
from .module_catalog import generate_module_catalog


class ArchitectureDocumentationGenerator:
    MODULE = "DOC-001"

    def __init__(
        self,
        platform_layer: PlatformIntegrationLayer | None = None,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
        deployment_readiness: DeploymentReadinessLayer | None = None,
    ) -> None:
        self.platform_layer = platform_layer or create_validation_platform_layer()
        self.runtime_registry = runtime_registry or create_runtime_registry_from_platform_layer(self.platform_layer)
        self.api_gateway = EnterpriseApiGateway(platform_layer=self.platform_layer, runtime_registry=self.runtime_registry)
        self.persistence = PersistenceIntegrationLayer()
        self.observability = ObservabilityIntegrationLayer(
            platform_layer=self.platform_layer,
            runtime_registry=self.runtime_registry,
            api_gateway=self.api_gateway,
            persistence_layer=self.persistence,
        )
        self.deployment_readiness = deployment_readiness or DeploymentReadinessLayer(
            platform_layer=self.platform_layer,
            runtime_registry=self.runtime_registry,
            api_gateway=self.api_gateway,
            config=create_config("test"),
            persistence_layer=self.persistence,
            observability_layer=self.observability,
        )

    def generate_architecture_documentation(self) -> dict[str, Any]:
        validation_summary = self._validation_summary()
        return {
            "module": self.MODULE,
            "status": "generated",
            "architecture_summary": generate_architecture_summary(
                self.runtime_registry,
                self.deployment_readiness,
                validation_summary,
            ),
            "module_catalog": self.generate_module_catalog(),
            "api_catalog": self.generate_api_catalog(),
            "integration_catalog": generate_integration_catalog(self.deployment_readiness, validation_summary),
            "dependency_graph": generate_dependency_graph(self.runtime_registry),
            "runtime_registry": self.runtime_registry.export_registry_snapshot(),
            "validation_summary": validation_summary,
        }

    def generate_module_catalog(self) -> dict[str, Any]:
        return generate_module_catalog(self.runtime_registry)

    def generate_api_catalog(self) -> dict[str, Any]:
        return generate_api_catalog(
            {
                "platform_layer": self.platform_layer,
                "runtime_registry": self.runtime_registry,
                "api_gateway": self.api_gateway,
                "deployment_readiness": self.deployment_readiness,
                "persistence": self.persistence,
                "observability": self.observability,
            }
        )

    def generate_documentation_manifest(self) -> dict[str, Any]:
        documentation = self.generate_architecture_documentation()
        manifest = DocumentationManifest(
            module=self.MODULE,
            baseline_version=DOCUMENTATION_BASELINE_VERSION,
            architecture_summary=documentation["architecture_summary"],
            module_catalog=documentation["module_catalog"],
            api_catalog=documentation["api_catalog"],
            integration_catalog=documentation["integration_catalog"],
            validation_summary=documentation["validation_summary"],
            runtime_registry=documentation["runtime_registry"],
        )
        return manifest.snapshot()

    def export_markdown(self) -> str:
        docs = self.generate_architecture_documentation()
        modules = docs["module_catalog"]["modules"]
        api_components = docs["api_catalog"]["components"]
        lines = [
            "# AI Decision Intelligence Platform - Architecture Overview",
            "",
            f"Module: {self.MODULE}",
            f"Status: {docs['status']}",
            "",
            "## Architecture Summary",
            f"Runtime components: {docs['architecture_summary']['runtime_component_count']}",
            f"Deployment status: {docs['architecture_summary']['deployment_status']}",
            f"Validation status: {docs['architecture_summary']['validation_status']}",
            "",
            "## Module Catalog",
        ]
        lines.extend(f"- {entry['module_id']} ({entry['phase']}): {entry['name']}" for entry in modules)
        lines.extend(["", "## Dependency Graph"])
        lines.extend(f"- {line}" for line in docs["dependency_graph"])
        lines.extend(["", "## API Catalog"])
        lines.extend(f"- {entry['component']}: {', '.join(entry['public_api'])}" for entry in api_components)
        lines.extend(["", "## Integration Points"])
        lines.extend(f"- {point}" for point in docs["integration_catalog"]["integration_points"])
        lines.extend(["", "## Validation Summary"])
        lines.extend(f"- {module}: {status}" for module, status in docs["validation_summary"]["module_statuses"])
        return "\n".join(lines) + "\n"

    def export_json_manifest(self) -> dict[str, Any]:
        return self.generate_documentation_manifest()

    def _validation_summary(self) -> dict[str, Any]:
        regression = create_regression_validator()
        quality = create_decision_quality_benchmark_suite()
        performance = create_performance_benchmark_harness("quick")
        governance = create_governance_validation_framework()
        stress = create_enterprise_stress_test_engine()
        module_statuses = (
            ("VB-001", regression.summarize_results()["status"]),
            ("VB-002", quality.summarize_results()["status"]),
            ("VB-003", performance.generate_performance_report()["status"]),
            ("VB-004", governance.generate_governance_report()["status"]),
            ("VB-005", stress.generate_stress_report()["status"]),
        )
        return {
            "summary_type": "validation_summary",
            "status": "passed" if all(status == "passed" for _, status in module_statuses) else "failed",
            "modules": tuple(module for module, _ in module_statuses),
            "module_statuses": module_statuses,
        }


def create_architecture_documentation_generator() -> ArchitectureDocumentationGenerator:
    return ArchitectureDocumentationGenerator()
