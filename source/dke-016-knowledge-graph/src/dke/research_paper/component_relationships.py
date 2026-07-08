from __future__ import annotations

from typing import Any

from .architecture_composer import generate_architecture_description, validate_architecture_description
from .methodology_errors import DuplicateArchitectureIdError, InconsistentArchitectureMappingError, UndocumentedComponentError

RELATIONSHIP_VERSION = "RP-003.1"

EXECUTION_SEQUENCE = ("DKE", "DIE", "DPG", "DDGM", "TDLL", "ADBM", "ADWG", "DHMF", "DRIF", "EDOF")


def generate_component_relationships(architecture: dict[str, Any] | None = None) -> dict[str, Any]:
    active_architecture = architecture or generate_architecture_description()
    validate_architecture_description(active_architecture)
    components = tuple(component["component_id"] for component in active_architecture["component_registry"]["components"])
    matrix = _interaction_matrix(components)
    report = {
        "module": "RP-003",
        "relationship_version": RELATIONSHIP_VERSION,
        "status": "generated",
        "component_ids": components,
        "interaction_matrix": matrix,
        "execution_sequence": tuple(
            {
                "sequence_number": index,
                "component_id": component_id,
                "role": _component_role(active_architecture, component_id),
            }
            for index, component_id in enumerate(EXECUTION_SEQUENCE, start=1)
        ),
        "relationship_report": {
            "component_count": len(components),
            "directed_interaction_count": sum(1 for row in matrix for cell in row["relations"] if cell["relationship"] != "none"),
            "orphan_components": (),
        },
    }
    validate_component_relationships(report)
    return report


def validate_component_relationships(report: dict[str, Any]) -> dict[str, Any]:
    component_ids = tuple(report["component_ids"])
    if len(component_ids) != len(set(component_ids)):
        raise DuplicateArchitectureIdError("duplicate relationship component IDs are not allowed")
    sequence_ids = tuple(step["component_id"] for step in report["execution_sequence"])
    unknown = tuple(component_id for component_id in sequence_ids if component_id not in component_ids)
    if unknown:
        raise InconsistentArchitectureMappingError(f"execution sequence references unknown components: {unknown}")
    matrix_sources = tuple(row["source_component_id"] for row in report["interaction_matrix"])
    if tuple(sorted(matrix_sources)) != matrix_sources or set(matrix_sources) != set(component_ids):
        raise InconsistentArchitectureMappingError("interaction matrix source components are inconsistent")
    related = set(sequence_ids)
    missing = tuple(sorted(set(component_ids) - related))
    if missing:
        raise UndocumentedComponentError(f"orphan component(s) are not documented by execution sequence: {missing}")
    return {
        "module": "RP-003",
        "status": "valid",
        "component_count": len(component_ids),
        "sequence_length": len(sequence_ids),
    }


def _interaction_matrix(component_ids: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    adjacency = {(source, target) for source, target in zip(EXECUTION_SEQUENCE, EXECUTION_SEQUENCE[1:])}
    return tuple(
        {
            "source_component_id": source,
            "relations": tuple(
                {
                    "target_component_id": target,
                    "relationship": _relationship(source, target, adjacency),
                }
                for target in component_ids
            ),
        }
        for source in component_ids
    )


def _relationship(source: str, target: str, adjacency: set[tuple[str, str]]) -> str:
    if source == target:
        return "self"
    if (source, target) in adjacency:
        return "invokes_next"
    if (target, source) in adjacency:
        return "receives_from_previous"
    return "none"


def _component_role(architecture: dict[str, Any], component_id: str) -> str:
    components = {
        component["component_id"]: component
        for component in architecture["component_registry"]["components"]
    }
    return components[component_id]["description"]
