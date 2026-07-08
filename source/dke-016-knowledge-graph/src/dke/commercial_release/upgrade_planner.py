from __future__ import annotations

from typing import Any

from .deployment_profiles import generate_deployment_profile, validate_deployment_profile
from .version_manager import create_version_metadata

UPGRADE_PLANNER_VERSION = "REL-004.1"


def generate_upgrade_plan(profile_name: str = "enterprise_server") -> dict[str, Any]:
    profile = generate_deployment_profile(profile_name)
    metadata = create_version_metadata()
    plan = {
        "module": "REL-004",
        "plan_version": UPGRADE_PLANNER_VERSION,
        "upgrade_id": f"upgrade-{profile_name}",
        "deployment_id": profile["deployment_id"],
        "from_version": metadata["product_version"],
        "to_version": metadata["product_version"],
        "upgrade_path": (
            "verify release metadata",
            "review compatibility matrix",
            "prepare configuration delta",
            "execute operator-managed upgrade outside REL-004",
            "validate health and provenance reports",
        ),
        "migration_checklist": (
            "confirm backup exists",
            "confirm rollback manifest is available",
            "confirm validation baseline is attached",
            "confirm documentation package is attached",
        ),
        "deployment_actions_performed": False,
    }
    validate_deployment_profile(profile)
    return plan
