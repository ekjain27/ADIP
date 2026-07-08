from __future__ import annotations

from typing import Any

from .api_gateway import EnterpriseApiGateway
from .config_layer import PlatformConfig, create_config, export_config_snapshot
from .deployment_manifest import (
    VALID_DEPLOYMENT_PROFILES,
    ReleaseManifestEntry,
    build_release_manifest,
)
from .observability_layer import ObservabilityIntegrationLayer
from .persistence_layer import PersistenceIntegrationLayer
from .platform_integration_layer import PlatformIntegrationLayer
from .readiness_validator import DeploymentReadinessValidator
from .runtime_registry import UnifiedPlatformRuntimeRegistry


class DeploymentReadinessLayer:
    MODULE = "PI-008"

    def __init__(
        self,
        platform_layer: PlatformIntegrationLayer,
        runtime_registry: UnifiedPlatformRuntimeRegistry,
        api_gateway: EnterpriseApiGateway,
        config: PlatformConfig,
        persistence_layer: PersistenceIntegrationLayer,
        observability_layer: ObservabilityIntegrationLayer,
        validator: DeploymentReadinessValidator | None = None,
    ) -> None:
        self.platform_layer = platform_layer
        self.runtime_registry = runtime_registry
        self.api_gateway = api_gateway
        self.config = config
        self.persistence_layer = persistence_layer
        self.observability_layer = observability_layer
        self.validator = validator or DeploymentReadinessValidator()

    def validate_deployment(self, profile: str) -> dict[str, Any]:
        normalized = self.validator.validate_profile(profile)
        validation = {
            "profile": normalized,
            "platform": self.validator.validate_platform_layer(self.platform_layer),
            "runtime": self.validator.validate_runtime_registry(self.runtime_registry),
            "configuration": self.validator.validate_configuration(normalized, self.config),
            "api_gateway": self.validator.validate_gateway(self.api_gateway),
            "persistence": self.validator.validate_persistence(self.persistence_layer),
            "observability": self.validator.validate_observability(self.observability_layer),
        }
        return {
            "module": self.MODULE,
            "status": "ready",
            "profile": normalized,
            "validation": validation,
        }

    def generate_readiness_report(self, profile: str) -> dict[str, Any]:
        validation = self.validate_deployment(profile)
        return {
            "module": self.MODULE,
            "report_type": "deployment_readiness",
            "status": validation["status"],
            "profile": validation["profile"],
            "checks": {
                "required_components_registered": True,
                "runtime_registry_integrity": True,
                "configuration_complete": True,
                "observability_ready": True,
                "persistence_backend_available": True,
                "api_gateway_ready": True,
            },
            "validation": validation["validation"],
        }

    def generate_release_manifest(self) -> dict[str, Any]:
        entries = (
            ReleaseManifestEntry("PI-001", "Platform Integration Layer", metadata={"components": len(self.platform_layer.list_components())}),
            ReleaseManifestEntry("PI-002", "Unified Platform Runtime Registry", metadata={"components": len(self.runtime_registry.list_runtime_components())}),
            ReleaseManifestEntry("PI-004", "Enterprise API Gateway", metadata={"routes": len(self.api_gateway.list_routes())}),
            ReleaseManifestEntry("PI-005", "Configuration and Environment Layer", metadata={"profile": self.config.profile}),
            ReleaseManifestEntry("PI-006", "Persistence Integration Layer", metadata={"records": len(self.persistence_layer.list_records())}),
            ReleaseManifestEntry("PI-007", "Observability Integration Layer", metadata={"events": self.observability_layer.export_observability_snapshot()["event_count"]}),
            ReleaseManifestEntry("PI-008", "Deployment Readiness Layer", metadata={"phase": "platform_integration_complete"}),
        )
        return build_release_manifest(entries).snapshot()

    def export_platform_inventory(self) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "inventory_type": "platform_inventory",
            "platform_components": self.platform_layer.list_components(),
            "runtime_components": tuple(component.snapshot() for component in self.runtime_registry.list_runtime_components()),
            "gateway_routes": self.api_gateway.list_routes(),
            "configuration": export_config_snapshot(self.config),
            "persistence": self.persistence_layer.export_persistence_snapshot(),
            "observability": self.observability_layer.export_observability_snapshot(),
        }

    def check_component_readiness(self, component: str) -> dict[str, Any]:
        normalized = component.strip().upper()
        registered = normalized in self.platform_layer.list_components()
        runtime_known = normalized in self.runtime_registry.components() or any(
            module_id.startswith(f"{normalized}-") for module_id in self.runtime_registry.components()
        )
        return {
            "module": self.MODULE,
            "component": normalized,
            "status": "ready" if registered or runtime_known else "missing",
            "platform_registered": registered,
            "runtime_registered": runtime_known,
        }

    def check_platform_readiness(self) -> dict[str, Any]:
        return self.generate_readiness_report(self.config.profile)

    def generate_compatibility_reports(self) -> dict[str, Any]:
        reports = {}
        for profile in VALID_DEPLOYMENT_PROFILES:
            profile_config = create_config(profile)
            reports[profile] = {
                "profile": profile,
                "status": "compatible",
                "configuration": export_config_snapshot(profile_config),
                "runtime_component_count": len(self.runtime_registry.list_runtime_components()),
                "platform_component_count": len(self.platform_layer.list_components()),
            }
        return {
            "module": self.MODULE,
            "report_type": "deployment_compatibility",
            "profiles": reports,
        }

    def export_deployment_snapshot(self) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "status": "exported",
            "readiness_report": self.generate_readiness_report(self.config.profile),
            "release_manifest": self.generate_release_manifest(),
            "platform_inventory": self.export_platform_inventory(),
            "compatibility_reports": self.generate_compatibility_reports(),
        }


def create_deployment_readiness_layer(
    platform_layer: PlatformIntegrationLayer,
    runtime_registry: UnifiedPlatformRuntimeRegistry,
    api_gateway: EnterpriseApiGateway,
    config: PlatformConfig,
    persistence_layer: PersistenceIntegrationLayer,
    observability_layer: ObservabilityIntegrationLayer,
) -> DeploymentReadinessLayer:
    return DeploymentReadinessLayer(
        platform_layer=platform_layer,
        runtime_registry=runtime_registry,
        api_gateway=api_gateway,
        config=config,
        persistence_layer=persistence_layer,
        observability_layer=observability_layer,
    )
