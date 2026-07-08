import pytest

from documentation import (
    DuplicateGuideSectionError,
    InconsistentDependencyGraphError,
    MalformedApiReferenceError,
    UndocumentedPublicModuleError,
    create_developer_guide_framework,
)


def test_automatic_developer_guide_generation():
    framework = create_developer_guide_framework()
    guide = framework.generate_developer_guide()
    sections = tuple(section for section, _ in guide["sections"])
    assert guide["module"] == "DOC-004"
    assert guide["status"] == "generated"
    assert "project_overview" in sections
    assert "sdk_reference" in sections


def test_sdk_discovery():
    framework = create_developer_guide_framework()
    reference = framework.generate_sdk_reference()
    components = tuple(component["component"] for component in reference["components"])
    assert reference["reference_type"] == "sdk_reference"
    assert "PlatformIntegrationLayer" in components
    assert "UnifiedPlatformRuntimeRegistry" in components
    assert "EnterpriseApiGateway" in components


def test_deterministic_output():
    framework = create_developer_guide_framework()
    first_manifest = framework.generate_onboarding_manifest()
    second_manifest = framework.generate_onboarding_manifest()
    first_markdown = framework.export_developer_markdown()
    second_markdown = framework.export_developer_markdown()
    assert first_manifest == second_manifest
    assert first_markdown == second_markdown


def test_checklist_generation():
    framework = create_developer_guide_framework()
    checklist = framework.generate_developer_checklist()
    assert checklist["checklist_type"] == "developer_onboarding"
    assert checklist["item_count"] >= 8
    assert all(item["required"] for item in checklist["items"])


def test_json_manifest_export():
    framework = create_developer_guide_framework()
    manifest = framework.generate_onboarding_manifest()
    assert manifest["module"] == "DOC-004"
    assert manifest["runtime_registry"]["module"] == "PI-002"
    assert manifest["doc_integrations"] == ("DOC-001", "DOC-002", "DOC-003", "PI-002")


def test_markdown_export():
    framework = create_developer_guide_framework()
    markdown = framework.export_developer_markdown()
    assert markdown.startswith("# Project-1 Developer Onboarding & SDK Guide")
    assert "## Installation Guide" in markdown
    assert "## Developer Checklist" in markdown
    assert "PlatformIntegrationLayer" in markdown


def test_duplicate_guide_section_rejection():
    framework = create_developer_guide_framework()
    guide = framework.generate_developer_guide()
    duplicate = {**guide, "sections": (*guide["sections"], guide["sections"][0])}
    with pytest.raises(DuplicateGuideSectionError, match="duplicate guide section"):
        framework.validate_developer_documentation(duplicate)


def test_undocumented_public_module_rejection():
    framework = create_developer_guide_framework()
    guide = framework.generate_developer_guide()
    trimmed = {**guide, "sections": tuple(item for item in guide["sections"] if item[0] != "sdk_reference")}
    with pytest.raises(UndocumentedPublicModuleError, match="undocumented public module section"):
        framework.validate_developer_documentation(trimmed)


def test_inconsistent_dependency_graph_rejection():
    framework = create_developer_guide_framework()
    guide = framework.generate_developer_guide()
    sections = dict(guide["sections"])
    dependency_overview = ({"module_id": "SELF", "dependencies": ("SELF",)},)
    sections["dependency_overview"] = dependency_overview
    mutated = {**guide, "sections": tuple((section, sections[section]) for section, _ in guide["sections"])}
    with pytest.raises(InconsistentDependencyGraphError, match="inconsistent dependency graph"):
        framework.validate_developer_documentation(mutated)


def test_malformed_api_reference_rejection():
    framework = create_developer_guide_framework()
    guide = framework.generate_developer_guide()
    sections = dict(guide["sections"])
    sections["sdk_reference"] = {"component_count": 0, "components": ()}
    mutated = {**guide, "sections": tuple((section, sections[section]) for section, _ in guide["sections"])}
    with pytest.raises(MalformedApiReferenceError, match="malformed API reference"):
        framework.validate_developer_documentation(mutated)


def test_integration_with_doc001_through_doc003_and_runtime_registry():
    framework = create_developer_guide_framework()
    manifest = framework.generate_onboarding_manifest()
    assert manifest["api_documentation"]["api_catalog"]["doc_001_manifest"]["module"] == "DOC-001"
    assert manifest["api_documentation"]["api_catalog"]["doc_002_registry"]["module"] == "DOC-002"
    assert manifest["api_documentation"]["module"] == "DOC-003"
    assert manifest["runtime_registry"]["module"] == "PI-002"
