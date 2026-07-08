from __future__ import annotations

from typing import Any

from platform_integration import RuntimeComponentMetadata, UnifiedPlatformRuntimeRegistry

from .documentation_generator import ArchitectureDocumentationGenerator, create_architecture_documentation_generator
from .module_registry_errors import (
    DuplicateModuleRegistryEntryError,
    MalformedModuleRegistryEntryError,
    MissingModuleMetadataError,
)
from .module_registry_exporter import export_registry_json, export_registry_markdown, registry_entries_to_phase_map
from .module_registry_models import PHASE_LABELS, PHASE_ORDER, ModuleRegistryEntry


class ModuleRegistryDocumenter:
    MODULE = "DOC-002"

    def __init__(
        self,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
        doc_generator: ArchitectureDocumentationGenerator | None = None,
    ) -> None:
        self.doc_generator = doc_generator or create_architecture_documentation_generator()
        self.runtime_registry = runtime_registry or self.doc_generator.runtime_registry

    def generate_module_registry(self) -> dict[str, Any]:
        entries = self._discover_entries()
        registry = {
            "module": self.MODULE,
            "status": "generated",
            "modules_by_phase": registry_entries_to_phase_map(entries),
            "summary": self.generate_phase_summary(entries),
            "statistics": self._statistics(entries),
            "doc_001_manifest": self.doc_generator.export_json_manifest(),
        }
        self.validate_registry_documentation(registry)
        return registry

    def generate_phase_summary(self, entries: tuple[ModuleRegistryEntry, ...] | None = None) -> dict[str, Any]:
        active_entries = entries or self._discover_entries()
        phase_counts = {
            phase: sum(1 for entry in active_entries if entry.phase == phase)
            for phase in PHASE_ORDER
        }
        return {
            "summary_type": "module_registry_summary",
            "phase_counts": tuple((phase, phase_counts[phase]) for phase in PHASE_ORDER),
            "phase_labels": tuple((phase, PHASE_LABELS[phase]) for phase in PHASE_ORDER),
            "non_empty_phases": tuple(phase for phase in PHASE_ORDER if phase_counts[phase] > 0),
        }

    def export_registry_markdown(self) -> str:
        return export_registry_markdown(self.generate_module_registry())

    def export_registry_json(self) -> dict[str, Any]:
        return export_registry_json(self.generate_module_registry())

    def validate_registry_documentation(self, registry: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(registry, dict) or registry.get("module") != self.MODULE:
            raise MalformedModuleRegistryEntryError("registry documentation must be a DOC-002 mapping")
        seen: set[str] = set()
        for phase in PHASE_ORDER:
            entries = registry["modules_by_phase"].get(phase, ())
            for entry in entries:
                module_id = entry.get("module_id")
                if module_id in seen:
                    raise DuplicateModuleRegistryEntryError(f"duplicate module ID in registry documentation: {module_id}")
                seen.add(module_id)
                required = ("module_id", "module_name", "phase", "version", "status", "dependencies", "public_interfaces", "description")
                missing = tuple(field for field in required if field not in entry or entry[field] in (None, ""))
                if missing:
                    raise MissingModuleMetadataError(f"missing module metadata: {', '.join(missing)}")
                if entry["phase"] != phase:
                    raise MalformedModuleRegistryEntryError(f"malformed registry entry phase: {entry['module_id']}")
        if len(seen) != registry["statistics"]["module_count"]:
            raise MalformedModuleRegistryEntryError("registry statistics do not match module entries")
        return {
            "module": self.MODULE,
            "status": "valid",
            "module_count": len(seen),
        }

    def _discover_entries(self) -> tuple[ModuleRegistryEntry, ...]:
        entries = [ModuleRegistryEntry.from_runtime_metadata(component) for component in self.runtime_registry.list_runtime_components()]
        entries.extend(self._documentation_entries())
        seen: set[str] = set()
        for entry in entries:
            if entry.module_id in seen:
                raise DuplicateModuleRegistryEntryError(f"duplicate module ID in registry documentation: {entry.module_id}")
            seen.add(entry.module_id)
        return tuple(sorted(entries, key=lambda entry: (PHASE_ORDER.index(entry.phase), entry.module_id)))

    def _documentation_entries(self) -> tuple[ModuleRegistryEntry, ...]:
        metadata = (
            RuntimeComponentMetadata(
                module_id="DOC-001",
                name="Architecture Overview and System Documentation",
                phase="documentation",
                capabilities=("architecture_documentation", "markdown_export", "json_manifest"),
                contracts={"provides": ("documentation_generation",)},
            ),
            RuntimeComponentMetadata(
                module_id="DOC-002",
                name="Module Registry Documentation",
                phase="documentation",
                dependencies=("DOC-001",),
                capabilities=("module_registry_documentation", "registry_markdown", "registry_json"),
                contracts={"provides": ("module_registry_documentation",), "requires": ("documentation_generation",)},
            ),
        )
        return tuple(ModuleRegistryEntry.from_runtime_metadata(item) for item in metadata)

    def _statistics(self, entries: tuple[ModuleRegistryEntry, ...]) -> dict[str, Any]:
        phase_counts = {
            phase: sum(1 for entry in entries if entry.phase == phase)
            for phase in PHASE_ORDER
        }
        return {
            "module_count": len(entries),
            "phase_count": len(PHASE_ORDER),
            "registered_phase_count": sum(1 for count in phase_counts.values() if count > 0),
            "phase_counts": tuple((phase, phase_counts[phase]) for phase in PHASE_ORDER),
        }


def create_module_registry_documenter(
    runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
) -> ModuleRegistryDocumenter:
    return ModuleRegistryDocumenter(runtime_registry=runtime_registry)
