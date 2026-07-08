from __future__ import annotations

from typing import Any

from .specification_errors import InconsistentSpecificationManifestError

SPECIFICATION_MANIFEST_VERSION = "PAT-004.1"


def generate_specification_manifest(
    specification: dict[str, Any],
    figure_manifest: dict[str, Any],
    patent_manifest: dict[str, Any],
    claims_manifest: dict[str, Any],
    novelty_manifest: dict[str, Any],
    documentation_trace: dict[str, Any],
    runtime_registry: dict[str, Any],
    completeness_report: dict[str, Any],
) -> dict[str, Any]:
    if specification.get("module") != "PAT-004" or figure_manifest.get("module") != "PAT-004":
        raise InconsistentSpecificationManifestError("inconsistent PAT-004 manifest source")
    if completeness_report.get("status") != "complete":
        raise InconsistentSpecificationManifestError("incomplete specification cannot be manifested")
    return {
        "module": "PAT-004",
        "manifest_version": SPECIFICATION_MANIFEST_VERSION,
        "status": "generated",
        "specification": specification,
        "figure_manifest": figure_manifest,
        "source_manifests": {
            "PAT-001": patent_manifest["manifest_version"],
            "PAT-002": claims_manifest["manifest_version"],
            "PAT-003": novelty_manifest["manifest_version"],
        },
        "documentation_trace": documentation_trace,
        "runtime_registry": runtime_registry,
        "completeness_report": completeness_report,
        "legal_notice": "Patent specification support artifact only; professional legal review is required before filing.",
    }
