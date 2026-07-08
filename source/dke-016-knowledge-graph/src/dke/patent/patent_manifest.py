from __future__ import annotations

from typing import Any

from documentation import (
    create_api_integration_documentation_framework,
    create_architecture_documentation_generator,
    create_developer_guide_framework,
    create_enterprise_deployment_guide_framework,
    create_module_registry_documenter,
)

from .invention_disclosure import export_disclosure_markdown, generate_invention_disclosure
from .invention_registry import InnovationRecord, discover_innovations, generate_innovation_registry, validate_innovation_registry

PATENT_MANIFEST_VERSION = "PAT-001.1"


class PatentPreparationFramework:
    MODULE = "PAT-001"

    def __init__(self) -> None:
        self.doc_001 = create_architecture_documentation_generator()
        self.doc_002 = create_module_registry_documenter(self.doc_001.runtime_registry)
        self.doc_003 = create_api_integration_documentation_framework()
        self.doc_004 = create_developer_guide_framework()
        self.doc_005 = create_enterprise_deployment_guide_framework()
        self.runtime_registry = self.doc_001.runtime_registry

    def discover_innovations(self) -> tuple[InnovationRecord, ...]:
        return discover_innovations(self.runtime_registry)

    def generate_innovation_registry(self) -> dict[str, Any]:
        return generate_innovation_registry(self.discover_innovations())

    def generate_invention_disclosure(self) -> dict[str, Any]:
        return generate_invention_disclosure(self.generate_innovation_registry(), self._documentation_trace())

    def export_patent_manifest(self) -> dict[str, Any]:
        innovations = self.discover_innovations()
        registry = generate_innovation_registry(innovations)
        disclosure = generate_invention_disclosure(registry, self._documentation_trace())
        return {
            "module": self.MODULE,
            "manifest_version": PATENT_MANIFEST_VERSION,
            "status": "generated",
            "innovation_registry": registry,
            "invention_disclosure": disclosure,
            "markdown_disclosure": export_disclosure_markdown(disclosure, innovations),
            "innovation_summary_report": self._innovation_summary(registry),
            "runtime_registry": self.runtime_registry.export_registry_snapshot(),
            "documentation_trace": self._documentation_trace(),
        }

    def validate_innovation_registry(self, innovations: tuple[InnovationRecord, ...] | None = None) -> dict[str, Any]:
        return validate_innovation_registry(innovations or self.discover_innovations())

    def _innovation_summary(self, registry: dict[str, Any]) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "report_type": "innovation_summary",
            "status": "generated",
            "innovation_count": registry["innovation_count"],
            "mapped_modules": registry["mapped_architecture_modules"],
            "documentation_modules": ("DOC-001", "DOC-002", "DOC-003", "DOC-004", "DOC-005"),
        }

    def _documentation_trace(self) -> dict[str, Any]:
        return {
            "DOC-001": self.doc_001.export_json_manifest()["module"],
            "DOC-002": self.doc_002.export_registry_json()["module"],
            "DOC-003": self.doc_003.export_api_json()["module"],
            "DOC-004": self.doc_004.generate_onboarding_manifest()["module"],
            "DOC-005": self.doc_005.generate_deployment_manifest()["module"],
            "PI-002": self.runtime_registry.export_registry_snapshot()["module"],
        }


def create_patent_preparation_framework() -> PatentPreparationFramework:
    return PatentPreparationFramework()
