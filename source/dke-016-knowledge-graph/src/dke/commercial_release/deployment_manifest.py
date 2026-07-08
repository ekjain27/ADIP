from __future__ import annotations

from typing import Any

from .compatibility_matrix import generate_compatibility_matrix, validate_compatibility_matrix
from .configuration_manager import generate_configuration_manifest, validate_configuration_manifest
from .deployment_errors import (
    DuplicateDeploymentIdentifierError,
    IncompleteDeploymentMetadataError,
    InconsistentUpgradePlanError,
    MalformedDeploymentManifestError,
)
from .deployment_profiles import (
    DEPLOYMENT_PROFILES_VERSION,
    SUPPORTED_DEPLOYMENT_TARGETS,
    generate_deployment_profile,
    list_deployment_profiles,
    validate_deployment_profile,
)
from .release_manifest import generate_release_manifest, validate_release_manifest
from .rollback_planner import generate_rollback_plan
from .upgrade_planner import generate_upgrade_plan

DEPLOYMENT_MANIFEST_VERSION = "REL-004.1"


def generate_deployment_manifest(profile_name: str = "enterprise_server") -> dict[str, Any]:
    profile = generate_deployment_profile(profile_name)
    release_manifest = generate_release_manifest()
    manifest = {
        "module": "REL-004",
        "manifest_version": DEPLOYMENT_MANIFEST_VERSION,
        "status": "generated",
        "deployment_profile": profile,
        "configuration_manifest": generate_configuration_manifest(),
        "compatibility_matrix": generate_compatibility_matrix(),
        "upgrade_plan": generate_upgrade_plan(profile_name),
        "rollback_plan": generate_rollback_plan(profile_name),
        "operations_checklist": generate_operations_checklist(profile_name),
        "release_metadata": release_manifest["version_metadata"],
        "integration_traces": _integration_traces(),
        "markdown_artifacts": _markdown_artifacts(profile["display_name"]),
        "integrity": {
            "deployment_actions_performed": False,
            "docker_executed": False,
            "kubernetes_executed": False,
            "dependencies_installed": False,
            "production_logic_modified": False,
        },
    }
    validate_deployment_package(manifest)
    return manifest


def generate_distribution_manifest(profile_name: str = "enterprise_server") -> dict[str, Any]:
    deployment_manifest = generate_deployment_manifest(profile_name)
    profile = deployment_manifest["deployment_profile"]
    inventory = (
        {"artifact_id": "package-manifest", "artifact_type": "distribution", "source": "REL-001 package metadata"},
        {"artifact_id": "deployment-bundle-manifest", "artifact_type": "distribution", "source": "REL-002 bundle reference"},
        {"artifact_id": "installation-manifest", "artifact_type": "installation", "source": "REL-004 deployment profile"},
        {"artifact_id": "configuration-manifest", "artifact_type": "configuration", "source": "REL-004 configuration manifest"},
        {"artifact_id": "security-compliance-manifest", "artifact_type": "compliance", "source": "REL-003 compliance reference"},
        {"artifact_id": "validation-baseline", "artifact_type": "validation", "source": "VB-001 through VB-005"},
        {"artifact_id": "documentation-package", "artifact_type": "documentation", "source": "DOC-001 through DOC-005"},
    )
    return {
        "module": "REL-004",
        "manifest_version": DEPLOYMENT_MANIFEST_VERSION,
        "status": "generated",
        "deployment_id": profile["deployment_id"],
        "profile_name": profile["profile_name"],
        "package_manifest": deployment_manifest["release_metadata"],
        "deployment_bundle_manifest": {
            "bundle_id": f"bundle-{profile['profile_name']}",
            "deployment_id": profile["deployment_id"],
            "deployment_actions_performed": False,
        },
        "installation_manifest": {
            "installation_id": f"install-{profile['profile_name']}",
            "deployment_id": profile["deployment_id"],
            "installation_actions_performed": False,
        },
        "distribution_inventory": inventory,
        "inventory_count": len(inventory),
    }


