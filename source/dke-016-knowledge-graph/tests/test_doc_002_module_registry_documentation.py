import pytest

from documentation import (
    DuplicateModuleRegistryEntryError,
    MalformedModuleRegistryEntryError,
    MissingModuleMetadataError,
    ModuleRegistryEntry,
    PHASE_ORDER,
    create_architecture_documentation_generator,
    create_module_registry_documenter,
)
from platform_integration import RuntimeComponentMetadata, UnifiedPlatformRuntimeRegistry


def test_automatic_discovery_from_runtime_registry():
    documenter = create_module_registry_documenter()
    registry = documenter.generate_module_registry()
    module_ids = tuple(
        entry["module_id"]
        for phase in PHASE_ORDER
        for entry in registry["modules_by_phase"][phase]
    )
    assert "DKE" in module_ids
    assert "DIE" in module_ids
    assert "DOC-001" in module_ids
    assert "DOC-002" in module_ids


def test_deterministic_ordering_by_phase_and_module_id():
    documenter = create_module_registry_documenter()
    registry = documenter.generate_module_registry()
    flattened = tuple(
        (entry["phase"], entry["module_id"])
        for phase in PHASE_ORDER
        for entry in registry["modules_by_phase"][phase]
    )
    assert flattened == tuple(sorted(flattened, key=lambda item: (PHASE_ORDER.index(item[0]), item[1])))


def test_duplicate_detection():
    runtime = UnifiedPlatformRuntimeRegistry()
    runtime.register_runtime_component(RuntimeComponentMetadata("DKE", "Duplicate DKE", "dke"))
    documenter = create_module_registry_documenter(runtime)
    registry = documenter.generate_module_registry()
    duplicate_entry = registry["modules_by_phase"]["dke"][0]
    registry["modules_by_phase"]["documentation"] = (*registry["modules_by_phase"]["documentation"], duplicate_entry)
    with pytest.raises(DuplicateModuleRegistryEntryError, match="duplicate module ID"):
        documenter.validate_registry_documentation(registry)


def test_metadata_validation():
    with pytest.raises(MissingModuleMetadataError, match="missing module metadata"):
        ModuleRegistryEntry("", "Missing", "documentation", "1.0.0", "complete", (), ("api",), "description")


def test_malformed_registry_entry_rejection():
    documenter = create_module_registry_documenter()
    registry = documenter.generate_module_registry()
    first = registry["modules_by_phase"]["platform_integration"][0]
    malformed = {**first, "phase": "documentation"}
    registry["modules_by_phase"]["platform_integration"] = (malformed, *registry["modules_by_phase"]["platform_integration"][1:])
    with pytest.raises(MalformedModuleRegistryEntryError, match="malformed registry entry phase"):
        documenter.validate_registry_documentation(registry)


def test_markdown_export():
    documenter = create_module_registry_documenter()
    markdown = documenter.export_registry_markdown()
    assert markdown.startswith("# Project-1 Module Registry")
    assert "## Platform Integration" in markdown
    assert "DOC-002 - Module Registry Documentation" in markdown


def test_json_export():
    documenter = create_module_registry_documenter()
    registry = documenter.export_registry_json()
    assert registry["module"] == "DOC-002"
    assert registry["status"] == "generated"
    assert registry["doc_001_manifest"]["module"] == "DOC-001"


def test_summary_generation_and_statistics():
    documenter = create_module_registry_documenter()
    registry = documenter.generate_module_registry()
    summary = registry["summary"]
    stats = registry["statistics"]
    assert summary["summary_type"] == "module_registry_summary"
    assert stats["module_count"] == 12
    assert stats["phase_count"] == len(PHASE_ORDER)


def test_integration_with_doc001_and_pi002():
    doc_generator = create_architecture_documentation_generator()
    documenter = create_module_registry_documenter(doc_generator.runtime_registry)
    registry = documenter.generate_module_registry()
    assert registry["doc_001_manifest"]["module"] == "DOC-001"
    assert registry["doc_001_manifest"]["runtime_registry"]["module"] == "PI-002"


def test_registry_documentation_is_deterministic():
    documenter = create_module_registry_documenter()
    first_markdown = documenter.export_registry_markdown()
    second_markdown = documenter.export_registry_markdown()
    first_json = documenter.export_registry_json()
    second_json = documenter.export_registry_json()
    assert first_markdown == second_markdown
    assert first_json == second_json
