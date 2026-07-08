from __future__ import annotations

from typing import Any

from documentation import create_architecture_documentation_generator
from platform_integration import default_platform_contracts

from .methodology_errors import (
    DuplicateArchitectureIdError,
    InconsistentArchitectureMappingError,
    TerminologyConsistencyError,
    UndocumentedComponentError,
)

ARCHITECTURE_DESCRIPTION_VERSION = "RP-003.1"

LAYER_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "layer_id": "knowledge_context_layer",
        "name": "Knowledge Context Layer",
        "component_ids": ("DKE",),
        "description": "Implemented context retrieval boundary supplied by the DKE platform contract.",
    },
    {
        "layer_id": "decision_intelligence_layer",
        "name": "Decision Intelligence Layer",
        "component_ids": ("DIE",),
        "description": "Implemented decision processing boundary supplied by the DIE platform contract.",
    },
    {
        "layer_id": "governance_provenance_layer",
        "name": "Governance And Provenance Layer",
        "component_ids": ("DDGM", "DPG", "TDLL"),
        "description": "Implemented governance evaluation, provenance graph, and temporal lineage boundaries.",
    },
    {
        "layer_id": "adaptive_workflow_layer",
        "name": "Adaptive Workflow Layer",
        "component_ids": ("ADBM", "ADWG", "EDOF"),
        "description": "Implemented adaptive behavior, workflow orchestration, and enterprise orchestration boundaries.",
    },
    {
        "layer_id": "monitoring_delivery_layer",
        "name": "Monitoring And Delivery Layer",
        "component_ids": ("DHMF", "DRIF"),
        "description": "Implemented health monitoring and recommendation interface boundaries.",
    },
)

IMPLEMENTED_SCOPE_MODULES = {
    "requirements": tuple(f"R-{index:03d}" for index in range(1, 11)),
    "knowledge_engineering": tuple(f"DKE-{index:03d}" for index in range(1, 21)),
    "decision_intelligence": tuple(f"DIE-{index:03d}" for index in range(1, 21)),
    "platform_integration": tuple(f"PI-{index:03d}" for index in range(1, 9)),
    "validation_benchmarking": tuple(f"VB-{index:03d}" for index in range(1, 6)),
    "documentation": tuple(f"DOC-{index:03d}" for index in range(1, 6)),
    "patent_support": tuple(f"PAT-{index:03d}" for index in range(1, 5)),
    "research_paper": ("RP-001", "RP-002", "RP-003"),
}


def generate_architecture_description(documentation: dict[str, Any] | None = None) -> dict[str, Any]:
    docs = documentation or create_architecture_documentation_generator().generate_architecture_documentation()
    runtime_registry = docs["runtime_registry"]
    component_registry = _component_registry(runtime_registry)
    architecture = {
        "module": "RP-003",
        "description_version": ARCHITECTURE_DESCRIPTION_VERSION,
        "status": "generated",
        "platform": docs["architecture_summary"]["platform"],
        "architecture_summary": {
            "runtime_component_count": docs["architecture_summary"]["runtime_component_count"],
            "deployment_status": docs["architecture_summary"]["deployment_status"],
            "validation_status": docs["architecture_summary"]["validation_status"],
            "implemented_scope_only": True,
        },
        "component_registry": component_registry,
        "layered_architecture": _layered_architecture(component_registry["components"]),
        "module_hierarchy": _module_hierarchy(),
        "runtime_lifecycle": _runtime_lifecycle(),
        "architecture_glossary": generate_architecture_glossary(component_registry),
        "source_evidence": {
            "documentation_module": docs["module"],
            "runtime_registry_module": runtime_registry["module"],
            "dependency_graph": docs["dependency_graph"],
            "integration_points": docs["integration_catalog"]["integration_points"],
        },
        "integrity": {
            "algorithms_fabricated": False,
            "equations_fabricated": False,
            "system_capabilities_fabricated": False,
        },
    }
    validate_architecture_description(architecture)
    return architecture


def generate_architecture_summary(architecture: dict[str, Any] | None = None) -> dict[str, Any]:
    active = architecture or generate_architecture_description()
    validate_architecture_description(active)
    return {
        "module": "RP-003",
        "summary_type": "architecture_summary",
        "status": "generated",
        "component_count": active["component_registry"]["component_count"],
        "layer_count": active["layered_architecture"]["layer_count"],
        "module_family_count": len(active["module_hierarchy"]["families"]),
        "runtime_lifecycle_step_count": len(active["runtime_lifecycle"]),
        "implemented_scope_only": True,
    }


