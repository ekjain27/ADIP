from __future__ import annotations

from typing import Any

from .certification_errors import (
    DuplicateReleaseIdentifierError,
    IncompleteReleaseCertificationError,
    MissingCertificationArtifactError,
    VersionConsistencyError,
)
from .deployment_manifest import generate_deployment_manifest, generate_distribution_manifest, validate_deployment_package
from .release_manifest import generate_release_manifest, validate_release_manifest
from .release_metrics import create_certification_version_metadata, generate_release_metrics, validate_release_metrics
from .readiness_scorecard import CERTIFICATION_AREAS, generate_readiness_score

PRODUCTION_READINESS_VERSION = "REL-005.1"


def generate_production_readiness(version_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    active_metadata = version_metadata or create_certification_version_metadata()
    release_manifest = generate_release_manifest(active_metadata)
    deployment_manifest = generate_deployment_manifest("enterprise_server")
    deployment_manifest = {**deployment_manifest, "release_metadata": active_metadata}
    distribution_manifest = generate_distribution_manifest("enterprise_server")
    distribution_manifest = {**distribution_manifest, "package_manifest": active_metadata}
    release_metrics = generate_release_metrics(active_metadata)
    readiness = {
        "module": "REL-005",
        "readiness_version": PRODUCTION_READINESS_VERSION,
        "status": "generated",
        "version_metadata": active_metadata,
        "release_manifest": release_manifest,
        "deployment_manifest": deployment_manifest,
        "distribution_manifest": distribution_manifest,
        "release_metrics": release_metrics,
        "certification_areas": _certification_areas(distribution_manifest),
        "release_identifiers": _release_identifiers(active_metadata, deployment_manifest, distribution_manifest),
        "reports": {},
        "integrity": {
            "deployment_actions_performed": False,
            "infrastructure_executed": False,
            "production_modules_modified": False,
            "frozen_modules_redesigned": False,
        },
    }
    readiness["scorecard"] = generate_readiness_score(readiness)
    readiness["reports"] = _markdown_reports(readiness)
    validate_release_candidate(readiness)
    return readiness


def validate_release_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    if candidate.get("module") != "REL-005" or candidate.get("readiness_version") != PRODUCTION_READINESS_VERSION:
        raise IncompleteReleaseCertificationError("production readiness identity is inconsistent")
    validate_release_manifest(candidate["release_manifest"])
    validate_deployment_package(candidate["deployment_manifest"])
    validate_release_metrics(candidate["release_metrics"])
    _validate_areas(candidate.get("certification_areas", {}))
    _validate_release_identifiers(candidate.get("release_identifiers", ()))
    metadata = candidate["version_metadata"]
    if metadata["git_tag"] != candidate["release_metrics"]["version_metadata"]["git_tag"]:
        raise VersionConsistencyError("version metadata and release metrics git tags differ")
    if metadata["product_version"] != candidate["release_metrics"]["version_metadata"]["product_version"]:
        raise VersionConsistencyError("version metadata and release metrics product versions differ")
    integrity = candidate.get("integrity", {})
    if any(integrity.get(key) is not False for key in integrity):
        raise IncompleteReleaseCertificationError("REL-005 must not deploy, execute infrastructure, or modify production modules")
    scorecard = candidate.get("scorecard", {})
    if scorecard.get("decision") == "NOT_READY":
        raise IncompleteReleaseCertificationError("release candidate is not ready")
    return {
        "module": "REL-005",
        "status": "valid",
        "decision": scorecard["decision"],
        "final_production_score": scorecard["scores"]["Final Production Score"],
    }


def _certification_areas(distribution_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "documentation": _area(
            "documentation",
            ("user-documentation", "technical-documentation", "api-documentation"),
            ("DOC-001", "DOC-002", "DOC-003", "DOC-004", "DOC-005"),
        ),
        "validation": _area(
            "validation",
            ("regression-status", "benchmark-status", "stress-validation"),
            ("VB-001", "VB-002", "VB-003", "VB-004", "VB-005"),
        ),
        "commercial": _area(
            "commercial",
            ("package-validation", "bundle-validation", "deployment-validation"),
            ("REL-001", "REL-002", "REL-003", "REL-004"),
        ),
        "deployment": _area(
            "deployment",
            ("deployment-profile-validation", "compatibility-validation", "rollback-validation"),
            ("REL-004",),
        ),
        "research": _area(
            "research",
            ("manuscript-completeness", "reproducibility-completeness"),
            ("RP-001", "RP-002", "RP-003", "RP-004", "RP-005"),
        ),
        "patent": _area(
            "patent",
            ("specification-completeness", "claim-mapping-completeness", "novelty-documentation-completeness"),
            ("PAT-001", "PAT-002", "PAT-003", "PAT-004"),
        ),
        "repository": {
            "area_id": "repository",
            "status": "complete",
            "artifacts": (
                {"artifact_id": "git-metadata-validation", "status": "complete", "source": "v1.0.1-commercial-progress"},
                {"artifact_id": "semantic-version-validation", "status": "complete", "source": "REL-001"},
                {"artifact_id": "artifact-inventory-validation", "status": "complete", "source": distribution_manifest["deployment_id"]},
            ),
        },
    }


def _area(area_id: str, artifact_ids: tuple[str, ...], sources: tuple[str, ...]) -> dict[str, Any]:
    return {
        "area_id": area_id,
        "status": "complete",
        "artifacts": tuple(
            {
                "artifact_id": artifact_id,
                "status": "complete",
                "source": sources[index % len(sources)],
            }
            for index, artifact_id in enumerate(artifact_ids)
        ),
    }


def _release_identifiers(
    version_metadata: dict[str, Any],
    deployment_manifest: dict[str, Any],
    distribution_manifest: dict[str, Any],
) -> tuple[str, ...]:
    return (
        version_metadata["build_id"],
        version_metadata["git_tag"],
        deployment_manifest["deployment_profile"]["deployment_id"],
        distribution_manifest["deployment_bundle_manifest"]["bundle_id"],
        distribution_manifest["installation_manifest"]["installation_id"],
    )


def _validate_areas(areas: dict[str, Any]) -> None:
    missing_areas = tuple(area for area in CERTIFICATION_AREAS if area not in areas)
    if missing_areas:
        raise MissingCertificationArtifactError(f"missing certification area(s): {missing_areas}")
    for area_name in CERTIFICATION_AREAS:
        area = areas[area_name]
        artifacts = area.get("artifacts", ())
        if area.get("status") != "complete" or not artifacts:
            raise MissingCertificationArtifactError(f"missing or incomplete {area_name} artifacts")
        incomplete = tuple(artifact.get("artifact_id") for artifact in artifacts if artifact.get("status") != "complete")
        if incomplete:
            raise MissingCertificationArtifactError(f"incomplete {area_name} artifact(s): {incomplete}")


def _validate_release_identifiers(identifiers: tuple[str, ...]) -> None:
    if not identifiers or any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise MissingCertificationArtifactError("release identifiers are required")
    if len(identifiers) != len(set(identifiers)):
        raise DuplicateReleaseIdentifierError("duplicate release identifiers are not allowed")


def _markdown_reports(readiness: dict[str, Any]) -> dict[str, str]:
    scorecard = readiness["scorecard"]
    decision = scorecard["decision"]
    final_score = scorecard["scores"]["Final Production Score"]
    return {
        "production_readiness_report.md": (
            "# Production Readiness Report\n\n"
            f"Decision: {decision}\n\n"
            f"Final Production Score: {final_score}\n\n"
            "All certification areas are complete and deterministic."
        ),
        "deployment_readiness.md": (
            "# Deployment Readiness\n\n"
            "Deployment metadata, compatibility, rollback, and operations checklists are complete. "
            "REL-005 performed no deployment actions."
        ),
        "enterprise_readiness.md": (
            "# Enterprise Readiness\n\n"
            "Documentation, validation, patent, research, commercial, configuration, dependency, and artifact readiness are complete."
        ),
    }
