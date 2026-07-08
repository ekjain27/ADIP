from __future__ import annotations

from typing import Any

from .claims_matrix import ClaimMapping, export_claims_matrix_markdown
from .claims_traceability import generate_traceability_report

CLAIMS_MANIFEST_VERSION = "PAT-002.1"


def generate_claims_manifest(mappings: tuple[ClaimMapping, ...], coverage_report: dict[str, Any]) -> dict[str, Any]:
    traceability = tuple(mapping.traceability() for mapping in mappings)
    return {
        "module": "PAT-002",
        "manifest_version": CLAIMS_MANIFEST_VERSION,
        "status": "generated",
        "claim_count": len(mappings),
        "claims": tuple(mapping.snapshot() for mapping in sorted(mappings, key=lambda item: item.claim_id)),
        "coverage_report": coverage_report,
        "traceability_report": generate_traceability_report(traceability),
        "claims_mapping_matrix_markdown": export_claims_matrix_markdown(mappings),
        "legal_notice": "Drafting support artifact only; not legal advice and not a patentability opinion.",
    }
