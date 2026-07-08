from __future__ import annotations

from typing import Any

from .literature_errors import InconsistentLiteratureClassificationError

SUPPORTED_LITERATURE_THEMES = (
    "Decision Intelligence",
    "Explainable AI",
    "Knowledge Graphs",
    "Multi-objective Optimization",
    "Decision Support Systems",
    "Enterprise AI",
    "Governance",
    "Provenance",
    "Workflow Orchestration",
    "Monitoring",
)

THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Decision Intelligence": ("decision intelligence", "decision-making", "decision making", "intelligence"),
    "Explainable AI": ("explainable", "explainability", "xai", "interpretable", "interpretability"),
    "Knowledge Graphs": ("knowledge graph", "graph", "ontology", "semantic", "rdf"),
    "Multi-objective Optimization": ("multi-objective", "multiobjective", "optimization", "pareto", "trade-off"),
    "Decision Support Systems": ("decision support", "dss", "recommendation", "support system"),
    "Enterprise AI": ("enterprise", "production ai", "platform", "operational", "deployment"),
    "Governance": ("governance", "policy", "compliance", "risk", "audit"),
    "Provenance": ("provenance", "lineage", "traceability", "source attribution", "evidence"),
    "Workflow Orchestration": ("workflow", "orchestration", "pipeline", "runtime", "coordination"),
    "Monitoring": ("monitoring", "observability", "telemetry", "drift", "alert"),
}


def classify_literature(entries: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    classifications = tuple(_classify_entry(entry) for entry in entries)
    taxonomy = generate_literature_taxonomy(classifications)
    return {
        "module": "RP-002",
        "classification_version": "RP-002.1",
        "status": "classified",
        "themes": SUPPORTED_LITERATURE_THEMES,
        "classifications": classifications,
        "taxonomy": taxonomy,
    }


def generate_literature_taxonomy(classifications: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    _validate_themes(classifications)
    buckets: dict[str, list[str]] = {theme: [] for theme in SUPPORTED_LITERATURE_THEMES}
    for classification in sorted(classifications, key=lambda item: item["literature_id"]):
        for theme in classification["themes"]:
            buckets[theme].append(classification["literature_id"])
    return {
        "taxonomy_version": "RP-002.1",
        "themes": tuple(
            {
                "theme": theme,
                "literature_ids": tuple(buckets[theme]),
                "entry_count": len(buckets[theme]),
            }
            for theme in SUPPORTED_LITERATURE_THEMES
        ),
    }


def _classify_entry(entry: dict[str, Any]) -> dict[str, Any]:
    evidence_text = " ".join(
        (
            entry["title"],
            entry["research_domain"],
            entry["summary"],
            " ".join(entry["keywords"]),
            " ".join(entry["relevance_tags"]),
        )
    ).lower()
    themes = tuple(
        theme for theme, keywords in THEME_KEYWORDS.items() if any(keyword in evidence_text for keyword in keywords)
    )
    if not themes:
        raise InconsistentLiteratureClassificationError(
            f"literature entry {entry['literature_id']} does not map to a supported theme"
        )
    return {
        "literature_id": entry["literature_id"],
        "title": entry["title"],
        "themes": themes,
        "classification_basis": "title, keywords, research_domain, summary, and relevance_tags",
        "fabricated_claims": False,
    }


def _validate_themes(classifications: tuple[dict[str, Any], ...]) -> None:
    supported = set(SUPPORTED_LITERATURE_THEMES)
    for classification in classifications:
        unknown = set(classification["themes"]) - supported
        if unknown:
            raise InconsistentLiteratureClassificationError(
                f"unsupported literature themes for {classification['literature_id']}: {sorted(unknown)}"
            )
