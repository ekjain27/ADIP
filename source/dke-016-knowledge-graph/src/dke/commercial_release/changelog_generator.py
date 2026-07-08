from __future__ import annotations

from typing import Any

from .version_manager import create_version_metadata, validate_version_metadata

CHANGELOG_VERSION = "REL-001.1"


def generate_changelog(version_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    active_metadata = version_metadata or create_version_metadata()
    validate_version_metadata(active_metadata)
    entries = (
        _entry("REL-001-001", "release_infrastructure", "Commercial release package initialized with deterministic version metadata."),
        _entry("REL-001-002", "version_management", "Release channels, semantic version validation, git tag validation, and regression baseline validation added."),
        _entry("REL-001-003", "package_metadata", "Package metadata, release manifest, release snapshot, and integrated module-family trace added."),
        _entry("REL-001-004", "non_deployment_scope", "Release layer records readiness state only and performs no external service or deployment action."),
    )
    return {
        "module": "REL-001",
        "changelog_version": CHANGELOG_VERSION,
        "status": "generated",
        "product_version": active_metadata["product_version"],
        "release_channel": active_metadata["release_channel"],
        "git_tag": active_metadata["git_tag"],
        "entries": entries,
        "entry_count": len(entries),
    }


def _entry(change_id: str, category: str, description: str) -> dict[str, Any]:
    return {
        "change_id": change_id,
        "category": category,
        "description": description,
        "frozen_module_redesign": False,
        "new_ai_capability": False,
    }
