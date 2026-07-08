from __future__ import annotations

from typing import Any

from .comparison_matrix import generate_comparison_matrix, generate_contribution_positioning_matrix
from .literature_classifier import classify_literature
from .research_gap_analyzer import generate_research_gap_matrix


def generate_related_work(registry: dict[str, Any], rp001_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    classification = classify_literature(tuple(registry["entries"]))
    outline = tuple(
        {
            "section_id": f"related_work_{index:02d}",
            "heading": item["theme"],
            "literature_ids": item["literature_ids"],
            "synthesis_instruction": "summarize only registered literature and cite supplied identifiers when present",
        }
        for index, item in enumerate(classification["taxonomy"]["themes"], start=1)
        if item["entry_count"]
    )
    return {
        "module": "RP-002",
        "status": "generated",
        "rp001_document_identifier": (rp001_metadata or {}).get("document_identifier"),
        "outline": outline,
        "taxonomy": classification["taxonomy"],
        "comparison_matrix": generate_comparison_matrix(registry),
        "research_gap_matrix": generate_research_gap_matrix(registry),
        "contribution_positioning_matrix": generate_contribution_positioning_matrix(registry),
        "integrity": {
            "citations_fabricated": False,
            "comparison_results_fabricated": False,
            "novelty_claims_fabricated": False,
        },
    }


def generate_literature_statistics(registry: dict[str, Any]) -> dict[str, Any]:
    classification = classify_literature(tuple(registry["entries"]))
    years = tuple(entry["publication_year"] for entry in registry["entries"])
    theme_counts = tuple(
        {"theme": item["theme"], "entry_count": item["entry_count"]}
        for item in classification["taxonomy"]["themes"]
    )
    return {
        "module": "RP-002",
        "status": "generated",
        "entry_count": registry["entry_count"],
        "unique_venue_count": len({entry["publication_venue"] for entry in registry["entries"]}),
        "unique_identifier_count": len({entry["identifier"] for entry in registry["entries"] if entry["identifier"]}),
        "publication_year_min": min(years),
        "publication_year_max": max(years),
        "theme_counts": theme_counts,
    }
