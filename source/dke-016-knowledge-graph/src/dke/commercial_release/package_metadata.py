from __future__ import annotations

from typing import Any

from .version_manager import create_version_metadata, validate_version_metadata

PACKAGE_METADATA_VERSION = "REL-001.1"


def generate_package_metadata(version_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    active_metadata = version_metadata or create_version_metadata()
    validation = validate_version_metadata(active_metadata)
    package_metadata = {
        "module": "REL-001",
        "package_metadata_version": PACKAGE_METADATA_VERSION,
        "status": "generated",
        "product": {
            "name": active_metadata["product_name"],
            "version": active_metadata["product_version"],
            "release_channel": active_metadata["release_channel"],
            "build_id": active_metadata["build_id"],
            "git_tag": active_metadata["git_tag"],
        },
        "baseline": {
            "regression_baseline": active_metadata["regression_baseline"],
            "regression_passed": validation["regression_passed"],
            "regression_total": validation["regression_total"],
        },
        "package_scope": {
            "release_infrastructure_only": True,
            "external_services_required": False,
            "deployment_actions_performed": False,
            "new_ai_capabilities_added": False,
        },
        "integrated_module_families": _integrated_module_families(),
    }
    return package_metadata


def _integrated_module_families() -> dict[str, tuple[str, ...]]:
    return {
        "documentation": tuple(f"DOC-{index:03d}" for index in range(1, 6)),
        "validation": tuple(f"VB-{index:03d}" for index in range(1, 6)),
        "patent": tuple(f"PAT-{index:03d}" for index in range(1, 5)),
        "research_paper": tuple(f"RP-{index:03d}" for index in range(1, 6)),
    }
