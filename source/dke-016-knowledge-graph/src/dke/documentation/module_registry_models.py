from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from platform_integration import VALID_RUNTIME_PHASES, RuntimeComponentMetadata

from .module_registry_errors import InconsistentPhaseAssignmentError, MissingModuleMetadataError

PHASE_LABELS: Mapping[str, str] = {
    "research": "Research",
    "dke": "DKE",
    "die": "DIE",
    "platform_integration": "Platform Integration",
    "validation_benchmarking": "Validation & Benchmarking",
    "documentation": "Documentation",
    "patent": "Patent",
    "research_paper": "Research Paper",
    "commercial_release": "Commercial Release",
}

PHASE_ORDER = tuple(VALID_RUNTIME_PHASES)


@dataclass(frozen=True)
class ModuleRegistryEntry:
    module_id: str
    module_name: str
    phase: str
    version: str
    status: str
    dependencies: tuple[str, ...]
    public_interfaces: tuple[str, ...]
    description: str

    @classmethod
    def from_runtime_metadata(cls, metadata: RuntimeComponentMetadata) -> "ModuleRegistryEntry":
        if not isinstance(metadata, RuntimeComponentMetadata):
            raise MissingModuleMetadataError("metadata must be RuntimeComponentMetadata")
        public_interfaces = tuple(sorted(dict.fromkeys((*metadata.capabilities, *metadata.contracts.get("provides", ()))))) or ("not declared",)
        return cls(
            module_id=metadata.module_id,
            module_name=metadata.name,
            phase=metadata.phase,
            version=metadata.version,
            status=metadata.status,
            dependencies=metadata.dependencies,
            public_interfaces=public_interfaces,
            description=f"{metadata.name} module in the {PHASE_LABELS[metadata.phase]} phase.",
        )

    def __post_init__(self) -> None:
        required = {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "phase": self.phase,
            "version": self.version,
            "status": self.status,
            "description": self.description,
        }
        missing = tuple(field for field, value in required.items() if not isinstance(value, str) or not value.strip())
        if missing:
            raise MissingModuleMetadataError(f"missing module metadata: {', '.join(missing)}")
        if self.phase not in PHASE_LABELS:
            raise InconsistentPhaseAssignmentError(f"inconsistent phase assignment: {self.phase}")

    def snapshot(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "phase": self.phase,
            "phase_label": PHASE_LABELS[self.phase],
            "version": self.version,
            "status": self.status,
            "dependencies": self.dependencies,
            "public_interfaces": self.public_interfaces,
            "description": self.description,
        }
