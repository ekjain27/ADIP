import pytest

from research_paper.architecture_composer import generate_architecture_description, generate_architecture_summary
from research_paper.component_relationships import generate_component_relationships, validate_component_relationships
from research_paper.methodology_errors import (
    DuplicateArchitectureIdError,
    InconsistentArchitectureMappingError,
    MalformedWorkflowDefinitionError,
    UndocumentedComponentError,
)
from research_paper.methodology_generator import generate_methodology, validate_methodology
from research_paper.methodology_manifest import METHODOLOGY_MANIFEST_VERSION, generate_methodology_manifest
from research_paper.workflow_documenter import generate_workflow_documentation, validate_workflow_documentation


def test_methodology_generation():
    methodology = generate_methodology()
    assert methodology["module"] == "RP-003"
    assert methodology["status"] == "generated"
    assert len(methodology["sections"]) == 9
    assert methodology["sections"][0]["section_id"] == "system_overview"
    assert methodology["integrity"]["algorithms_fabricated"] is False
    assert methodology["integrity"]["equations_fabricated"] is False
    assert methodology["markdown"].startswith("# Methodology And System Architecture")


def test_architecture_discovery_from_runtime_registry():
    architecture = generate_architecture_description()
    component_ids = tuple(component["component_id"] for component in architecture["component_registry"]["components"])
    assert component_ids == ("ADBM", "ADWG", "DDGM", "DHMF", "DIE", "DKE", "DPG", "DRIF", "EDOF", "TDLL")
    assert architecture["architecture_summary"]["runtime_component_count"] == 10
    assert architecture["source_evidence"]["runtime_registry_module"] == "PI-002"
    assert architecture["integrity"]["system_capabilities_fabricated"] is False


def test_workflow_generation():
    workflows = generate_workflow_documentation()
    workflow_ids = tuple(workflow["workflow_id"] for workflow in workflows["workflows"])
    assert workflow_ids == tuple(sorted(workflow_ids))
    assert "workflow_decision_pipeline" in workflow_ids
    assert "workflow_validation" in workflow_ids
    decision = next(workflow for workflow in workflows["workflows"] if workflow["workflow_id"] == "workflow_decision_pipeline")
    assert decision["component_ids"][0] == "DKE"
    assert decision["component_ids"][-1] == "EDOF"


def test_component_relationship_generation():
    relationships = generate_component_relationships()
    sequence = tuple(step["component_id"] for step in relationships["execution_sequence"])
    assert sequence == ("DKE", "DIE", "DPG", "DDGM", "TDLL", "ADBM", "ADWG", "DHMF", "DRIF", "EDOF")
    assert relationships["relationship_report"]["orphan_components"] == ()
    assert relationships["interaction_matrix"][0]["source_component_id"] == "ADBM"


def test_deterministic_methodology_output():
    first = generate_methodology()
    second = generate_methodology()
    assert first == second
    assert generate_architecture_description() == generate_architecture_description()
    assert generate_workflow_documentation() == generate_workflow_documentation()


def test_manifest_generation_and_integration_traces():
    manifest = generate_methodology_manifest()
    assert manifest["module"] == "RP-003"
    assert manifest["manifest_version"] == METHODOLOGY_MANIFEST_VERSION
    assert manifest["documentation_trace"]["DOC-001"] == "DOC-001"
    assert manifest["documentation_trace"]["DOC-005"] == "DOC-005"
    assert manifest["platform_integration_trace"]["PI-001"] == "PI-001"
    assert manifest["platform_integration_trace"]["PI-008"] == "PI-008"
    assert manifest["validation_trace"]["VB-001"] == "VB-001"
    assert manifest["validation_trace"]["VB-005"] == "VB-005"
    assert manifest["patent_trace"]["PAT-001"] == "PAT-001.1"
    assert manifest["patent_trace"]["PAT-004"] == "PAT-004.1"
    assert manifest["runtime_registry"]["module"] == "PI-002"
    assert manifest["integrity"]["production_modules_modified"] is False


def test_validate_methodology_success():
    validation = validate_methodology(generate_methodology())
    assert validation["status"] == "valid"
    assert validation["section_count"] == 9
    assert validation["component_count"] == 10
    assert validation["workflow_count"] == 7


def test_architecture_summary_generation():
    summary = generate_architecture_summary()
    assert summary["component_count"] == 10
    assert summary["layer_count"] == 5
    assert summary["implemented_scope_only"] is True


def test_duplicate_architecture_id_rejection():
    architecture = generate_architecture_description()
    duplicated = {
        **architecture,
        "component_registry": {
            **architecture["component_registry"],
            "components": (
                architecture["component_registry"]["components"][0],
                architecture["component_registry"]["components"][0],
                *architecture["component_registry"]["components"][2:],
            ),
        },
    }
    with pytest.raises(DuplicateArchitectureIdError, match="duplicate architecture component IDs"):
        validate_methodology({**generate_methodology(), "architecture": duplicated})


def test_orphan_component_rejection():
    relationships = generate_component_relationships()
    malformed = {
        **relationships,
        "execution_sequence": tuple(
            step for step in relationships["execution_sequence"] if step["component_id"] != "EDOF"
        ),
    }
    with pytest.raises(UndocumentedComponentError, match="orphan component"):
        validate_component_relationships(malformed)


def test_malformed_workflow_rejection():
    workflows = generate_workflow_documentation()
    malformed = {
        **workflows,
        "workflows": (
            {**workflows["workflows"][0], "steps": ()},
            *workflows["workflows"][1:],
        ),
    }
    with pytest.raises(MalformedWorkflowDefinitionError, match="malformed workflow definition"):
        validate_workflow_documentation(malformed)


def test_methodology_section_order_rejection():
    methodology = generate_methodology()
    malformed = {**methodology, "sections": tuple(reversed(methodology["sections"]))}
    with pytest.raises(InconsistentArchitectureMappingError, match="section ordering"):
        validate_methodology(malformed)
