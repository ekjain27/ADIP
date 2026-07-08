from __future__ import annotations

from typing import Any

from .api_gateway import EnterpriseApiGateway
from .config_layer import PlatformConfig, validate_config
from .config_errors import InvalidConfigProfileError
from .config_profiles import normalize_profile
from .deployment_errors import (
    IncompatibleRuntimeStateError,
    IncompleteConfigurationError,
    MissingDeploymentComponentError,
    UnsupportedDeploymentProfileError,
)
from .deployment_manifest import VALID_DEPLOYMENT_PROFILES
from .observability_layer import ObservabilityIntegrationLayer
from .persistence_layer import PersistenceIntegrationLayer
from .platform_contracts import PLATFORM_COMPONENTS
from .platform_integration_layer import PlatformIntegrationLayer
from .runtime_registry import UnifiedPlatformRuntimeRegistry


class DeploymentReadinessValidator:
    REQUIRED_COMPONENTS = PLATFORM_COMPONENTS

    def validate_profile(self, profile: str) -> str:
        try:
            normalized = normalize_profile(profile)
        except InvalidConfigProfileError as exc:
            raise UnsupportedDeploymentProfileError(str(exc)) from exc
        if normalized not in VALID_DEPLOYMENT_PROFILES:
            raise UnsupportedDeploymentProfileError(f"unsupported deployment profile: {normalized}")
        return normalized

    def validate_platform_layer(self, platform_layer: PlatformIntegrationLayer) -> dict[str, Any]:
        components = platform_layer.list_components()
        missing = tuple(component for component in self.REQUIRED_COMPONENTS if component not in components)
        if missing:
            raise MissingDeploymentComponentError(f"missing required platform component(s): {', '.join(missing)}")
        return platform_layer.validate_platform(required_components=self.REQUIRED_COMPONENTS)

    def validate_runtime_registry(self, runtime_registry: UnifiedPlatformRuntimeRegistry) -> dict[str, Any]:
        try:
            dependencies = runtime_registry.validate_dependencies()
            compatibility = runtime_registry.validate_compatibility()
        except Exception as exc:
            raise IncompatibleRuntimeStateError(str(exc)) from exc
        return {
            "dependencies": dependencies,
            "compatibility": compatibility,
            "snapshot": runtime_registry.export_registry_snapshot(),
        }

    def validate_configuration(self, profile: str, config: PlatformConfig) -> dict[str, Any]:
        normalized = self.validate_profile(profile)
        if config.profile != normalized:
            raise IncompleteConfigurationError(f"configuration profile mismatch: {config.profile} != {normalized}")
        try:
            return validate_config(config)
        except Exception as exc:
            raise IncompleteConfigurationError(str(exc)) from exc

    def validate_gateway(self, gateway: EnterpriseApiGateway) -> dict[str, Any]:
        snapshot = gateway.export_gateway_snapshot()
        if snapshot["route_count"] == 0:
            raise MissingDeploymentComponentError("api gateway has no registered routes")
        return snapshot

    def validate_persistence(self, persistence_layer: PersistenceIntegrationLayer) -> dict[str, Any]:
        snapshot = persistence_layer.export_persistence_snapshot()
        backend_names = tuple(backend["name"] for backend in snapshot["backends"])
        if "memory" not in backend_names:
            raise MissingDeploymentComponentError("memory persistence backend is required")
        return snapshot

    def validate_observability(self, observability_layer: ObservabilityIntegrationLayer) -> dict[str, Any]:
        snapshot = observability_layer.export_observability_snapshot()
        if snapshot["health"]["health_check_count"] == 0:
            raise MissingDeploymentComponentError("observability health checks are required")
        return snapshot
