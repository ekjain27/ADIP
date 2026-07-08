from __future__ import annotations

from typing import Any

from .deployment_profiles import generate_deployment_profile
from .version_manager import create_version_metadata

ROLLBACK_PLANNER_VERSION = "REL-004.1"


def generate_rollback_plan(profile_name: str = "enterprise_server") -> dict[str, Any]:
    profile = generate_deployment_profile(profile_name)
    metadata = create_version_metadata()
    return {
        "module": "REL-004",
        "plan_version": ROLLBACK_PLANNER_VERSION,
        "rollback_id": f"rollback-{profile_name}",
        "deployment_id": profile["deployment_id"],
        "target_version": metadata["product_version"],
        "rollback_path": (
            "pause operator-managed rollout",
            "restore previous package snapshot",
            "restore previous configuration snapshot",
            "run validation and health checks",
            "record rollback evidence",
        ),
        "rollback_checklist": (
            "previous package snapshot identified",
            "previous configuration snapshot identified",
            "validation owner assigned",
            "audit evidence location recorded",
        ),
        "deployment_actions_performed": False,
    }
