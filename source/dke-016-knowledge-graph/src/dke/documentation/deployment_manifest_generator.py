from __future__ import annotations

from typing import Any

from .environment_documenter import SUPPORTED_DEPLOYMENT_ENVIRONMENTS
from .operations_errors import IncompleteDeploymentMetadataError, InconsistentDeploymentManifestError

DEPLOYMENT_MANIFEST_VERSION = "DOC-005.1"


def generate_deployment_manifest(
    architecture_manifest: dict[str, Any],
    developer_manifest: dict[str, Any],
    environment_documentation: dict[str, Any],
    readiness_report: dict[str, Any],
) -> dict[str, Any]:
    manifest = {
        "module": "DOC-005",
        "manifest_version": DEPLOYMENT_MANIFEST_VERSION,
        "status": "generated",
        "architecture_module": architecture_manifest.get("module"),
        "developer_module": developer_manifest.get("module"),
        "environments": tuple(item["environment"] for item in environment_documentation["environments"]),
        "readiness": readiness_report,
        "deployment_documentation_only": True,
    }
    validate_deployment_manifest(manifest)
    return manifest


def validate_deployment_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    required = ("module", "manifest_version", "status", "architecture_module", "developer_module", "environments", "readiness")
    missing = tuple(field for field in required if field not in manifest or manifest[field] in (None, ""))
    if missing:
        raise IncompleteDeploymentMetadataError(f"incomplete deployment metadata: {', '.join(missing)}")
    if manifest["module"] != "DOC-005" or manifest["manifest_version"] != DEPLOYMENT_MANIFEST_VERSION:
        raise InconsistentDeploymentManifestError("inconsistent deployment manifest identity")
    if tuple(manifest["environments"]) != SUPPORTED_DEPLOYMENT_ENVIRONMENTS:
        raise InconsistentDeploymentManifestError("inconsistent deployment manifest environments")
    return {"module": "DOC-005", "status": "valid", "environment_count": len(manifest["environments"])}
