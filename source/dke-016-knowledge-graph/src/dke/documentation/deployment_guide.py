from __future__ import annotations

from typing import Any

from .api_documenter import create_api_integration_documentation_framework
from .deployment_manifest_generator import generate_deployment_manifest, validate_deployment_manifest
from .developer_guide import DeveloperGuideFramework, create_developer_guide_framework
from .documentation_generator import ArchitectureDocumentationGenerator, create_architecture_documentation_generator
from .environment_documenter import EnvironmentDocumenter
from .maintenance_documenter import generate_maintenance_checklist, generate_maintenance_plan, generate_operational_checklist
from .module_registry_documenter import create_module_registry_documenter
from .operations_errors import DuplicateOperationalProcedureError
from .operations_manual import OPERATIONAL_PROCEDURES, export_operations_markdown, generate_operations_manual_content


class EnterpriseDeploymentGuideFramework:
    MODULE = "DOC-005"

    def __init__(
        self,
        doc_generator: ArchitectureDocumentationGenerator | None = None,
        developer_guide: DeveloperGuideFramework | None = None,
    ) -> None:
        self.doc_generator = doc_generator or create_architecture_documentation_generator()
        self.module_registry = create_module_registry_documenter(self.doc_generator.runtime_registry)
        self.api_documentation = create_api_integration_documentation_framework()
        self.developer_guide = developer_guide or create_developer_guide_framework()
        self.environment_documenter = EnvironmentDocumenter()

    def generate_deployment_guide(self) -> dict[str, Any]:
        manual = self.generate_operations_manual()
        manifest = self.generate_deployment_manifest()
        return {
            "module": self.MODULE,
            "status": "generated",
            "deployment_manifest": manifest,
            "operations_manual": manual,
            "environment_readiness_report": self.generate_environment_readiness_report(),
            "operational_checklist": self.generate_operational_checklist(),
            "maintenance_checklist": generate_maintenance_checklist(),
        }

    def generate_operations_manual(self) -> dict[str, Any]:
        context = {
            "environments": tuple(item["environment"] for item in self.generate_environment_documentation()["environments"]),
            "maintenance_plan": self.generate_maintenance_plan(),
        }
        return generate_operations_manual_content(context)

    def generate_environment_documentation(self, environment: str | None = None) -> dict[str, Any]:
        return self.environment_documenter.generate_environment_documentation(environment)

    def generate_maintenance_plan(self) -> dict[str, Any]:
        return generate_maintenance_plan()

    def generate_deployment_manifest(self) -> dict[str, Any]:
        return generate_deployment_manifest(
            self.doc_generator.export_json_manifest(),
            self.developer_guide.generate_onboarding_manifest(),
            self.generate_environment_documentation(),
            self.generate_environment_readiness_report(),
        )

    def generate_operational_checklist(self) -> dict[str, Any]:
        return generate_operational_checklist()

    def generate_environment_readiness_report(self) -> dict[str, Any]:
        return self.environment_documenter.generate_environment_readiness_report(self.doc_generator.deployment_readiness)

    def export_operations_markdown(self) -> str:
        return export_operations_markdown(self.generate_operations_manual(), self.generate_deployment_manifest())

    def validate_operations_documentation(self, guide: dict[str, Any] | None = None) -> dict[str, Any]:
        active_guide = guide or self.generate_deployment_guide()
        manual = active_guide["operations_manual"]
        procedure_ids = tuple(procedure["id"] for procedure in manual["procedures"])
        duplicates = tuple(procedure for procedure in procedure_ids if procedure_ids.count(procedure) > 1)
        if duplicates:
            raise DuplicateOperationalProcedureError(f"duplicate operational procedure(s): {', '.join(sorted(set(duplicates)))}")
        missing = tuple(procedure for procedure in OPERATIONAL_PROCEDURES if procedure not in procedure_ids)
        if missing:
            raise DuplicateOperationalProcedureError(f"missing operational procedure(s): {', '.join(missing)}")
        manifest_validation = validate_deployment_manifest(active_guide["deployment_manifest"])
        return {
            "module": self.MODULE,
            "status": "valid",
            "procedure_count": len(procedure_ids),
            "manifest": manifest_validation,
        }


def create_enterprise_deployment_guide_framework() -> EnterpriseDeploymentGuideFramework:
    return EnterpriseDeploymentGuideFramework()
