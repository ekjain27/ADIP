from __future__ import annotations

from copy import deepcopy
from typing import Any

from .deployment_errors import IncompleteConfigurationError

CONFIGURATION_MANAGER_VERSION = "REL-004.1"
SUPPORTED_CONFIGURATION_PROFILES: tuple[str, ...] = ("default", "production", "enterprise", "development")

_CONFIGURATIONS: dict[str, dict[str, Any]] = {
    "default": {
        "runtime": {"mode": "standard", "debug": False, "telemetry": "configured"},
        "security": {"secrets_source": "externalized", "network_policy": "environment-defined"},
        "observability": {"health_checks": True, "structured_logs": True, "metrics": True},
        "governance": {"provenance_required": True, "audit_logging": True},
    },
    "production": {
        "runtime": {"mode": "production", "debug": False, "telemetry": "required"},
        "security": {"secrets_source": "enterprise-secret-store", "network_policy": "restricted"},
        "observability": {"health_checks": True, "structured_logs": True, "metrics": True},
        "governance": {"provenance_required": True, "audit_logging": True},
    },
    "enterprise": {
        "runtime": {"mode": "enterprise", "debug": False, "telemetry": "required"},
        "security": {"secrets_source": "enterprise-managed", "network_policy": "enterprise-approved"},
        "observability": {"health_checks": True, "structured_logs": True, "metrics": True},
        "governance": {"provenance_required": True, "audit_logging": True},
    },
    "development": {
        "runtime": {"mode": "development", "debug": True, "telemetry": "local"},
        "security": {"secrets_source": "developer-local", "network_policy": "local-only"},
        "observability": {"health_checks": True, "structured_logs": True, "metrics": False},
        "governance": {"provenance_required": True, "audit_logging": True},
    },
}


def generate_configuration(configuration_id: str = "default") -> dict[str, Any]:
    if configuration_id not in SUPPORTED_CONFIGURATION_PROFILES:
        raise IncompleteConfigurationError(f"unsupported configuration profile: {configuration_id}")
    configuration = {
        "module": "REL-004",
        "configuration_version": CONFIGURATION_MANAGER_VERSION,
        "configuration_id": configuration_id,
        "configuration": deepcopy(_CONFIGURATIONS[configuration_id]),
        "secrets_embedded": False,
        "deployment_actions_performed": False,
    }
    validate_configuration(configuration)
    return configuration


def generate_configuration_manifest() -> dict[str, Any]:
    configurations = tuple(generate_configuration(configuration_id) for configuration_id in SUPPORTED_CONFIGURATION_PROFILES)
    manifest = {
        "module": "REL-004",
        "manifest_version": CONFIGURATION_MANAGER_VERSION,
        "status": "generated",
        "configurations": configurations,
        "configuration_count": len(configurations),
    }
    validate_configuration_manifest(manifest)
    return manifest


def validate_configuration(configuration: dict[str, Any]) -> dict[str, Any]:
    configuration_id = configuration.get("configuration_id")
    if configuration_id not in SUPPORTED_CONFIGURATION_PROFILES:
        raise IncompleteConfigurationError(f"unsupported configuration profile: {configuration_id}")
    payload = configuration.get("configuration")
    if not isinstance(payload, dict):
        raise IncompleteConfigurationError("configuration payload is required")
    required_sections = ("runtime", "security", "observability", "governance")
    missing = tuple(section for section in required_sections if not payload.get(section))
    if missing:
        raise IncompleteConfigurationError(f"missing configuration section(s): {missing}")
    if configuration.get("secrets_embedded") is not False:
        raise IncompleteConfigurationError("configuration must not embed secrets")
    return {"module": "REL-004", "status": "valid", "configuration_id": configuration_id}


def validate_configuration_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    configurations = manifest.get("configurations", ())
    ids = tuple(configuration.get("configuration_id") for configuration in configurations)
    if len(ids) != len(set(ids)):
        raise IncompleteConfigurationError("duplicate configuration identifiers")
    for configuration in configurations:
        validate_configuration(configuration)
    expected = set(SUPPORTED_CONFIGURATION_PROFILES)
    if set(ids) != expected:
        raise IncompleteConfigurationError("configuration manifest does not cover all supported profiles")
    return {"module": "REL-004", "status": "valid", "configuration_count": len(ids)}