def generate_architecture_glossary(component_registry: dict[str, Any]) -> dict[str, Any]:
    components = tuple(component["component_id"] for component in component_registry["components"])
    glossary_terms = (
        ("component_registry", "Deterministic registry of runtime platform components discovered from PI-002."),
        ("interaction_matrix", "Pairwise component relationship structure derived from implemented workflow order."),
        ("runtime_lifecycle", "Documented initialization, registration, execution, validation, and publication sequence."),
        ("implemented_scope", "Methodology boundary limited to modules and contracts present in the codebase."),
        ("no_fabricated_formulas", "Publication constraint that equations are omitted unless implemented sources provide them."),
    )
    component_terms = tuple(
        (component["component_id"], component["description"] or component["name"])
        for component in component_registry["components"]
    )
    terms = tuple(
        {"term_id": term_id, "definition": definition}
        for term_id, definition in sorted((*glossary_terms, *component_terms), key=lambda item: item[0])
    )
    if set(components) - {term["term_id"] for term in terms}:
        raise TerminologyConsistencyError("component glossary coverage is incomplete")
    return {
        "glossary_version": ARCHITECTURE_DESCRIPTION_VERSION,
        "term_count": len(terms),
        "terms": terms,
    }


def validate_architecture_description(architecture: dict[str, Any]) -> dict[str, Any]:
    components = tuple(architecture["component_registry"]["components"])
    component_ids = tuple(component["component_id"] for component in components)
    if len(component_ids) != len(set(component_ids)):
        raise DuplicateArchitectureIdError("duplicate architecture component IDs are not allowed")
    layer_component_ids = tuple(
        component_id
        for layer in architecture["layered_architecture"]["layers"]
        for component_id in layer["component_ids"]
    )
    if set(component_ids) != set(layer_component_ids):
        missing = tuple(sorted(set(component_ids) - set(layer_component_ids)))
        extra = tuple(sorted(set(layer_component_ids) - set(component_ids)))
        raise UndocumentedComponentError(f"inconsistent layered architecture coverage; missing={missing}, extra={extra}")
    if tuple(sorted(component_ids)) != component_ids:
        raise InconsistentArchitectureMappingError("component registry ordering must be deterministic")
    glossary_ids = tuple(term["term_id"] for term in architecture["architecture_glossary"]["terms"])
    if len(glossary_ids) != len(set(glossary_ids)):
        raise TerminologyConsistencyError("duplicate architecture glossary term IDs are not allowed")
    return {
        "module": "RP-003",
        "status": "valid",
        "component_count": len(component_ids),
        "layer_count": architecture["layered_architecture"]["layer_count"],
        "glossary_term_count": len(glossary_ids),
    }


def _component_registry(runtime_registry: dict[str, Any]) -> dict[str, Any]:
    contracts = default_platform_contracts()
    components = []
    for component in sorted(runtime_registry["components"], key=lambda item: item["module_id"]):
        contract = contracts[component["module_id"]]
        components.append(
            {
                "component_id": component["module_id"],
                "name": component["name"],
                "runtime_phase": component["phase"],
                "version": component["version"],
                "status": component["status"],
                "capabilities": component["capabilities"],
                "dependencies": component["dependencies"],
                "contracts": component["contracts"],
                "execution_method": contract.execution_method,
                "description": contract.description,
                "source": "PI-002 runtime registry and PI-001 platform contract",
            }
        )
    return {
        "registry_type": "architecture_component_registry",
        "component_count": len(components),
        "components": tuple(components),
    }


def _layered_architecture(components: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    component_ids = {component["component_id"] for component in components}
    layers = tuple(
        {
            **layer,
            "component_ids": tuple(component_id for component_id in layer["component_ids"] if component_id in component_ids),
        }
        for layer in LAYER_DEFINITIONS
    )
    return {
        "architecture_type": "layered_architecture",
        "layer_count": len(layers),
        "layers": layers,
    }


def _module_hierarchy() -> dict[str, Any]:
    return {
        "hierarchy_type": "implemented_module_scope",
        "families": tuple(
            {
                "family_id": family_id,
                "module_ids": module_ids,
                "module_count": len(module_ids),
            }
            for family_id, module_ids in sorted(IMPLEMENTED_SCOPE_MODULES.items())
        ),
    }


def _runtime_lifecycle() -> tuple[dict[str, Any], ...]:
    steps = (
        ("runtime_01_initialize_contracts", "Initialize deterministic platform contracts", ("PI-001",)),
        ("runtime_02_register_components", "Register runtime components in PI-002", ("PI-002",)),
        ("runtime_03_validate_integration", "Validate platform, gateway, persistence, observability, and deployment readiness", ("PI-003", "PI-004", "PI-005", "PI-006", "PI-007", "PI-008")),
        ("runtime_04_execute_workflows", "Execute knowledge, decision, governance, provenance, monitoring, and delivery workflows", ("DKE", "DIE", "DPG", "DDGM", "TDLL", "ADBM", "ADWG", "DHMF", "DRIF", "EDOF")),
        ("runtime_05_validate_outputs", "Validate deterministic regression, decision quality, performance, governance, and stress behavior", ("VB-001", "VB-002", "VB-003", "VB-004", "VB-005")),
        ("runtime_06_publish_artifacts", "Publish synchronized documentation, patent-support, and research-paper artifacts", ("DOC-001", "DOC-002", "DOC-003", "DOC-004", "DOC-005", "PAT-001", "PAT-002", "PAT-003", "PAT-004", "RP-001", "RP-002", "RP-003")),
    )
    return tuple(
        {"step_id": step_id, "description": description, "supporting_modules": modules}
        for step_id, description, modules in steps
    )
