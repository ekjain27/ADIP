import pytest

from platform_integration import (
    EnterpriseApiGateway,
    FrozenConfigMutationError,
    InvalidConfigProfileError,
    InvalidConfigTypeError,
    MissingConfigValueError,
    PlatformContract,
    PlatformIntegrationLayer,
    RuntimeComponentMetadata,
    UnifiedPlatformRuntimeRegistry,
    create_config,
    export_config_snapshot,
    freeze_config,
    gateway_config_metadata,
    get_config_value,
    override_config,
    platform_config_metadata,
    runtime_config_metadata,
    validate_config,
)


class EchoComponent:
    def execute(self, payload):
        return payload


def test_default_local_config():
    config = create_config("local")
    assert config.profile == "local"
    assert config.values["debug_enabled"] is True
    assert config.values["strict_validation"] is True
    assert config.values["max_pipeline_steps"] == 10
    assert validate_config(config)["status"] == "valid"


def test_test_staging_production_profiles():
    test_config = create_config("test")
    staging_config = create_config("staging")
    production_config = create_config("production")
    assert test_config.values["debug_enabled"] is True
    assert test_config.values["max_pipeline_steps"] == 5
    assert staging_config.values["debug_enabled"] is False
    assert production_config.values["max_pipeline_steps"] == 25


def test_invalid_profile_rejected():
    with pytest.raises(InvalidConfigProfileError, match="invalid configuration profile"):
        create_config("qa")


def test_missing_required_value_rejected():
    config = create_config("local")
    bad_values = dict(config.values)
    del bad_values["platform_name"]
    bad_config = type(config)(profile="local", values=bad_values)
    with pytest.raises(MissingConfigValueError, match="missing required config value"):
        validate_config(bad_config)


def test_invalid_type_rejected():
    with pytest.raises(InvalidConfigTypeError, match="max_pipeline_steps must be int"):
        create_config("local", {"max_pipeline_steps": "many"})


def test_frozen_snapshot_immutability():
    config = freeze_config(create_config("test"))
    assert config.frozen is True
    with pytest.raises(TypeError):
        config.values["debug_enabled"] = False
    with pytest.raises(FrozenConfigMutationError, match="frozen"):
        override_config(config, {"debug_enabled": False})


def test_deterministic_snapshot_export():
    config = freeze_config(create_config("production"))
    first = export_config_snapshot(config)
    second = export_config_snapshot(config)
    assert first == second
    assert first["module"] == "PI-005"
    assert first["created_at"] == "1970-01-01T00:00:00Z"


def test_safe_override_behavior():
    config = create_config("local")
    updated = override_config(config, {"debug_enabled": False, "max_pipeline_steps": 3})
    assert updated.values["debug_enabled"] is False
    assert updated.values["max_pipeline_steps"] == 3
    assert config.values["debug_enabled"] is True
    assert get_config_value(updated, "max_pipeline_steps") == 3


def test_get_missing_config_value_rejected():
    config = create_config("local")
    with pytest.raises(MissingConfigValueError, match="missing config value"):
        get_config_value(config, "not_present")


def test_integration_with_pi_001_platform_layer():
    config = create_config("test")
    layer = PlatformIntegrationLayer()
    layer.register_component("DKE", EchoComponent(), PlatformContract("DKE", "knowledge_extraction", "execute"))
    metadata = platform_config_metadata(config, layer)
    assert metadata == {
        "module": "PI-005",
        "integration": "PI-001",
        "profile": "test",
        "component_count": 1,
        "strict_validation": True,
    }


def test_integration_with_pi_002_runtime_registry():
    config = create_config("staging")
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(
        RuntimeComponentMetadata(
            module_id="PI-005",
            name="Configuration Layer",
            phase="platform_integration",
            capabilities=("configuration",),
        )
    )
    metadata = runtime_config_metadata(config, registry)
    assert metadata["integration"] == "PI-002"
    assert metadata["component_count"] == 1
    assert metadata["runtime_registry_enabled"] is True


def test_integration_with_pi_004_gateway():
    config = create_config("production")
    gateway = EnterpriseApiGateway()
    metadata = gateway_config_metadata(config, gateway)
    assert metadata["integration"] == "PI-004"
    assert metadata["route_count"] == 5
    assert metadata["gateway_enabled"] is True
