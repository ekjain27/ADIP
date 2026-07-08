from __future__ import annotations

from typing import Any

from patent import create_patent_specification_generator

from .acronym_registry import AcronymEntry, generate_acronym_registry
from .glossary_manager import GlossaryTerm, generate_glossary
from .paper_errors import (
    DuplicateAcronymError,
    DuplicateSectionError,
    GlossaryConsistencyError,
    MalformedPaperMetadataError,
    NumberingConsistencyError,
)
from .paper_manifest import generate_manifest as build_paper_manifest
from .paper_metadata import PAPER_METADATA_VERSION, generate_metadata
from .paper_structure import (
    MANDATORY_SECTION_IDS,
    PaperSection,
    generate_appendix_registry,
    generate_citation_placeholder_registry,
    generate_figure_registry,
    generate_structure,
    generate_table_registry,
)


class ResearchPaperGenerator:
    MODULE = "RP-001"

    def __init__(self) -> None:
        self.patent_generator = create_patent_specification_generator()
        self.runtime_registry = self.patent_generator.runtime_registry
        self._patent_manifest: dict[str, Any] | None = None

    def generate_metadata(self, **overrides: Any) -> dict[str, Any]:
        return generate_metadata(**overrides)

    def generate_structure(self, sections: tuple[PaperSection, ...] | None = None) -> dict[str, Any]:
        return generate_structure(sections)

    def generate_glossary(self, terms: tuple[GlossaryTerm, ...] | None = None) -> dict[str, Any]:
        return generate_glossary(terms)

    def generate_acronym_registry(self, acronyms: tuple[AcronymEntry, ...] | None = None) -> dict[str, Any]:
        return generate_acronym_registry(acronyms)

    def generate_paper(self, **metadata_overrides: Any) -> dict[str, Any]:
        metadata = self.generate_metadata(**metadata_overrides)
        structure = self.generate_structure()
        patent_manifest = self._patent_manifest_cached()
        figure_registry = generate_figure_registry(patent_manifest["figure_manifest"])
        table_registry = generate_table_registry()
        appendix_registry = generate_appendix_registry()
        citation_registry = generate_citation_placeholder_registry()
        acronym_registry = self.generate_acronym_registry()
        glossary = self.generate_glossary()
        paper = {
            "module": self.MODULE,
            "status": "generated",
            "title": "Deterministic AI Decision Intelligence Platform: Architecture, Integration, Validation, And Artifact Traceability",
            "subtitle": "A metadata-synchronized publication foundation for Project-1",
            "metadata": metadata,
            "abstract_template": (
                "This paper template describes the implemented Project-1 platform architecture, "
                "integration mechanisms, validation framework, documentation pipeline, and patent-support traceability. "
                "Experimental results and citations are intentionally represented as placeholders until supplied by verified sources."
            ),
            "keyword_registry": (
                "AI decision intelligence",
                "deterministic platform integration",
                "runtime registry",
                "governance validation",
                "provenance traceability",
                "validation benchmarking",
            ),
            "acronym_registry": acronym_registry,
            "terminology_glossary": glossary,
            "section_hierarchy": structure,
            "subsection_hierarchy": tuple((section["section_id"], section["subsections"]) for section in structure["sections"]),
            "figure_registry": figure_registry,
            "table_registry": table_registry,
            "appendix_registry": appendix_registry,
            "citation_placeholder_registry": citation_registry,
        }
        self.validate_paper(paper)
        return paper

    def generate_manifest(self) -> dict[str, Any]:
        paper = self.generate_paper()
        return build_paper_manifest(
            paper,
            self._metadata_report(paper),
            self._completeness_report(paper),
            self.runtime_registry.export_registry_snapshot(),
            self._documentation_trace(),
            self._patent_trace(),
        )

    def export_markdown_paper(self, paper: dict[str, Any] | None = None) -> str:
        active_paper = paper or self.generate_paper()
        self.validate_paper(active_paper)
        metadata = active_paper["metadata"]
        lines = [
            f"# {active_paper['title']}",
            "",
            f"_{active_paper['subtitle']}_",
            "",
            "## Authors",
            "",
        ]
        for author in metadata["authors"]:
            lines.append(f"- {author['name']} ({author['affiliation_id']})")
        lines.extend(["", "## Abstract", "", active_paper["abstract_template"], "", "## Keywords", ""])
        for keyword in active_paper["keyword_registry"]:
            lines.append(f"- {keyword}")
        lines.append("")
        for section in active_paper["section_hierarchy"]["sections"]:
            lines.append(f"## {section['title']}")
            lines.append("")
            for subsection in section["subsections"]:
                lines.append(f"### {subsection.replace('_', ' ').title()}")
                lines.append("")
                lines.append("Content placeholder derived from platform metadata; verified results and citations are added separately.")
                lines.append("")
        return "\n".join(lines)

    def validate_paper(self, paper: dict[str, Any] | None = None) -> dict[str, Any]:
        active = paper or self.generate_paper()
        if active.get("module") != self.MODULE or not active.get("title"):
            raise MalformedPaperMetadataError("malformed paper metadata")
        section_ids = tuple(active["section_hierarchy"]["section_ids"])
        if section_ids != MANDATORY_SECTION_IDS:
            raise DuplicateSectionError("mandatory sections are missing or out of order")
        acronyms = tuple(entry["acronym"] for entry in active["acronym_registry"]["acronyms"])
        if len(acronyms) != len(set(acronyms)):
            raise DuplicateAcronymError("duplicate acronym in paper")
        glossary_terms = tuple(entry["term"] for entry in active["terminology_glossary"]["terms"])
        if len(glossary_terms) != len(set(glossary_terms)):
            raise GlossaryConsistencyError("duplicate glossary term in paper")
        self._validate_numbering(active["figure_registry"]["figures"], "figure_number")
        self._validate_numbering(active["table_registry"]["tables"], "table_number")
        return {
            "module": self.MODULE,
            "status": "valid",
            "section_count": len(section_ids),
            "figure_count": active["figure_registry"]["figure_count"],
            "table_count": active["table_registry"]["table_count"],
            "citation_placeholder_count": active["citation_placeholder_registry"]["citation_count"],
        }

    def _metadata_report(self, paper: dict[str, Any]) -> dict[str, Any]:
        metadata = paper["metadata"]
        return {
            "module": self.MODULE,
            "report_type": "metadata_report",
            "status": "generated",
            "metadata_version": PAPER_METADATA_VERSION,
            "document_identifier": metadata["document_identifier"],
            "publication_profile": metadata["publication_profile"],
            "target_venue_profile": metadata["target_venue_profile"],
            "author_count": len(metadata["authors"]),
        }

    def _completeness_report(self, paper: dict[str, Any]) -> dict[str, Any]:
        validation = self.validate_paper(paper)
        return {
            "module": self.MODULE,
            "report_type": "paper_completeness",
            "status": "complete",
            "section_count": validation["section_count"],
            "figure_count": validation["figure_count"],
            "table_count": validation["table_count"],
            "appendix_count": paper["appendix_registry"]["appendix_count"],
            "citation_placeholder_count": validation["citation_placeholder_count"],
            "no_fabricated_citations": True,
            "no_fabricated_results": True,
        }

    def _documentation_trace(self) -> dict[str, Any]:
        return self._patent_manifest_cached()["documentation_trace"]

    def _patent_trace(self) -> dict[str, Any]:
        manifest = self._patent_manifest_cached()
        return {
            "PAT-001": manifest["source_manifests"]["PAT-001"],
            "PAT-002": manifest["source_manifests"]["PAT-002"],
            "PAT-003": manifest["source_manifests"]["PAT-003"],
            "PAT-004": manifest["manifest_version"],
        }

    def _patent_manifest_cached(self) -> dict[str, Any]:
        if self._patent_manifest is None:
            self._patent_manifest = self.patent_generator.export_json_manifest()
        return self._patent_manifest

    def _validate_numbering(self, entries: tuple[dict[str, Any], ...], key: str) -> None:
        if tuple(entry[key] for entry in entries) != tuple(range(1, len(entries) + 1)):
            raise NumberingConsistencyError(f"inconsistent {key} numbering")


def create_research_paper_generator() -> ResearchPaperGenerator:
    return ResearchPaperGenerator()


def generate_paper() -> dict[str, Any]:
    return create_research_paper_generator().generate_paper()


def generate_metadata_report() -> dict[str, Any]:
    generator = create_research_paper_generator()
    return generator._metadata_report(generator.generate_paper())


def generate_structure_report() -> dict[str, Any]:
    return create_research_paper_generator().generate_structure()


def generate_glossary_report() -> dict[str, Any]:
    return create_research_paper_generator().generate_glossary()


def generate_acronym_registry_report() -> dict[str, Any]:
    return create_research_paper_generator().generate_acronym_registry()


def generate_manifest() -> dict[str, Any]:
    return create_research_paper_generator().generate_manifest()


def validate_paper() -> dict[str, Any]:
    return create_research_paper_generator().validate_paper()
