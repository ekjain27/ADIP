from __future__ import annotations

from typing import Any

from .literature_classifier import classify_literature

COMPARISON_DIMENSIONS = (
    "research_domain",
    "supported_themes",
    "evidence_summary",
    "provided_relevance_tags",
    "comparison_result",
)


def generate_comparison_matrix(registry: dict[str, Any]) -> dict[str, Any]:
    classification = classify_literature(tuple(registry["entries"]))
    classification_by_id = {item["literature_id"]: item for item in classification["classifications"]}
    rows = tuple(
        {
            "literature_id": entry["literature_id"],
            "title": entry["title"],
            "research_domain": entry["research_domain"],
            "supported_themes": classification_by_id[entry["literature_id"]]["themes"],
            "evidence_summary": entry["summary"],
            "provided_relevance_tags": entry["relevance_tags"],
            "comparison_result": "not_supplied",
            "fabricated_comparison": False,
        }
        for entry in registry["entries"]
    )
    return {
        "module": "RP-002",
        "matrix_type": "literature_comparison",
        "status": "generated",
        "dimensions": COMPARISON_DIMENSIONS,
        "rows": rows,
        "row_count": len(rows),
    }


def generate_contribution_positioning_matrix(registry: dict[str, Any]) -> dict[str, Any]:
    classification = classify_literature(tuple(registry["entries"]))
    rows = tuple(
        {
            "project_contribution": contribution,
            "related_theme": theme,
            "supporting_literature_ids": _literature_for_theme(classification, theme),
            "positioning_statement": "evidence_required_before_claiming_novelty",
            "novelty_claimed": False,
        }
        for contribution, theme in (
            ("deterministic decision intelligence platform structure", "Decision Intelligence"),
            ("knowledge graph backed decision context", "Knowledge Graphs"),
            ("governed provenance and validation traces", "Provenance"),
            ("platform integration and workflow contracts", "Workflow Orchestration"),
            ("operational validation and monitoring readiness", "Monitoring"),
        )
    )
    return {
        "module": "RP-002",
        "matrix_type": "contribution_positioning",
        "status": "generated",
        "rows": rows,
        "novelty_claims_fabricated": False,
    }


def _literature_for_theme(classification: dict[str, Any], theme: str) -> tuple[str, ...]:
    return tuple(
        item["literature_id"] for item in classification["classifications"] if theme in item["themes"]
    )
