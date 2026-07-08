from __future__ import annotations

from copy import deepcopy
from typing import Any

from .deployment_errors import IncompleteDeploymentMetadataError, UnsupportedDeploymentProfileError

DEPLOYMENT_PROFILES_VERSION = "REL-004.1"

SUPPORTED_DEPLOYMENT_TARGETS: tuple[str, ...] = (
    "local_workstation",
    "enterprise_server",
    "docker",
    "kubernetes",
    "cloud_vm",
    "air_gapped_enterprise",
    "evaluation_installation",
)

_PROFILE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "local_workstation": {
        "display_name": "Local Workstation",
        "environment_profile": "single-user local execution",
        "runtime_profile": "python-and-node-local-runtime",
        "resource_profile": {"cpu": "developer workstation", "memory": "moderate", "storage": "local filesystem"},
        "dependency_profile": ("python runtime", "node runtime", "local package dependencies"),
    },
    "enterprise_server": {
        "display_name": "Enterprise Server",
        "environment_profile": "managed internal server",
        "runtime_profile": "managed-service-runtime",
        "resource_profile": {"cpu": "server class", "memory": "enterprise workload", "storage": "managed volume"},
        "dependency_profile": ("python runtime", "node runtime", "enterprise configuration store"),
    },
    "docker": {
        "display_name": "Docker",
        "environment_profile": "container image runtime",
        "runtime_profile": "container-runtime",
        "resource_profile": {"cpu": "container quota", "memory": "container quota", "storage": "mounted volume"},
        "dependency_profile": ("container runtime", "image registry metadata", "environment variables"),
    },
    "kubernetes": {
        "display_name": "Kubernetes",
        "environment_profile": "orchestrated container platform",
        "runtime_profile": "kubernetes-workload-runtime",
        "resource_profile": {"cpu": "pod requests and limits", "memory": "pod requests and limits", "storage": "persistent volume"},
        "dependency_profile": ("cluster namespace", "deployment manifest", "service manifest", "config map"),
    },
    "cloud_vm": {
        "display_name": "Cloud VM",
        "environment_profile": "cloud-hosted virtual machine",
        "runtime_profile": "vm-managed-runtime",
        "resource_profile": {"cpu": "cloud instance class", "memory": "cloud instance class", "storage": "attached disk"},
        "dependency_profile": ("vm image metadata", "network policy", "runtime packages"),
    },
    "air_gapped_enterprise": {
        "display_name": "Air-gapped Enterprise",
        "environment_profile": "offline enterprise environment",
        "runtime_profile": "offline-managed-runtime",
        "resource_profile": {"cpu": "approved internal server", "memory": "approved internal server", "storage": "offline media"},
        "dependency_profile": ("offline package bundle", "offline documentation bundle", "checksum manifest"),
    },
    "evaluation_installation": {
        "display_name": "Evaluation Installation",
        "environment_profile": "time-boxed evaluation runtime",
        "runtime_profile": "evaluation-runtime",
        "resource_profile": {"cpu": "evaluation host", "memory": "evaluation host", "storage": "temporary workspace"},
        "dependency_profile": ("evaluation license metadata", "sample configuration", "local runtime packages"),
    },
}


def generate_deployment_profile(profile_name: str = "enterprise_server") -> dict[str, Any]:
    if profile_name not in SUPPORTED_DEPLOYMENT_TARGETS:
        raise UnsupportedDeploymentProfileError(f"unsupported deployment profile: {profile_name}")
    definition = deepcopy(_PROFILE_DEFINITIONS[profile_name])
    profile = {
        "module": "REL-004",
        "profile_version": DEPLOYMENT_PROFILES_VERSION,
        "deployment_id": f"deploy-{profile_name}",
        "profile_name": profile_name,
        "display_name": definition["display_name"],
        "environment_profile": definition["environment_profile"],
        "runtime_profile": definition["runtime_profile"],
        "resource_profile": definition["resource_profile"],
        "dependency_profile": definition["dependency_profile"],
        "deployment_actions_performed": False,
        "external_services_required": False,
    }
    validate_deployment_profile(profile)
    return profile


def list_deployment_profiles() -> tuple[dict[str, Any], ...]:
    return tuple(generate_deployment_profile(profile_name) for profile_name in SUPPORTED_DEPLOYMENT_TARGETS)


def validate_deployment_profile(profile: dict[str, Any]) -> dict[str, Any]:
    profile_name = profile.get("profile_name")
    if profile_name not in SUPPORTED_DEPLOYMENT_TARGETS:
        raise UnsupportedDeploymentProfileError(f"unsupported deployment profile: {profile_name}")
    required = (
        "deployment_id",
        "display_name",
        "environment_profile",
        "runtime_profile",
        "resource_profile",
        "dependency_profile",
    )
    missing = tuple(key for key in required if key not in profile or not profile[key])
    if missing:
        raise IncompleteDeploymentMetadataError(f"missing deployment metadata: {missing}")
    if profile.get("deployment_actions_performed") is not False:
        raise IncompleteDeploymentMetadataError("REL-004 must not perform deployment actions")
    return {
        "module": "REL-004",
        "status": "valid",
        "profile_name": profile_name,
        "deployment_id": profile["deployment_id"],
    }
