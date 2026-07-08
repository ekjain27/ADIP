import pytest

from platform_integration import (
    DeploymentReadinessLayer,
    DuplicateManifestEntryError,
    EnterpriseApiGateway,
    IncompleteConfigurationError,
    MissingDeploymentComponentError,
    ObservabilityIntegrationLayer,
    PersistenceIntegrationLayer,
    PlatformIntegrationLayer,
    ReleaseManifestEntry,
    UnsupportedDeploymentProfileError,
    build_release_manifest,
    create_config,
    create_runtime_registry_from_platform_layer,
    default_platform_contracts,
    override_config,
)


class UniversalComponent:
    def retrieve_context(self, payload):
        return payload

    def process(self, payload):
        return payload

    def build(self, payload):
        return payload

    def evaluate(self, payload):
        return payload

    def track(self, payload):
        return payload

    def adapt(self, payload):
        return payload

    def orchestrate(self, payload):
        return payload

    def monitor(self, payload):
        return payload

    def serve(self, payload):
        return payload


def test_deployment_validation():
    layer = _readiness_layer("local")
    validation = layer.validate_deployment("local")
    assert validation["module"] == "PI-008"
    assert validation["status"] == "ready"
    assert validation["profile"] == "local"


def test_profile_validation_rejects_unsupported_profile():
    layer = _readiness_layer("local")
    with pytest.raises(UnsupportedDeploymentProfileError):
        layer.validate_deployment("qa")


def test_missing_component_rejected():
    platform = PlatformIntegrationLayer()
    contracts = default_platform_contracts()
    platform.register_component("DKE", UniversalComponent(), contracts["DKE"])
    runtime = create_runtime_registry_from_platform_layer(platform)
    gateway = EnterpriseApiGateway(platform_layer=platform, runtime_registry=runtime)
    persistence = PersistenceIntegrationLayer()
    observability = ObservabilityIntegrationLayer(
        platform_layer=platform,
        runtime_registry=runtime,
        api_gateway=gateway,
        persistence_layer=persistence,
    )
    layer = DeploymentReadinessLayer(platform, runtime, gateway, create_config("local"), persistence, observability)
    with pytest.raises(MissingDeploymentComponentError, match="missing required platform component"):
        layer.validate_deployment("local")


def test_incomplete_configuration_rejected():
    layer = _readiness_layer("local")
    layer.config = override_config(layer.config, {"platform_name": "Mismatch Test"})
    with pytest.raises(IncompleteConfigurationError, match="profile mismatch"):
        layer.validate_deployment("production")


def test_manifest_generation():
    manifest = _readiness_layer("test").generate_release_manifest()
    assert manifest["manifest_id"] == "project-1-platform-integration-release"
    assert manifest["entry_count"] == 7
    assert tuple(entry["module_id"] for entry in manifest["entries"]) == (
        "PI-001",
        "PI-002",
        "PI-004",
        "PI-005",
        "PI-006",
        "PI-007",
        "PI-008",
    )


def test_duplicate_manifest_entry_rejected():
    entry = ReleaseManifestEntry("PI-001", "Platform Integration Layer")
    with pytest.raises(DuplicateManifestEntryError, match="duplicate manifest entry"):
        build_release_manifest((entry, entry))


def test_inventory_export():
    inventory = _readiness_layer("staging").export_platform_inventory()
    assert inventory["module"] == "PI-008"
    assert len(inventory["platform_components"]) == 10
    assert inventory["configuration"]["profile"] == "staging"


def test_readiness_reporting():
    report = _readiness_layer("production").generate_readiness_report("production")
    assert report["report_type"] == "deployment_readiness"
    assert all(report["checks"].values())
    assert report["status"] == "ready"


def test_compatibility_reporting():
    reports = _readiness_layer("local").generate_compatibility_reports()
    assert reports["report_type"] == "deployment_compatibility"
    assert tuple(reports["profiles"]) == ("local", "test", "staging", "production")
    assert all(report["status"] == "compatible" for report in reports["profiles"].values())


def test_component_readiness():
    layer = _readiness_layer("local")
    assert layer.check_component_readiness("DKE")["status"] == "ready"
    assert layer.check_component_readiness("UNKNOWN")["status"] == "missing"


def test_deterministic_output():
    layer = _readiness_layer("test")
    first = layer.export_deployment_snapshot()
    second = layer.export_deployment_snapshot()
    assert first == second
    assert first["module"] == "PI-008"


def test_integration_with_pi_001_through_pi_007():
    layer = _readiness_layer("local")
    snapshot = layer.export_deployment_snapshot()
    assert snapshot["readiness_report"]["validation"]["platform"]["module"] == "PI-001"
    assert snapshot["readiness_report"]["validation"]["runtime"]["snapshot"]["module"] == "PI-002"
    assert snapshot["readiness_report"]["validation"]["api_gateway"]["module"] == "PI-004"
    assert snapshot["readiness_report"]["validation"]["configuration"]["module"] == "PI-005"
    assert snapshot["readiness_report"]["validation"]["persistence"]["module"] == "PI-006"
    assert snapshot["readiness_report"]["validation"]["observability"]["module"] == "PI-007"


def _readiness_layer(profile):
    platform = PlatformIntegrationLayer()
    contracts = default_platform_contracts()
    component = UniversalComponent()
    for name in sorted(contracts):
        platform.register_component(name, component, contracts[name])
    runtime = create_runtime_registry_from_platform_layer(platform)
    gateway = EnterpriseApiGateway(platform_layer=platform, runtime_registry=runtime)
    persistence = PersistenceIntegrationLayer()
    observability = ObservabilityIntegrationLayer(
        platform_layer=platform,
        runtime_registry=runtime,
        api_gateway=gateway,
        persistence_layer=persistence,
    )
    return DeploymentReadinessLayer(
        platform,
        runtime,
        gateway,
        create_config(profile),
        persistence,
        observability,
    )
