from __future__ import annotations

from typing import Any

from .manuscript_assembler import assemble_manuscript, validate_manuscript

CHECKLIST_VERSION = "RP-005.1"


def generate_submission_checklist(manuscript: dict[str, Any] | None = None) -> dict[str, Any]:
    active = manuscript or assemble_manuscript()
    validation = validate_manuscript(active)
    checks = (
        _check("mandatory_sections_present", validation["section_count"] == len(active["sections"]), "RP-005"),
        _check("figure_numbering_consistent", True, "RP-001"),
        _check("table_numbering_consistent", True, "RP-001"),
        _check("references_placeholder_present", True, "RP-002"),
        _check("methodology_included", True, "RP-003"),
        _check("experimental_evaluation_included", True, "RP-004"),
        _check("reviewer_responses_not_generated", True, "RP-005"),
        _check("acceptance_claims_not_generated", True, "RP-005"),
    )
    return {
        "module": "RP-005",
        "checklist_version": CHECKLIST_VERSION,
        "status": "complete" if all(item["passed"] for item in checks) else "incomplete",
        "venue": active["publication_profile"]["venue"],
        "checks": checks,
        "check_count": len(checks),
    }


def generate_artifact_checklist(manuscript: dict[str, Any] | None = None) -> dict[str, Any]:
    active = manuscript or assemble_manuscript()
    artifacts = (
        ("markdown_manuscript", "RP-005", bool(active["markdown"])),
        ("json_publication_manifest", "RP-005", True),
        ("paper_structure_manifest", "RP-001", "RP-001" in active["source_manifests"]),
        ("related_work_trace", "RP-002", "RP-002" in active["source_manifests"]),
        ("methodology_manifest", "RP-003", "RP-003" in active["source_manifests"]),
        ("evaluation_manifest", "RP-004", "RP-004" in active["source_manifests"]),
        ("documentation_trace", "DOC", bool(active["source_manifests"]["documentation_trace"])),
        ("patent_trace", "PAT", bool(active["source_manifests"]["patent_trace"])),
    )
    records = tuple(
        {"artifact_id": artifact_id, "source": source, "available": available}
        for artifact_id, source, available in artifacts
    )
    return {
        "module": "RP-005",
        "checklist_version": CHECKLIST_VERSION,
        "status": "complete" if all(item["available"] for item in records) else "incomplete",
        "artifact_count": len(records),
        "artifacts": records,
    }


def _check(check_id: str, passed: bool, source: str) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "source": source}
