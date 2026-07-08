from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .paper_errors import DuplicateSectionError, NumberingConsistencyError

MANDATORY_SECTION_IDS = (
    "abstract",
    "introduction",
    "background",
    "architecture",
    "methodology",
    "validation",
    "discussion",
    "limitations",
    "conclusion",
    "appendices",
)


@dataclass(frozen=True)
class PaperSection:
    section_id: str
    title: str
    subsections: tuple[str, ...] = ()

    def snapshot(self) -> dict[str, Any]:
        return {"section_id": self.section_id, "title": self.title, "subsections": self.subsections}


def default_sections() -> tuple[PaperSection, ...]:
    return (
        PaperSection("abstract", "Abstract", ("abstract_template", "contribution_summary")),
        PaperSection("introduction", "Introduction", ("motivation", "scope", "contributions")),
        PaperSection("background", "Background", ("decision_intelligence", "platform_integration", "governance_and_provenance")),
        PaperSection("architecture", "Platform Architecture", ("runtime_registry", "integration_layer", "contract_adapters", "observability")),
        PaperSection("methodology", "Methodology", ("deterministic_generation", "validation_design", "artifact_traceability")),
        PaperSection("validation", "Validation And Benchmarking", ("regression_validation", "quality_benchmarking", "stress_testing")),
        PaperSection("discussion", "Discussion", ("enterprise_readiness", "research_implications")),
        PaperSection("limitations", "Limitations", ("no_fabricated_results", "citation_placeholders")),
        PaperSection("conclusion", "Conclusion", ("summary", "future_work")),
        PaperSection("appendices", "Appendices", ("metadata_appendix", "glossary", "artifact_manifest")),
    )


def generate_structure(sections: tuple[PaperSection, ...] | None = None) -> dict[str, Any]:
    active_sections = tuple(sections or default_sections())
    validate_sections(active_sections)
    return {
        "module": "RP-001",
        "structure_type": "research_paper_structure",
        "status": "generated",
        "section_count": len(active_sections),
        "sections": tuple(section.snapshot() for section in active_sections),
        "section_ids": tuple(section.section_id for section in active_sections),
    }


def validate_sections(sections: tuple[PaperSection, ...]) -> dict[str, Any]:
    seen: set[str] = set()
    for section in sections:
        if section.section_id in seen:
            raise DuplicateSectionError(f"duplicate section ID: {section.section_id}")
        seen.add(section.section_id)
    missing = tuple(section_id for section_id in MANDATORY_SECTION_IDS if section_id not in seen)
    if missing:
        raise DuplicateSectionError(f"mandatory section missing: {', '.join(missing)}")
    if tuple(section.section_id for section in sections) != MANDATORY_SECTION_IDS:
        raise DuplicateSectionError("section ordering is not deterministic")
    return {"module": "RP-001", "status": "valid", "section_count": len(sections)}


def generate_figure_registry(patent_figure_manifest: dict[str, Any]) -> dict[str, Any]:
    figures = tuple(
        {
            "figure_number": index,
            "figure_id": figure["figure_id"].replace("FIG-", "RP-FIG-"),
            "title": figure["title"],
            "source": "PAT-004",
        }
        for index, figure in enumerate(patent_figure_manifest["figures"], start=1)
    )
    _validate_numbering(figures, "figure_number")
    return {"module": "RP-001", "registry_type": "figure_registry", "status": "generated", "figure_count": len(figures), "figures": figures}


def generate_table_registry() -> dict[str, Any]:
    tables = (
        {"table_number": 1, "table_id": "RP-TABLE-001", "title": "Module Phase Inventory", "source": "DOC-002"},
        {"table_number": 2, "table_id": "RP-TABLE-002", "title": "Validation And Benchmarking Summary", "source": "VB"},
        {"table_number": 3, "table_id": "RP-TABLE-003", "title": "Patent Artifact Traceability", "source": "PAT"},
    )
    _validate_numbering(tables, "table_number")
    return {"module": "RP-001", "registry_type": "table_registry", "status": "generated", "table_count": len(tables), "tables": tables}


def generate_appendix_registry() -> dict[str, Any]:
    appendices = (
        {"appendix_id": "APP-A", "title": "Runtime Registry Metadata", "source": "PI-002"},
        {"appendix_id": "APP-B", "title": "Documentation Trace", "source": "DOC"},
        {"appendix_id": "APP-C", "title": "Patent Preparation Trace", "source": "PAT"},
        {"appendix_id": "APP-D", "title": "Citation Placeholder Registry", "source": "RP-001"},
    )
    return {"module": "RP-001", "registry_type": "appendix_registry", "status": "generated", "appendix_count": len(appendices), "appendices": appendices}


def generate_citation_placeholder_registry() -> dict[str, Any]:
    placeholders = (
        {"citation_id": "CIT-PLACEHOLDER-001", "purpose": "Decision intelligence background", "status": "placeholder_only"},
        {"citation_id": "CIT-PLACEHOLDER-002", "purpose": "Knowledge extraction background", "status": "placeholder_only"},
        {"citation_id": "CIT-PLACEHOLDER-003", "purpose": "Governance and provenance background", "status": "placeholder_only"},
        {"citation_id": "CIT-PLACEHOLDER-004", "purpose": "Validation and benchmarking methodology", "status": "placeholder_only"},
    )
    return {"module": "RP-001", "registry_type": "citation_placeholder_registry", "status": "generated", "citation_count": len(placeholders), "citations": placeholders}


def _validate_numbering(entries: tuple[dict[str, Any], ...], key: str) -> None:
    expected = tuple(range(1, len(entries) + 1))
    actual = tuple(entry[key] for entry in entries)
    if actual != expected:
        raise NumberingConsistencyError(f"inconsistent {key} numbering")
