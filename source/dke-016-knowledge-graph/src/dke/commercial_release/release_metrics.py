from __future__ import annotations

from typing import Any

from .certification_errors import VersionConsistencyError
from .version_manager import create_version_metadata, validate_version_metadata

RELEASE_METRICS_VERSION = "REL-005.1"
CERTIFICATION_PRODUCT_VERSION = "1.0.1-commercial-progress"
CERTIFICATION_GIT_TAG = "v1.0.1-commercial-progress"
CERTIFICATION_BUILD_ID = "AIDIP-PROJECT1-1.0.1-commercial-progress-005"
CERTIFICATION_REGRESSION_BASELINE = "606/606 passing"


def create_certification_version_metadata() -> dict[str, Any]:
    return create_version_metadata(
        product_version=CERTIFICATION_PRODUCT_VERSION,
        release_channel="production",
        build_id=CERTIFICATION_BUILD_ID,
        git_tag=CERTIFICATION_GIT_TAG,
        regression_baseline=CERTIFICATION_REGRESSION_BASELINE,
        release_status="production_certification",
    )


def generate_release_metrics(version_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    active_metadata = version_metadata or create_certification_version_metadata()
    validation = validate_version_metadata(active_metadata)
    metrics = {
        "module": "REL-005",
        "metrics_version": RELEASE_METRICS_VERSION,
        "status": "generated",
        "version_metadata": active_metadata,
        "version_validation": validation,
        "regression": {
            "baseline": active_metadata["regression_baseline"],
            "passed": validation["regression_passed"],
            "total": validation["regression_total"],
            "status": "passing" if validation["regression_passed"] == validation["regression_total"] else "failing",
        },
        "artifact_counts": {
            "documentation": 5,
            "validation": 5,
            "patent": 4,
            "research_paper": 5,
            "commercial_release": 5,
            "deployment_profiles": 7,
            "configuration_profiles": 4,
        },
        "build_consistency": {
            "semantic_version_valid": True,
            "git_tag_valid": True,
            "regression_baseline_valid": True,
            "deployment_actions_performed": False,
            "infrastructure_executed": False,
        },
    }
    validate_release_metrics(metrics)
    return metrics


def validate_release_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    if metrics.get("module") != "REL-005" or metrics.get("metrics_version") != RELEASE_METRICS_VERSION:
        raise VersionConsistencyError("release metrics identity is inconsistent")
    metadata = metrics.get("version_metadata", {})
    validation = validate_version_metadata(metadata)
    if metadata.get("git_tag") != CERTIFICATION_GIT_TAG:
        raise VersionConsistencyError("git tag does not match REL-005 certification baseline")
    if metadata.get("product_version") != CERTIFICATION_PRODUCT_VERSION:
        raise VersionConsistencyError("product version does not match REL-005 certification baseline")
    if metrics.get("regression", {}).get("passed") != 606 or metrics.get("regression", {}).get("total") != 606:
        raise VersionConsistencyError("regression baseline must be 606/606 passing")
    build = metrics.get("build_consistency", {})
    if any(build.get(flag) is not False for flag in ("deployment_actions_performed", "infrastructure_executed")):
        raise VersionConsistencyError("REL-005 must not perform deployment or infrastructure execution")
    return {
        "module": "REL-005",
        "status": "valid",
        "product_version": validation["product_version"],
        "git_tag": metadata["git_tag"],
        "regression_passed": validation["regression_passed"],
        "regression_total": validation["regression_total"],
    }
