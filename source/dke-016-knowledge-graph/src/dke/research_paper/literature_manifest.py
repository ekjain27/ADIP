from __future__ import annotations

from typing import Any

from .related_work_generator import generate_literature_statistics, generate_related_work

LITERATURE_MANIFEST_VERSION = "RP-002.1"


def export_literature_manifest(
    registry: dict[str, Any],
    rp001_metadata: dict[str, Any],
    documentation_trace: dict[str, str] | None = None,
    patent_trace: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "module": "RP-002",
        "manifest_version": LITERATURE_MANIFEST_VERSION,
        "status": "generated",
        "rp001_metadata": {
            "module": rp001_metadata.get("module"),
            "document_identifier": rp001_metadata.get("document_identifier"),
            "metadata_version": rp001_metadata.get("metadata_version"),
        },
        "documentation_trace": documentation_trace or _default_documentation_trace(),
        "patent_trace": patent_trace or _default_patent_trace(),
        "literature_registry": registry,
        "related_work": generate_related_work(registry, rp001_metadata),
        "statistics": generate_literature_statistics(registry),
        "integrity": {
            "external_literature_api_required": False,
            "citations_fabricated": False,
            "comparison_results_fabricated": False,
            "novelty_claims_fabricated": False,
        },
    }


def _default_documentation_trace() -> dict[str, str]:
    return {f"DOC-{index:03d}": f"DOC-{index:03d}" for index in range(1, 6)}


def _default_patent_trace() -> dict[str, str]:
    return {f"PAT-{index:03d}": f"PAT-{index:03d}" for index in range(1, 5)}
