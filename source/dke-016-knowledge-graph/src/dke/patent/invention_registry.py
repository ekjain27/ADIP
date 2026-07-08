from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from platform_integration import UnifiedPlatformRuntimeRegistry

from .innovation_catalog import (
    ARCHITECTURAL_CONTRIBUTIONS,
    INNOVATION_MODULES,
    INNOVATION_TITLES,
    innovation_description,
    novelty_summary,
)
from .patent_errors import DuplicateInnovationError, MissingInnovationMetadataError, UnsupportedInnovationMappingError


@dataclass(frozen=True)
class InnovationRecord:
    innovation_id: str
    title: str
    description: str
    related_modules: tuple[str, ...]
    architectural_contribution: str
    novelty_summary: str

    def __post_init__(self) -> None:
        required = {
            "innovation_id": self.innovation_id,
            "title": self.title,
            "description": self.description,
            "architectural_contribution": self.architectural_contribution,
            "novelty_summary": self.novelty_summary,
        }
        missing = tuple(field for field, value in required.items() if not isinstance(value, str) or not value.strip())
        if missing:
            raise MissingInnovationMetadataError(f"missing innovation metadata: {', '.join(missing)}")
        if not self.related_modules:
            raise MissingInnovationMetadataError("related_modules are required")

    def snapshot(self) -> dict[str, Any]:
        return {
            "innovation_id": self.innovation_id,
            "title": self.title,
            "description": self.description,
            "related_modules": self.related_modules,
            "architectural_contribution": self.architectural_contribution,
            "novelty_summary": self.novelty_summary,
        }


def discover_innovations(runtime_registry: UnifiedPlatformRuntimeRegistry) -> tuple[InnovationRecord, ...]:
    if not isinstance(runtime_registry, UnifiedPlatformRuntimeRegistry):
        raise UnsupportedInnovationMappingError("runtime_registry must be UnifiedPlatformRuntimeRegistry")
    components = {component.module_id: component.snapshot() for component in runtime_registry.list_runtime_components()}
    records: list[InnovationRecord] = []
    for component_id in INNOVATION_MODULES:
        if component_id not in components:
            raise UnsupportedInnovationMappingError(f"innovation module is not registered: {component_id}")
        metadata = components[component_id]
        records.append(
            InnovationRecord(
                innovation_id=f"PAT-001-{component_id}",
                title=INNOVATION_TITLES[component_id],
                description=innovation_description(component_id, metadata),
                related_modules=(component_id,),
                architectural_contribution=ARCHITECTURAL_CONTRIBUTIONS[component_id],
                novelty_summary=novelty_summary(component_id),
            )
        )
    return tuple(sorted(records, key=lambda record: record.innovation_id))


def generate_innovation_registry(innovations: tuple[InnovationRecord, ...]) -> dict[str, Any]:
    validate_innovation_registry(innovations)
    return {
        "module": "PAT-001",
        "registry_type": "innovation_registry",
        "status": "generated",
        "innovation_count": len(innovations),
        "innovations": tuple(record.snapshot() for record in sorted(innovations, key=lambda item: item.innovation_id)),
        "mapped_architecture_modules": INNOVATION_MODULES,
    }


def validate_innovation_registry(innovations: tuple[InnovationRecord, ...]) -> dict[str, Any]:
    seen: set[str] = set()
    for record in innovations:
        if not isinstance(record, InnovationRecord):
            raise MissingInnovationMetadataError("innovation registry entries must be InnovationRecord")
        if record.innovation_id in seen:
            raise DuplicateInnovationError(f"duplicate innovation ID: {record.innovation_id}")
        seen.add(record.innovation_id)
        for module_id in record.related_modules:
            if module_id not in INNOVATION_MODULES:
                raise UnsupportedInnovationMappingError(f"unsupported innovation mapping: {module_id}")
    return {
        "module": "PAT-001",
        "status": "valid",
        "innovation_count": len(innovations),
    }
