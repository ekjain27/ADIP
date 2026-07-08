from __future__ import annotations

from typing import Any

from .comparison_matrix import NoveltyComparisonRecord, export_novelty_matrix_markdown

NOVELTY_MANIFEST_VERSION = "PAT-003.1"


def generate_novelty_manifest(
    records: tuple[NoveltyComparisonRecord, ...],
    innovation_coverage: dict[str, Any],
    reference_coverage: dict[str, Any],
    reference_registry: dict[str, Any],
    runtime_registry: dict[str, Any],
) -> dict[str, Any]:
    return {
        "module": "PAT-003",
        "manifest_version": NOVELTY_MANIFEST_VERSION,
        "status": "generated",
        "analysis_count": len(records),
        "analyses": tuple(record.snapshot() for record in sorted(records, key=lambda item: item.analysis_id)),
        "novelty_matrix_markdown": export_novelty_matrix_markdown(records),
        "innovation_coverage_report": innovation_coverage,
        "reference_coverage_report": reference_coverage,
        "reference_registry": reference_registry,
        "runtime_registry": runtime_registry,
        "legal_notice": "Structured comparison support only; no legal opinion or patentability conclusion is provided.",
    }
