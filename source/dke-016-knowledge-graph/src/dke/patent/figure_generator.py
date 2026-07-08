from __future__ import annotations

from .figure_manifest import PatentFigure, generate_figure_manifest


def default_patent_figures() -> tuple[PatentFigure, ...]:
    return (
        PatentFigure(
            "FIG-001",
            "Overall Platform Architecture",
            "Metadata for an integrated architecture spanning research, DKE, DIE, platform integration, validation, documentation, and patent preparation.",
            ("R", "DKE", "DIE", "PI", "VB", "DOC", "PAT"),
        ),
        PatentFigure(
            "FIG-002",
            "Decision Pipeline",
            "Metadata for deterministic flow from research evidence through knowledge extraction and decision intelligence execution.",
            ("R", "DKE", "DIE"),
        ),
        PatentFigure(
            "FIG-003",
            "Runtime Registry",
            "Metadata for module registration, lifecycle state, capability metadata, dependency relationships, and compatibility checks.",
            ("PI-002",),
        ),
        PatentFigure(
            "FIG-004",
            "Platform Integration",
            "Metadata for the platform boundary connecting extraction, decision, provenance, governance, monitoring, recommendation, and orchestration components.",
            ("PI-001", "PI-003", "PI-004", "PI-005", "PI-006", "PI-007", "PI-008"),
        ),
        PatentFigure(
            "FIG-005",
            "Validation Pipeline",
            "Metadata for regression, decision quality, performance, governance, provenance, stress, and failure validation.",
            ("VB-001", "VB-002", "VB-003", "VB-004", "VB-005"),
        ),
        PatentFigure(
            "FIG-006",
            "Provenance And Governance",
            "Metadata for decision provenance, governance mesh compliance, temporal lineage, audit completeness, and trace coverage.",
            ("DPG", "DDGM", "TDLL"),
        ),
        PatentFigure(
            "FIG-007",
            "Workflow Orchestration",
            "Metadata for adaptive behavior, deterministic workflow orchestration, enterprise orchestration, and routing between platform engines.",
            ("ADBM", "ADWG", "EDOF", "PI-003", "PI-004"),
        ),
        PatentFigure(
            "FIG-008",
            "Monitoring Architecture",
            "Metadata for deterministic observability, monitoring integration, health reporting, metrics, tracing, and audit forwarding.",
            ("DHMF", "PI-007"),
        ),
    )


def generate_default_figure_manifest() -> dict:
    return generate_figure_manifest(default_patent_figures())
