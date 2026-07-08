from __future__ import annotations

from copy import deepcopy
from typing import Any

from .changelog_generator import generate_changelog
from .package_metadata import generate_package_metadata
from .release_errors import InconsistentReleaseManifestError
from .version_manager import create_version_metadata, validate_version_metadata

RELEASE_MANIFEST_VERSION = "REL-001.1"

_RELEASE_SNAPSHOT_CACHE: dict[str, Any] | None = None


def generate_release_manifest(version_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    active_metadata = version_metadata or create_version_metadata()
    validation = validate_version_metadata(active_metadata)
    package_metadata = generate_package_metadata(active_metadata)
    changelog = generate_changelog(active_metadata)
    manifest = {
        "module": "REL-001",
        "manifest_version": RELEASE_MANIFEST_VERSION,
        "status": "generated",
        "release_readiness_state": active_metadata["release_status"],
        "version_metadata": active_metadata,
        "version_validation": validation,
        "package_metadata": package_metadata,
        "changelog": changelog,
        "source_traces": _source_traces(),
        "integrity": {
            "external_services_required": False,
            "deployment_actions_performed": False,
            "frozen_modules_redesigned": False,
            "new_ai_decision_engine_capability_added": False,
        },
    }
    validate_release_manifest(manifest)
    return manifest


def export_release_snapshot(version_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    global _RELEASE_SNAPSHOT_CACHE
    if version_metadata is None:
        if _RELEASE_SNAPSHOT_CACHE is None:
            _RELEASE_SNAPSHOT_CACHE = generate_release_manifest()
        return deepcopy(_RELEASE_SNAPSHOT_CACHE)
    return deepcopy(generate_release_manifest(version_metadata))


def validate_release_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("module") != "REL-001" or manifest.get("manifest_version") != RELEASE_MANIFEST_VERSION:
        raise InconsistentReleaseManifestError("inconsistent REL-001 manifest identity")
    validation = validate_version_metadata(manifest["version_metadata"])
    product = manifest["package_metadata"]["product"]
    if product["version"] != validation["product_version"] or product["git_tag"] != validation["git_tag"]:
        raise InconsistentReleaseManifestError("package metadata does not match version metadata")
    traces = manifest.get("source_traces", {})
    required_families = ("documentation", "validation", "patent", "research_paper")
    missing = tuple(family for family in required_families if family not in traces or not traces[family])
    if missing:
        raise InconsistentReleaseManifestError(f"missing release source trace(s): {missing}")
    integrity = manifest.get("integrity", {})
    if any(integrity.get(key) is not False for key in integrity):
        raise InconsistentReleaseManifestError("REL-001 cannot perform deployment actions or add capabilities")
    return {
        "module": "REL-001",
        "status": "valid",
        "product_version": validation["product_version"],
        "release_channel": validation["release_channel"],
        "source_trace_family_count": len(required_families),
    }


def _source_traces() -> dict[str, Any]:
    return {
        "documentation": {f"DOC-{index:03d}": f"DOC-{index:03d}" for index in range(1, 6)},
        "validation": {f"VB-{index:03d}": f"VB-{index:03d}" for index in range(1, 6)},
        "patent": {
            "PAT-001": "PAT-001.1",
            "PAT-002": "PAT-002.1",
            "PAT-003": "PAT-003.1",
            "PAT-004": "PAT-004.1",
        },
        "research_paper": {
            "RP-001": "RP-001.1",
            "RP-002": "RP-002.1",
            "RP-003": "RP-003.1",
            "RP-004": "RP-004.1",
            "RP-005": "RP-005.1",
        },
        "official_baseline": {
            "git_tag": "v1.0.0-pre-release",
            "regression": "535/535 passing",
        },
    }
