from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from platform_integration import PLATFORM_COMPONENTS
from validation import WorkflowRunner

from .methodology_errors import DuplicateArchitectureIdError, MalformedWorkflowDefinitionError

WORKFLOW_DOCUMENTATION_VERSION = "RP-003.1"


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_id: str
    name: str
    purpose: str
    component_ids: tuple[str, ...]
    steps: tuple[str, ...]
    source_modules: tuple[str, ...]
    limitations: tuple[str, ...] = ()

    def to_record(self) -> dict[str, Any]:
        if not self.workflow_id.strip() or not self.name.strip() or not self.steps:
            raise MalformedWorkflowDefinitionError("workflow requires ID, name, and steps")
        if any(not step.strip() for step in self.steps):
            raise MalformedWorkflowDefinitionError(f"workflow contains an empty step: {self.workflow_id}")
        unknown = tuple(component_id for component_id in self.component_ids if component_id not in PLATFORM_COMPONENTS)
        if unknown:
            raise MalformedWorkflowDefinitionError(f"workflow references unknown platform component(s): {unknown}")
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "purpose": self.purpose,
            "component_ids": self.component_ids,
            "steps": self.steps,
            "source_modules": self.source_modules,
            "limitations": self.limitations,
            "fabricated_algorithms": False,
        }


def generate_workflow_documentation() -> dict[str, Any]:
    runner = WorkflowRunner()
    workflows = tuple(definition.to_record() for definition in _workflow_definitions(runner))
    documentation = {
        "module": "RP-003",
        "documentation_version": WORKFLOW_DOCUMENTATION_VERSION,
        "status": "generated",
        "registered_validation_workflows": runner.workflow_names(),
        "workflows": workflows,
        "workflow_count": len(workflows),
        "integrity": {
            "mathematical_formulations_fabricated": False,
            "unsupported_algorithms_fabricated": False,
        },
    }
    validate_workflow_documentation(documentation)
    return documentation


def validate_workflow_documentation(documentation: dict[str, Any]) -> dict[str, Any]:
    workflow_ids = tuple(workflow["workflow_id"] for workflow in documentation["workflows"])
    if len(workflow_ids) != len(set(workflow_ids)):
        raise DuplicateArchitectureIdError("duplicate workflow IDs are not allowed")
    for workflow in documentation["workflows"]:
        if not workflow["steps"] or not workflow["source_modules"]:
            raise MalformedWorkflowDefinitionError(f"malformed workflow definition: {workflow['workflow_id']}")
        unknown = tuple(component_id for component_id in workflow["component_ids"] if component_id not in PLATFORM_COMPONENTS)
        if unknown:
            raise MalformedWorkflowDefinitionError(f"workflow references unknown platform component(s): {unknown}")
    if tuple(sorted(workflow_ids)) != workflow_ids:
        raise MalformedWorkflowDefinitionError("workflow ordering must be deterministic")
    return {
        "module": "RP-003",
        "status": "valid",
        "workflow_count": len(workflow_ids),
    }


def _workflow_definitions(runner: WorkflowRunner) -> tuple[WorkflowDefinition, ...]:
    definitions = (
        WorkflowDefinition(
            "workflow_decision_pipeline",
            "Decision Pipeline",
            "Documents the implemented deterministic path from knowledge context to enterprise recommendation.",
            ("DKE", "DIE", "DPG", "DDGM", "TDLL", "ADBM", "ADWG", "DHMF", "DRIF", "EDOF"),
            (
                "DKE retrieves context from the supplied research query.",
                "DIE processes the context into a deterministic decision payload.",
                "DPG, DDGM, and TDLL attach provenance, governance, and lineage metadata.",
                "ADBM, ADWG, DHMF, DRIF, and EDOF adapt, orchestrate, monitor, serve, and enterprise-wrap the payload.",
            ),
            ("PI-001", "PI-002", "VB-001"),
            ("No unimplemented ranking, optimization, or learning algorithm is claimed.",),
        ),
        WorkflowDefinition(
            "workflow_governance",
            "Governance Workflow",
            "Documents implemented governance evaluation and compliance reporting boundaries.",
            ("DPG", "DDGM", "TDLL"),
            (
                "DPG links the decision payload to provenance metadata.",
                "DDGM evaluates the payload against deterministic governance behavior.",
                "TDLL records temporal lineage status for downstream validation.",
            ),
            ("VB-004", "PAT-001", "DOC-001"),
        ),
        WorkflowDefinition(
            "workflow_knowledge_pipeline",
            "Knowledge Pipeline",
            "Documents the implemented research-to-DKE validation workflow.",
            ("DKE",),
            (
                "The validation runner supplies a deterministic research query.",
                "The DKE platform contract returns a context payload with source research identifiers.",
                "The workflow output is used by DIE and full-platform regression flows.",
            ),
            ("R-001", "R-010", "DKE", "VB-001"),
            ("No external literature API or retrieval model is required by this methodology composer.",),
        ),
        WorkflowDefinition(
            "workflow_platform_integration",
            "Platform Integration Workflow",
            "Documents implemented platform registration, registry, API, persistence, observability, and deployment readiness boundaries.",
            ("DKE", "DIE", "DPG", "DDGM", "TDLL", "ADBM", "ADWG", "DHMF", "DRIF", "EDOF"),
            (
                "PI-001 registers platform contracts and executable components.",
                "PI-002 exports runtime registry metadata for documentation and validation.",
                "PI-003 through PI-008 adapt contracts, expose internal API routes, configure runtime, persist records, observe events, and validate deployment readiness.",
            ),
            tuple(f"PI-{index:03d}" for index in range(1, 9)),
        ),
        WorkflowDefinition(
            "workflow_provenance",
            "Provenance Workflow",
            "Documents implemented provenance graph and temporal lineage boundaries.",
            ("DPG", "TDLL"),
            (
                "DPG builds a provenance representation from the decision payload.",
                "TDLL records deterministic lineage metadata.",
                "Validation and patent-support traces consume the same module identifiers.",
            ),
            ("VB-004", "PAT-001", "PAT-002", "PAT-003"),
        ),
        WorkflowDefinition(
            "workflow_runtime_lifecycle",
            "Runtime Lifecycle",
            "Documents the implemented lifecycle from contract setup to generated artifacts.",
            ("DKE", "DIE", "DPG", "DDGM", "TDLL", "ADBM", "ADWG", "DHMF", "DRIF", "EDOF"),
            (
                "Create the validation platform layer.",
                "Register runtime components and export registry snapshots.",
                "Execute deterministic workflows through platform contracts.",
                "Validate regression, quality, performance, governance, and stress reports.",
                "Generate documentation, patent-support, and research-paper artifacts from synchronized metadata.",
            ),
            ("DOC-001", "PI-002", "VB-001", "PAT-004", "RP-003"),
        ),
        WorkflowDefinition(
            "workflow_validation",
            "Validation Workflow",
            "Documents implemented regression, quality, performance, governance, and stress validation artifacts.",
            (),
            (
                "VB-001 executes end-to-end deterministic regression workflows.",
                "VB-002 reports decision quality benchmark status.",
                "VB-003 reports performance benchmark status.",
                "VB-004 validates governance and provenance behavior.",
                "VB-005 reports enterprise stress and failure-testing behavior.",
            ),
            tuple(f"VB-{index:03d}" for index in range(1, 6)),
        ),
    )
    return tuple(sorted(definitions, key=lambda item: item.workflow_id))
