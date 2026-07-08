from __future__ import annotations

from typing import Any

from .developer_checklist import generate_developer_checklist
from .developer_errors import (
    DuplicateGuideSectionError,
    InconsistentDependencyGraphError,
    MalformedApiReferenceError,
    UndocumentedPublicModuleError,
)
from .onboarding_generator import OnboardingDocumentationGenerator
from .sdk_documenter import SDKDocumenter

GUIDE_SECTIONS = (
    "project_overview",
    "architecture_summary",
    "installation_guide",
    "project_structure",
    "dependency_overview",
    "configuration_guide",
    "runtime_lifecycle",
    "extension_guide",
    "troubleshooting_guide",
    "sdk_reference",
)


class DeveloperGuideFramework:
    MODULE = "DOC-004"

    def __init__(self, onboarding_generator: OnboardingDocumentationGenerator | None = None) -> None:
        self.onboarding_generator = onboarding_generator or OnboardingDocumentationGenerator()
        self.sdk_documenter = self.onboarding_generator.sdk_documenter

    def generate_developer_guide(self) -> dict[str, Any]:
        manifest = self.generate_onboarding_manifest()
        guide = {
            "module": self.MODULE,
            "status": "generated",
            "sections": tuple((section, manifest[section]) for section in GUIDE_SECTIONS),
            "developer_checklist": manifest["developer_checklist"],
        }
        self.validate_developer_documentation(guide)
        return guide

    def generate_sdk_reference(self) -> dict[str, Any]:
        return self.sdk_documenter.generate_sdk_reference()

    def generate_onboarding_manifest(self) -> dict[str, Any]:
        return self.onboarding_generator.generate_onboarding_manifest()

    def generate_developer_checklist(self) -> dict[str, Any]:
        return generate_developer_checklist()

    def export_developer_markdown(self) -> str:
        guide = self.generate_developer_guide()
        lines = ["# Project-1 Developer Onboarding & SDK Guide", "", f"Module: {self.MODULE}", ""]
        for section, payload in guide["sections"]:
            lines.extend([f"## {section.replace('_', ' ').title()}", ""])
            lines.extend(self._section_lines(payload))
            lines.append("")
        lines.extend(["## Developer Checklist", ""])
        for item in guide["developer_checklist"]["items"]:
            lines.append(f"- [ ] {item['description']}")
        return "\n".join(lines) + "\n"

    def validate_developer_documentation(self, guide: dict[str, Any] | None = None) -> dict[str, Any]:
        active_guide = guide or self.generate_developer_guide()
        sections = tuple(section for section, _ in active_guide["sections"])
        duplicates = tuple(section for section in sections if sections.count(section) > 1)
        if duplicates:
            raise DuplicateGuideSectionError(f"duplicate guide section(s): {', '.join(sorted(set(duplicates)))}")
        missing_sections = tuple(section for section in GUIDE_SECTIONS if section not in sections)
        if missing_sections:
            raise UndocumentedPublicModuleError(f"undocumented public module section(s): {', '.join(missing_sections)}")
        dependency_overview = dict(
            (entry["module_id"], tuple(entry["dependencies"]))
            for section, payload in active_guide["sections"]
            if section == "dependency_overview"
            for entry in payload
        )
        for module_id, dependencies in dependency_overview.items():
            if module_id in dependencies:
                raise InconsistentDependencyGraphError(f"inconsistent dependency graph for {module_id}")
        sdk_reference = dict(active_guide["sections"])["sdk_reference"]
        if not sdk_reference.get("components"):
            raise MalformedApiReferenceError("malformed API reference: no SDK components")
        return {
            "module": self.MODULE,
            "status": "valid",
            "section_count": len(sections),
            "sdk_component_count": sdk_reference["component_count"],
        }

    def _section_lines(self, payload: Any) -> list[str]:
        if isinstance(payload, dict):
            return [f"- {key}: {payload[key]}" for key in sorted(payload)]
        if isinstance(payload, tuple):
            lines: list[str] = []
            for item in payload:
                if isinstance(item, dict):
                    label = item.get("component") or item.get("module_id") or item.get("phase") or item.get("id") or "item"
                    lines.append(f"- {label}: {item}")
                else:
                    lines.append(f"- {item}")
            return lines
        return [f"- {payload}"]


def create_developer_guide_framework() -> DeveloperGuideFramework:
    return DeveloperGuideFramework()
