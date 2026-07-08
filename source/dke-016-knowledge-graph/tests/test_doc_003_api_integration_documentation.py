import pytest

from documentation import (
    ApiDocumentationEntry,
    ApiParameter,
    DuplicateApiIdentifierError,
    InconsistentIntegrationMappingError,
    IntegrationMapping,
    MalformedApiSignatureError,
    UndocumentedPublicInterfaceError,
    create_api_integration_documentation_framework,
    generate_integration_matrix,
)


def test_automatic_api_discovery():
    framework = create_api_integration_documentation_framework()
    catalog = framework.generate_api_catalog()
    api_ids = tuple(api["api_id"] for api in catalog["apis"])
    assert catalog["module"] == "DOC-003"
    assert "PlatformIntegrationLayer.execute_component" in api_ids
    assert "UnifiedPlatformRuntimeRegistry.export_registry_snapshot" in api_ids
    assert "EnterpriseApiGateway.handle_request" in api_ids


def test_deterministic_ordering():
    framework = create_api_integration_documentation_framework()
    first = framework.generate_api_catalog()["apis"]
    second = framework.generate_api_catalog()["apis"]
    assert first == second
    assert tuple(api["api_id"] for api in first) == tuple(sorted(api["api_id"] for api in first))


def test_api_metadata_validation():
    framework = create_api_integration_documentation_framework()
    validation = framework.validate_api_documentation()
    assert validation["module"] == "DOC-003"
    assert validation["status"] == "valid"
    assert validation["api_count"] > 0


def test_undocumented_public_interface_rejection():
    bad = ApiDocumentationEntry(
        api_id="Bad.method",
        name="method",
        module="documentation.bad",
        owner="bad",
        purpose="",
        parameters=(),
        return_type="Any",
        exceptions=(),
        dependencies=(),
    )
    framework = create_api_integration_documentation_framework()
    with pytest.raises(UndocumentedPublicInterfaceError, match="undocumented public interface"):
        framework.validate_api_documentation((bad,))


def test_malformed_signature_rejection():
    with pytest.raises(MalformedApiSignatureError, match="API parameter requires"):
        ApiParameter("", "Any")


def test_integration_matrix_generation():
    framework = create_api_integration_documentation_framework()
    matrix = framework.generate_integration_matrix()
    mapping_ids = tuple(mapping["mapping_id"] for mapping in matrix["mappings"])
    assert matrix["matrix_type"] == "integration_matrix"
    assert "research-to-dke" in mapping_ids
    assert "dke-to-die" in mapping_ids
    assert "die-to-platform" in mapping_ids
    assert "platform-to-validation" in mapping_ids


def test_markdown_export():
    framework = create_api_integration_documentation_framework()
    markdown = framework.export_api_markdown()
    assert markdown.startswith("# Project-1 API & Integration Documentation")
    assert "## Public APIs" in markdown
    assert "PlatformIntegrationLayer.execute_component" in markdown
    assert "Research -> DKE" in markdown


def test_json_export():
    framework = create_api_integration_documentation_framework()
    payload = framework.export_api_json()
    assert payload["module"] == "DOC-003"
    assert payload["api_catalog"]["doc_001_manifest"]["module"] == "DOC-001"
    assert payload["api_catalog"]["doc_002_registry"]["module"] == "DOC-002"
    assert payload["integration_documentation"]["runtime_registry_interactions"]["module"] == "PI-002"


def test_duplicate_api_identifier_rejection():
    entry = ApiDocumentationEntry(
        api_id="Duplicate.method",
        name="method",
        module="documentation.test",
        owner="test",
        purpose="Test method",
        parameters=(ApiParameter("payload", "Mapping"),),
        return_type="dict",
        exceptions=(),
        dependencies=(),
    )
    framework = create_api_integration_documentation_framework()
    with pytest.raises(DuplicateApiIdentifierError, match="duplicate API identifier"):
        framework.validate_api_documentation((entry, entry))


def test_duplicate_integration_mapping_rejection():
    mapping = IntegrationMapping("same", "A", "B", "handoff", "contract", "entry")
    with pytest.raises(InconsistentIntegrationMappingError, match="duplicate integration mapping"):
        generate_integration_matrix((mapping, mapping))


def test_integration_with_doc001_doc002_and_platform_modules():
    framework = create_api_integration_documentation_framework()
    payload = framework.export_api_json()
    gateway_routes = payload["integration_documentation"]["api_gateway_routes"]
    assert payload["api_catalog"]["doc_001_manifest"]["module"] == "DOC-001"
    assert payload["api_catalog"]["doc_002_registry"]["module"] == "DOC-002"
    assert any(route["route"] == "/platform/execute" for route in gateway_routes)
    assert payload["integration_documentation"]["contract_adapter_mappings"]["module"] == "PI-003"
