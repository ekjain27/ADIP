from __future__ import annotations

from typing import Any

from .manuscript_assembler import assemble_manuscript, export_markdown_manuscript, validate_manuscript
from .publication_manifest import generate_publication_manifest
from .publication_package_profiles import generate_publication_profile
from .submission_checklist import generate_artifact_checklist, generate_submission_checklist


def validate_publication_package(package: dict[str, Any] | None = None) -> dict[str, Any]:
    active = package or generate_publication_manifest()
    manuscript_validation = validate_manuscript(active["manuscript"])
    if active["publication_completeness_report"]["status"] != "complete":
        from .publication_errors import InconsistentPublicationManifestError

        raise InconsistentPublicationManifestError("publication package is incomplete")
    return {
        "module": "RP-005",
        "status": "valid",
        "venue": active["publication_profile"]["venue"],
        "section_count": manuscript_validation["section_count"],
        "artifact_count": active["artifact_checklist"]["artifact_count"],
    }


__all__ = [
    "assemble_manuscript",
    "export_markdown_manuscript",
    "generate_artifact_checklist",
    "generate_publication_manifest",
    "generate_publication_profile",
    "generate_submission_checklist",
    "validate_manuscript",
    "validate_publication_package",
]
