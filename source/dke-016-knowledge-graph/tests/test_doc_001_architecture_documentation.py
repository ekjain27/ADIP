from documentation import (
    DOCUMENTATION_BASELINE_VERSION,
    create_architecture_documentation_generator,
)


def test_generate_architecture_documentation():
    generator = create_architecture_documentation_generator()
    docs = generator.generate_architecture_documentation()
    assert docs["module"] == "DOC-001"
    assert docs["status"] == "generated"
    assert docs["architecture_summary"]["runtime_component_count"] == 10


def test_generate_module_catalog_from_runtime_registry():
    generator = create_architecture_documentation_generator()
    catalog = generator.generate_module_catalog()
    module_ids = tuple(module["module_id"] for module in catalog["modules"])
    assert catalog["catalog_type"] == "module_catalog"
    assert "DKE" in module_ids
    assert "DIE" in module_ids
    assert "DPG" in module_ids


def test_generate_api_catalog():
    generator = create_architecture_documentation_generator()
    catalog = generator.generate_api_catalog()
    components = {entry["component"]: entry for entry in catalog["components"]}
    assert "platform_layer" in components
    assert "execute_component" in components["platform_layer"]["public_api"]
    assert "runtime_registry" in components
    assert "export_registry_snapshot" in components["runtime_registry"]["public_api"]


def test_generate_documentation_manifest():
    generator = create_architecture_documentation_generator()
    manifest = generator.generate_documentation_manifest()
    assert manifest["module"] == "DOC-001"
    assert manifest["baseline_version"] == DOCUMENTATION_BASELINE_VERSION
    assert manifest["status"] == "generated"
    assert manifest["runtime_registry"]["module"] == "PI-002"


def test_export_markdown():
    generator = create_architecture_documentation_generator()
    markdown = generator.export_markdown()
    assert markdown.startswith("# AI Decision Intelligence Platform - Architecture Overview")
    assert "## Module Catalog" in markdown
    assert "DKE" in markdown
    assert "VB-005" in markdown


def test_export_json_manifest():
    generator = create_architecture_documentation_generator()
    manifest = generator.export_json_manifest()
    assert manifest == generator.generate_documentation_manifest()
    assert manifest["validation_summary"]["status"] == "passed"


def test_dependency_graph_text_representation():
    generator = create_architecture_documentation_generator()
    docs = generator.generate_architecture_documentation()
    assert "DKE -> none" in docs["dependency_graph"]
    assert "DIE -> none" in docs["dependency_graph"]


def test_integration_catalog():
    generator = create_architecture_documentation_generator()
    docs = generator.generate_architecture_documentation()
    catalog = docs["integration_catalog"]
    assert catalog["catalog_type"] == "integration_catalog"
    assert catalog["deployment_module"] == "PI-008"
    assert "VB-001" in catalog["validation_modules"]
    assert "VB-005" in catalog["validation_modules"]


def test_validation_summary_includes_vb001_through_vb005():
    generator = create_architecture_documentation_generator()
    summary = generator.generate_architecture_documentation()["validation_summary"]
    assert summary["status"] == "passed"
    assert summary["modules"] == ("VB-001", "VB-002", "VB-003", "VB-004", "VB-005")


def test_documentation_output_is_deterministic():
    generator = create_architecture_documentation_generator()
    first_markdown = generator.export_markdown()
    second_markdown = generator.export_markdown()
    first_manifest = generator.export_json_manifest()
    second_manifest = generator.export_json_manifest()
    assert first_markdown == second_markdown
    assert first_manifest == second_manifest
