from __future__ import annotations

from typing import Any

from .api_documenter import ApiIntegrationDocumentationFramework, create_api_integration_documentation_framework
from .developer_checklist import generate_developer_checklist
from .documentation_generator import ArchitectureDocumentationGenerator, create_architecture_documentation_generator
from .module_registry_documenter import ModuleRegistryDocumenter, create_module_registry_documenter
from .sdk_documenter import SDKDocumenter


class OnboardingDocumentationGenerator:
    def __init__(
        self,
        doc_generator: ArchitectureDocumentationGenerator | None = None,
        module_registry: ModuleRegistryDocumenter | None = None,
        api_framework: ApiIntegrationDocumentationFramework | None = None,
        sdk_documenter: SDKDocumenter | None = None,
    ) -> None:
        self.doc_generator = doc_generator or create_architecture_documentation_generator()
        self.module_registry = module_registry or create_module_registry_documenter(self.doc_generator.runtime_registry)
        self.api_framework = api_framework or create_api_integration_documentation_framework()
        self.sdk_documenter = sdk_documenter or SDKDocumenter(self.api_framework)

    def generate_onboarding_manifest(self) -> dict[str, Any]:
        architecture = self.doc_generator.generate_architecture_documentation()
        registry = self.module_registry.export_registry_json()
        api_docs = self.api_framework.export_api_json()
        sdk_reference = self.sdk_documenter.generate_sdk_reference()
        checklist = generate_developer_checklist()
        return {
            "module": "DOC-004",
            "status": "generated",
            "project_overview": self._project_overview(architecture),
            "architecture_summary": architecture["architecture_summary"],
            "installation_guide": self._installation_guide(),
            "project_structure": self._project_structure(registry),
            "dependency_overview": self._dependency_overview(registry),
            "configuration_guide": self._configuration_guide(),
            "runtime_lifecycle": self._runtime_lifecycle(),
            "extension_guide": self._extension_guide(),
            "troubleshooting_guide": self._troubleshooting_guide(),
            "sdk_reference": sdk_reference,
            "api_documentation": api_docs,
            "developer_checklist": checklist,
            "runtime_registry": self.doc_generator.runtime_registry.export_registry_snapshot(),
            "doc_integrations": ("DOC-001", "DOC-002", "DOC-003", "PI-002"),
        }

    def _project_overview(self, architecture: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": "AI Decision Intelligence Platform - Project-1",
            "status": architecture["status"],
            "runtime_components": architecture["architecture_summary"]["runtime_component_count"],
        }

    def _installation_guide(self) -> tuple[str, ...]:
        return (
            "Create a Python environment with the repository test dependencies.",
            "Use src/dke on PYTHONPATH or rely on pytest.ini for tests.",
            "Run python -m pytest -q to verify deterministic behavior.",
        )

    def _project_structure(self, registry: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        return tuple(
            {
                "phase": phase,
                "modules": tuple(entry["module_id"] for entry in registry["modules_by_phase"][phase]),
            }
            for phase, _ in registry["summary"]["phase_labels"]
        )

    def _dependency_overview(self, registry: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        return tuple(
            {
                "module_id": entry["module_id"],
                "dependencies": entry["dependencies"],
            }
            for phase, _ in registry["summary"]["phase_labels"]
            for entry in registry["modules_by_phase"][phase]
        )

    def _configuration_guide(self) -> tuple[str, ...]:
        return (
            "Use create_config(profile) for local, test, staging, or production profiles.",
            "Use override_config for deterministic test overrides.",
            "Use freeze_config before sharing immutable configuration snapshots.",
        )

    def _runtime_lifecycle(self) -> tuple[str, ...]:
        return (
            "Register platform components through PI-001.",
            "Document runtime metadata through PI-002 snapshots.",
            "Validate deployment readiness through PI-008.",
            "Run VB-001 through VB-005 before release documentation.",
        )

    def _extension_guide(self) -> tuple[str, ...]:
        return (
            "Add new integrations behind platform boundaries.",
            "Register metadata in the runtime registry.",
            "Expose deterministic public APIs and update generated documentation tests.",
        )

    def _troubleshooting_guide(self) -> tuple[str, ...]:
        return (
            "For missing components, inspect PlatformIntegrationLayer.list_components().",
            "For runtime metadata issues, inspect UnifiedPlatformRuntimeRegistry.export_registry_snapshot().",
            "For gateway issues, inspect EnterpriseApiGateway.export_gateway_snapshot().",
        )
