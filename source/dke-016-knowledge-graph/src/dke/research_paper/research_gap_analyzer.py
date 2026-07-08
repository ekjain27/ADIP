from __future__ import annotations

from typing import Any

from .literature_classifier import SUPPORTED_LITERATURE_THEMES, classify_literature


def generate_research_gap_matrix(registry: dict[str, Any]) -> dict[str, Any]:
    classification = classify_literature(tuple(registry["entries"]))
    taxonomy = classification["taxonomy"]["themes"]
    rows = tuple(
        {
            "theme": item["theme"],
            "supporting_literature_ids": item["literature_ids"],
            "evidence_status": "covered_by_registered_literature" if item["entry_count"] else "not_covered_by_registered_literature",
            "gap_statement": (
                "registered literature is available for synthesis"
                if item["entry_count"]
                else "no registered literature supplied for this theme"
            ),
            "novelty_claimed": False,
        }
        for item in taxonomy
    )
    return {
        "module": "RP-002",
        "matrix_type": "research_gap",
        "status": "generated",
        "themes": SUPPORTED_LITERATURE_THEMES,
        "rows": rows,
        "fabricated_gap_claims": False,
    }
