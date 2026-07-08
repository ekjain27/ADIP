from __future__ import annotations

import re
from typing import Any

from .release_errors import (
    InvalidGitTagError,
    InvalidRegressionBaselineError,
    InvalidVersionMetadataError,
    UnsupportedReleaseChannelError,
)

VERSION_METADATA_VERSION = "REL-001.1"
DEFAULT_PRODUCT_NAME = "AI Decision Intelligence Platform - Project-1"
DEFAULT_PRODUCT_VERSION = "1.0.0-pre-release"
DEFAULT_RELEASE_CHANNEL = "pre_release"
DEFAULT_BUILD_ID = "AIDIP-PROJECT1-1.0.0-pre-release-001"
DEFAULT_GIT_TAG = "v1.0.0-pre-release"
DEFAULT_REGRESSION_BASELINE = "535/535 passing"
DEFAULT_RELEASE_STATUS = "release_candidate"
SUPPORTED_RELEASE_CHANNELS = ("development", "alpha", "beta", "pre_release", "production")

_SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")
_GIT_TAG_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")
_REGRESSION_RE = re.compile(r"^(0|[1-9]\d*)/(0|[1-9]\d*) passing$")


def create_version_metadata(
    product_name: str = DEFAULT_PRODUCT_NAME,
    product_version: str = DEFAULT_PRODUCT_VERSION,
    release_channel: str = DEFAULT_RELEASE_CHANNEL,
    build_id: str = DEFAULT_BUILD_ID,
    git_tag: str = DEFAULT_GIT_TAG,
    regression_baseline: str = DEFAULT_REGRESSION_BASELINE,
    release_status: str = DEFAULT_RELEASE_STATUS,
) -> dict[str, Any]:
    metadata = {
        "module": "REL-001",
        "metadata_version": VERSION_METADATA_VERSION,
        "status": "generated",
        "product_name": product_name,
        "product_version": product_version,
        "release_channel": release_channel,
        "build_id": build_id,
        "git_tag": git_tag,
        "regression_baseline": regression_baseline,
        "release_status": release_status,
        "external_services_required": False,
        "deployment_actions_performed": False,
    }
    validate_version_metadata(metadata)
    return metadata


def validate_version_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    product_name = metadata.get("product_name")
    if not isinstance(product_name, str) or not product_name.strip():
        raise InvalidVersionMetadataError("product_name is required")
    product_version = metadata.get("product_version")
    if not isinstance(product_version, str) or not _SEMVER_RE.match(product_version):
        raise InvalidVersionMetadataError(f"invalid semantic version: {product_version}")
    release_channel = metadata.get("release_channel")
    if release_channel not in SUPPORTED_RELEASE_CHANNELS:
        raise UnsupportedReleaseChannelError(f"unsupported release channel: {release_channel}")
    build_id = metadata.get("build_id")
    if not isinstance(build_id, str) or not build_id.strip():
        raise InvalidVersionMetadataError("build_id is required")
    git_tag = metadata.get("git_tag")
    if not isinstance(git_tag, str) or not _GIT_TAG_RE.match(git_tag):
        raise InvalidGitTagError(f"invalid git tag: {git_tag}")
    regression_baseline = metadata.get("regression_baseline")
    if not isinstance(regression_baseline, str):
        raise InvalidRegressionBaselineError("regression_baseline is required")
    match = _REGRESSION_RE.match(regression_baseline)
    if not match:
        raise InvalidRegressionBaselineError(f"invalid regression baseline: {regression_baseline}")
    passed, total = (int(match.group(1)), int(match.group(2)))
    if passed > total or total == 0:
        raise InvalidRegressionBaselineError(f"invalid regression baseline: {regression_baseline}")
    if metadata.get("deployment_actions_performed") is not False:
        raise InvalidVersionMetadataError("REL-001 must not perform deployment actions")
    return {
        "module": "REL-001",
        "status": "valid",
        "product_version": product_version,
        "release_channel": release_channel,
        "git_tag": git_tag,
        "regression_passed": passed,
        "regression_total": total,
    }
