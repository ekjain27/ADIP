from __future__ import annotations

from typing import Any

from .manuscript_assembler import assemble_manuscript, validate_manuscript
from .submission_checklist import generate_artifact_checklist, generate_submission_checklist

PUBLICATION_MANIFEST_VERSION = "RP-005.1"


def generate_publication_manifest(manuscript: dict[str, Any] | None = None, venue: str = "arXiv") -> dict[str, Any]:
    active = manuscript or assemble_manuscript(venue)
    validation = validate_manuscript(active)
    submission_checklist = generate_submission_checklist(active)
    artifact_checklist = generate_artifact_checklist(active)
    completeness_report = _completeness_report(active, validation, submission_checklist, artifact_checklist)
    return {
        "module": "RP-005",
        "manifest_version": PUBLICATION_MANIFEST_VERSION,
        "status": "generated",
        "publication_profile": active["publication_profile"],
        "manuscript": active,
        "submission_checklist": submission_checklist,
        "artifact_checklist": artifact_checklist,
        "publication_completeness_report": completeness_report,
        "source_manifests": active["source_manifests"],
        "integrity": {
            "references_fabricated": False,
            "reviewer_comments_fabricated": False,
            "acceptance_information_fabricated": False,
            "experimental_results_fabricated": False,
        },
    }


def _completeness_report(
    manuscript: dict[str, Any],
    validation: dict[str, Any],
    submission_checklist: dict[str, Any],
    artifact_checklist: dict[str, Any],
) -> dict[str, Any]:
    return {
        "module": "RP-005",
        "report_type": "publication_completeness",
        "status": "complete"
        if validation["status"] == "valid"
        and submission_checklist["status"] == "complete"
        and artifact_checklist["status"] == "complete"
        else "incomplete",
        "venue": manuscript["publication_profile"]["venue"],
        "section_count": validation["section_count"],
        "figure_count": validation["figure_count"],
        "table_count": validation["table_count"],
        "appendix_count": validation["appendix_count"],
        "references_placeholder_only": True,
        "ready_for_author_reference_completion": True,
    }
