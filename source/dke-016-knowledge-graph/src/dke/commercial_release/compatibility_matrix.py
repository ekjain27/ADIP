from __future__ import annotations

from typing import Any

from .deployment_profiles import SUPPORTED_DEPLOYMENT_TARGETS

COMPATIBILITY_MATRIX_VERSION = "REL-004.1"


def generate_compatibility_matrix() -> dict[str, Any]:
    rows = tuple(
        {
            "deployment_id": f"deploy-{profile_name}",
            "profile_name": profile_name,
            "compatible_release_channels": ("pre_release", "production") if profile_name != "development" else ("development",),
            "requires_external_service": False,
            "deployment_execution_supported": False,
            "configuration_profiles": _configuration_profiles(profile_name),
        }
        for profile_name in SUPPORTED_DEPLOYMENT_TARGETS
    )
    return {
        "module": "REL-004",
        "matrix_version": COMPATIBILITY_MATRIX_VERSION,
        "status": "generated",
        "rows": rows,
        "row_count": len(rows),
    }


def validate_compatibility_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    rows = matrix.get("rows", ())
    ids = tuple(row.get("deployment_id") for row in rows)
    if len(ids) != len(set(ids)):
        from .deployment_errors import DuplicateDeploymentIdentifierError

        raise DuplicateDeploymentIdentifierError("duplicate deployment identifiers in compatibility matrix")
    expected_ids = tuple(f"deploy-{profile_name}" for profile_name in SUPPORTED_DEPLOYMENT_TARGETS)
    if ids != expected_ids:
        from .deployment_errors import MalformedDeploymentManifestError

        raise MalformedDeploymentManifestError("compatibility matrix ordering or coverage is inconsistent")
    return {"module": "REL-004", "status": "valid", "row_count": len(rows)}


def _configuration_profiles(profile_name: str) -> tuple[str, ...]:
    if profile_name == "local_workstation":
        return ("default", "development")
    if profile_name == "evaluation_installation":
        return ("default", "development")
    if profile_name in {"enterprise_server", "air_gapped_enterprise"}:
        return ("enterprise", "production")
    return ("default", "production")