def generate_operations_checklist(profile_name: str = "enterprise_server") -> dict[str, Any]:
    profile = generate_deployment_profile(profile_name)
    return {
        "module": "REL-004",
        "checklist_version": DEPLOYMENT_MANIFEST_VERSION,
        "deployment_id": profile["deployment_id"],
        "health_check_manifest": (
            "verify runtime process status",
            "verify API health endpoint configuration",
            "verify provenance and governance health reports",
            "verify validation baseline availability",
        ),
        "startup_checklist": (
            "review release manifest",
            "apply operator-managed configuration",
            "start runtime using approved operations procedure",
            "capture startup evidence",
        ),
        "shutdown_checklist": (
            "record shutdown reason",
            "stop runtime using approved operations procedure",
            "preserve logs and audit evidence",
            "confirm no deployment action was executed by REL-004",
        ),
        "maintenance_checklist": (
            "review release notes",
            "review validation reports",
            "review dependency and compliance manifests",
            "archive operational evidence",
        ),
        "deployment_actions_performed": False,
    }


def validate_deployment_package(package: dict[str, Any]) -> dict[str, Any]:
    if package.get("module") != "REL-004":
        raise MalformedDeploymentManifestError("deployment package must be REL-004")
    profile = package.get("deployment_profile")
    if not isinstance(profile, dict):
        raise IncompleteDeploymentMetadataError("deployment_profile is required")
    profile_validation = validate_deployment_profile(profile)
    validate_configuration_manifest(package.get("configuration_manifest", {}))
    validate_compatibility_matrix(package.get("compatibility_matrix", {}))
    validate_release_manifest(generate_release_manifest(package["release_metadata"]))
    upgrade = package.get("upgrade_plan", {})
    rollback = package.get("rollback_plan", {})
    if upgrade.get("deployment_id") != profile_validation["deployment_id"]:
        raise InconsistentUpgradePlanError("upgrade plan deployment_id does not match profile")
    if rollback.get("deployment_id") != profile_validation["deployment_id"]:
        raise InconsistentUpgradePlanError("rollback plan deployment_id does not match profile")
    if upgrade.get("deployment_actions_performed") is not False or rollback.get("deployment_actions_performed") is not False:
        raise InconsistentUpgradePlanError("upgrade and rollback plans must not execute deployment actions")
    integrity = package.get("integrity", {})
    if any(integrity.get(key) is not False for key in integrity):
        raise MalformedDeploymentManifestError("REL-004 must not execute deployment, Docker, Kubernetes, or install actions")
    _validate_unique_deployment_ids(package)
    return {
        "module": "REL-004",
        "status": "valid",
        "deployment_id": profile_validation["deployment_id"],
        "profile_name": profile_validation["profile_name"],
    }


def _validate_unique_deployment_ids(package: dict[str, Any]) -> None:
    ids = [package["deployment_profile"]["deployment_id"]]
    ids.extend(row["deployment_id"] for row in package["compatibility_matrix"]["rows"])
    if len(ids) != len(set(ids)):
        expected_duplicate = package["deployment_profile"]["deployment_id"] in ids[1:]
        if not expected_duplicate:
            raise DuplicateDeploymentIdentifierError("duplicate deployment identifiers")


def _integration_traces() -> dict[str, Any]:
    return {
        "commercial_release": {
            "REL-001": "version and release metadata",
            "REL-002": "release bundle reference",
            "REL-003": "security, compliance, and licensing reference",
        },
        "documentation": tuple(f"DOC-{index:03d}" for index in range(1, 6)),
        "validation": tuple(f"VB-{index:03d}" for index in range(1, 6)),
    }


def _markdown_artifacts(display_name: str) -> dict[str, str]:
    title = f"{display_name} Deployment"
    return {
        "deployment_guide": f"# Deployment Guide\n\nTarget: {title}\n\nThis guide prepares deployment metadata only and does not deploy software.",
        "installation_guide": f"# Installation Guide\n\nTarget: {title}\n\nInstallation steps are operator-managed and not executed by REL-004.",
        "upgrade_guide": f"# Upgrade Guide\n\nTarget: {title}\n\nUpgrade planning is documented without performing migration.",
        "operations_guide": f"# Operations Guide\n\nTarget: {title}\n\nOperations checklists are generated for enterprise readiness.",
    }


def generate_all_deployment_profiles_manifest() -> dict[str, Any]:
    profiles = list_deployment_profiles()
    ids = tuple(profile["deployment_id"] for profile in profiles)
    if len(ids) != len(set(ids)):
        raise DuplicateDeploymentIdentifierError("duplicate deployment identifiers")
    return {
        "module": "REL-004",
        "manifest_version": DEPLOYMENT_PROFILES_VERSION,
        "status": "generated",
        "supported_targets": SUPPORTED_DEPLOYMENT_TARGETS,
        "profiles": profiles,
        "profile_count": len(profiles),
    }
