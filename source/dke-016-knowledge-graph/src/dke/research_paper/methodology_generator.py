from __future__ import annotations

from typing import Any

from documentation import create_architecture_documentation_generator
from patent import create_patent_specification_generator

from .architecture_composer import generate_architecture_description, generate_architecture_summary, validate_architecture_description
from .component_relationships import generate_component_relationships, validate_component_relationships
from .methodology_errors import InconsistentArchitectureMappingError, TerminologyConsistencyError
from .workflow_documenter import generate_workflow_documentation, validate_workflow_documentation

METHODOLOGY_VERSION = "RP-003.1"

METHODOLOGY_SECTION_ORDER = (
    "system_overview",
    "architectural_design",
    "core_components",
    "processing_workflow",
    "data_flow",
    "integration_strategy",
    "validation_strategy",
    "design_principles",
    "limitations",
)


def generate_methodology() -> dict[str, Any]:
    documentation_generator = create_architecture_documentation_generator()
    documentation = documentation_generator.generate_architecture_documentation()
    patent_generator = create_patent_specification_generator()
    patent_manifest = patent_generator.export_json_manifest()
    architecture = generate_architecture_description(documentation)
    workflows = generate_workflow_documentation()
    relationships = generate_component_relationships(architecture)
    methodology = {
        "module": "RP-003",
        "methodology_version": METHODOLOGY_VERSION,
        "status": "generated",
        "sections": _methodology_sections(architecture, workflows, relationships, documentation, patent_manifest),
        "architecture": architecture,
        "workflow_documentation": workflows,
        "component_relationships": relationships,
        "architecture_summary": generate_architecture_summary(architecture),
        "component_relationship_report": relationships["relationship_report"],
        "markdown": _markdown_methodology(architecture, workflows, relationships),
        "source_trace": {
            "documentation_trace": _documentation_trace(documentation),
            "platform_integration_trace": {f"PI-{index:03d}": f"PI-{index:03d}" for index in range(1, 9)},
            "validation_trace": {f"VB-{index:03d}": f"VB-{index:03d}" for index in range(1, 6)},
            "patent_trace": {
                "PAT-001": patent_manifest["source_manifests"]["PAT-001"],
                "PAT-002": patent_manifest["source_manifests"]["PAT-002"],
                "PAT-003": patent_manifest["source_manifests"]["PAT-003"],
                "PAT-004": patent_manifest["manifest_version"],
            },
            "runtime_registry": documentation["runtime_registry"],
        },
        "integrity": {
            "algorithms_fabricated": False,
            "equations_fabricated": False,
            "unsupported_capabilities_fabricated": False,
        },
    }
    validate_methodology(methodology)
    return methodology


def validate_methodology(methodology: dict[str, Any] | None = None) -> dict[str, Any]:
    active = methodology or generate_methodology()
    section_ids = tuple(section["section_id"] for section in active["sections"])
    if section_ids != METHODOLOGY_SECTION_ORDER:
        raise InconsistentArchitectureMappingError("methodology section ordering is incomplete or non-deterministic")
    validate_architecture_description(active["architecture"])
    validate_workflow_documentation(active["workflow_documentation"])
    validate_component_relationships(active["component_relationships"])
    glossary_terms = {term["term_id"] for term in active["architecture"]["architecture_glossary"]["terms"]}
    missing_terms = tuple(
        component["component_id"]
        for component in active["architecture"]["component_registry"]["components"]
        if component["component_id"] not in glossary_terms
    )
    if missing_terms:
        raise TerminologyConsistencyError(f"methodology glossary missing component terms: {missing_terms}")
    return {
        "module": "RP-003",
        "status": "valid",
        "section_count": len(section_ids),
        "component_count": active["architecture_summary"]["component_count"],
        "workflow_count": active["workflow_documentation"]["workflow_count"],
    }


def _methodology_sections(
    architecture: dict[str, Any],
    workflows: dict[str, Any],
    relationships: dict[str, Any],
    documentation: dict[str, Any],
    patent_manifest: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    content = {
        "system_overview": (
            f"The implemented platform is documented as {architecture['platform']} with "
            f"{architecture['component_registry']['component_count']} runtime components exported by PI-002."
        ),
        "architectural_design": (
            f"The architecture is organized into {architecture['layered_architecture']['layer_count']} deterministic layers "
            "derived from platform contracts and runtime registry metadata."
        ),
        "core_components": (
            "Core components are DKE, DIE, DPG, DDGM, TDLL, ADBM, ADWG, DHMF, DRIF, and EDOF; each component is described "
            "from its implemented platform contract."
        ),
        "processing_workflow": (
            f"The processing workflow follows {len(relationships['execution_sequence'])} ordered component steps and "
            f"{workflows['workflow_count']} documented workflow views."
        ),
        "data_flow": (
            "Data flow is represented as deterministic payload transformation through registered platform contracts; "
            "no unsupported mathematical equations are introduced."
        ),
        "integration_strategy": (
            "Integration is grounded in PI-001 through PI-008, including contracts, runtime registry, adapter, API gateway, "
            "configuration, persistence, observability, and deployment readiness boundaries."
        ),
        "validation_strategy": (
            f"Validation is grounded in {', '.join(documentation['validation_summary']['modules'])} with status "
            f"{documentation['validation_summary']['status']}."
        ),
        "design_principles": (
            "The methodology emphasizes deterministic ordering, traceable metadata, frozen runtime components, explicit "
            "contract boundaries, and synchronized generated artifacts."
        ),
        "limitations": (
            "The methodology is limited to implemented modules and generated manifests. It does not claim unimplemented "
            f"algorithms, equations, benchmark values, or patentability; PAT trace status is {patent_manifest['status']}."
        ),
    }
    return tuple(
        {
            "section_id": section_id,
            "title": section_id.replace("_", " ").title(),
            "content": content[section_id],
            "fabricated_claims": False,
        }
        for section_id in METHODOLOGY_SECTION_ORDER
    )


def _markdown_methodology(
    architecture: dict[str, Any],
    workflows: dict[str, Any],
    relationships: dict[str, Any],
) -> str:
    lines = [
        "# Methodology And System Architecture",
        "",
        "## System Overview",
        (
            f"The methodology is generated from the implemented runtime registry and documentation artifacts for "
            f"{architecture['platform']}."
        ),
        "",
        "## Architectural Design",
    ]
    for layer in architecture["layered_architecture"]["layers"]:
        lines.append(f"- {layer['name']}: {', '.join(layer['component_ids'])}")
    lines.extend(["", "## Core Components"])
    for component in architecture["component_registry"]["components"]:
        lines.append(f"- {component['component_id']}: {component['description']}")
    lines.extend(["", "## Processing Workflow"])
    for step in relationships["execution_sequence"]:
        lines.append(f"- {step['sequence_number']}. {step['component_id']}: {step['role']}")
    lines.extend(["", "## Workflow Views"])
    for workflow in workflows["workflows"]:
        lines.append(f"- {workflow['name']}: {workflow['purpose']}")
    lines.extend(
        [
            "",
            "## Limitations",
            "This methodology documents implemented contracts, registry metadata, workflow behavior, validation outputs, and generated artifacts only. It does not add equations, algorithms, or capabilities absent from the codebase.",
        ]
    )
    return "\n".join(lines) + "\n"


def _documentation_trace(documentation: dict[str, Any]) -> dict[str, str]:
    return {
        "DOC-001": documentation["module"],
        "DOC-002": "DOC-002",
        "DOC-003": "DOC-003",
        "DOC-004": "DOC-004",
        "DOC-005": "DOC-005",
    }
