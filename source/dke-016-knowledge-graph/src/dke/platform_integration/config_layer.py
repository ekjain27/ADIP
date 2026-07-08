from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any, Mapping

from .api_gateway import EnterpriseApiGateway
from .config_errors import FrozenConfigMutationError, InvalidConfigTypeError, MissingConfigValueError
from .config_profiles import (
    CONFIG_SCHEMA,
    DETERMINISTIC_CONFIG_TIMESTAMP,
    ConfigFieldSpec,
    default_profile_values,
    normalize_profile,
)
from .platform_integration_layer import PlatformIntegrationLayer
from .runtime_registry import UnifiedPlatformRuntimeRegistry


@dataclass(frozen=True)
class PlatformConfig:
    profile: str
    values: Mapping[str, Any]
    frozen: bool = False
    created_at: str = DETERMINISTIC_CONFIG_TIMESTAMP
    updated_at: str = DETERMINISTIC_CONFIG_TIMESTAMP

    def __post_init__(self) -> None:
        normalized_profile = normalize_profile(self.profile)
        object.__setattr__(self, "profile", normalized_profile)
        object.__setattr__(self, "values", MappingProxyType(dict(sorted(self.values.items()))))

    def snapshot(self) -> dict[str, Any]:
        return {
            "module": "PI-005",
            "profile": self.profile,
            "frozen": self.frozen,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "values": dict(self.values),
        }


def create_config(profile: str, values: Mapping[str, Any] | None = None) -> PlatformConfig:
    normalized_profile = normalize_profile(profile)
    merged = default_profile_values(normalized_profile)
    merged.update(dict(values or {}))
    merged["profile"] = normalized_profile
    config = PlatformConfig(profile=normalized_profile, values=merged)
    validate_config(config)
    return config


def validate_config(config: PlatformConfig) -> dict[str, Any]:
    if not isinstance(config, PlatformConfig):
        raise InvalidConfigTypeError("config must be a PlatformConfig")
    schema = _schema_by_key()
    for key, spec in schema.items():
        if spec.required and key not in config.values:
            raise MissingConfigValueError(f"missing required config value: {key}")
        if key in config.values and not isinstance(config.values[key], spec.value_type):
            raise InvalidConfigTypeError(
                f"config value {key} must be {spec.value_type.__name__}, got {type(config.values[key]).__name__}"
            )
    if config.values.get("profile") != config.profile:
        raise InvalidConfigTypeError("config profile value must match config profile")
    return {
        "module": "PI-005",
        "status": "valid",
        "profile": config.profile,
        "field_count": len(config.values),
        "schema": tuple(spec.metadata() for spec in CONFIG_SCHEMA),
    }


def freeze_config(config: PlatformConfig) -> PlatformConfig:
    validate_config(config)
    return replace(config, frozen=True, values=dict(config.values), updated_at=DETERMINISTIC_CONFIG_TIMESTAMP)


def override_config(config: PlatformConfig, overrides: Mapping[str, Any]) -> PlatformConfig:
    if config.frozen:
        raise FrozenConfigMutationError(f"configuration snapshot is frozen: {config.profile}")
    if not isinstance(overrides, Mapping):
        raise InvalidConfigTypeError("config overrides must be a mapping")
    values = dict(config.values)
    values.update(dict(overrides))
    values["profile"] = config.profile
    updated = PlatformConfig(
        profile=config.profile,
        values=values,
        frozen=False,
        created_at=config.created_at,
        updated_at=DETERMINISTIC_CONFIG_TIMESTAMP,
    )
    validate_config(updated)
    return updated


def export_config_snapshot(config: PlatformConfig) -> dict[str, Any]:
    validate_config(config)
    return config.snapshot()


def get_config_value(config: PlatformConfig, key: str) -> Any:
    validate_config(config)
    if key not in config.values:
        raise MissingConfigValueError(f"missing config value: {key}")
    return config.values[key]


def platform_config_metadata(config: PlatformConfig, platform_layer: PlatformIntegrationLayer) -> dict[str, Any]:
    validate_config(config)
    return {
        "module": "PI-005",
        "integration": "PI-001",
        "profile": config.profile,
        "component_count": len(platform_layer.list_components()),
        "strict_validation": config.values["strict_validation"],
    }


def runtime_config_metadata(config: PlatformConfig, runtime_registry: UnifiedPlatformRuntimeRegistry) -> dict[str, Any]:
    validate_config(config)
    return {
        "module": "PI-005",
        "integration": "PI-002",
        "profile": config.profile,
        "component_count": len(runtime_registry.list_runtime_components()),
        "runtime_registry_enabled": config.values["runtime_registry_enabled"],
    }


def gateway_config_metadata(config: PlatformConfig, gateway: EnterpriseApiGateway) -> dict[str, Any]:
    validate_config(config)
    return {
        "module": "PI-005",
        "integration": "PI-004",
        "profile": config.profile,
        "route_count": len(gateway.list_routes()),
        "gateway_enabled": config.values["gateway_enabled"],
    }


def _schema_by_key() -> dict[str, ConfigFieldSpec]:
    return {spec.key: spec for spec in CONFIG_SCHEMA}
