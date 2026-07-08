from __future__ import annotations

from typing import Any

from .claims_mapper import ClaimsMappingFramework
from .figure_generator import default_patent_figures
from .figure_manifest import PatentFigure, generate_figure_manifest as build_figure_manifest
from .invention_registry import InnovationRecord
from .novelty_analyzer import NoveltyAnalysisFramework
from .patent_manifest import PatentPreparationFramework, create_patent_preparation_framework
from .specification_errors import (
    IncompleteSpecificationTraceabilityError,
    MalformedSpecificationSectionError,
)
from .specification_manifest import generate_specification_manifest as build_specification_manifest

REQUIRED_SPECIFICATION_SECTIONS = (
    "patent_title",
    "technical_field",
    "background",
    "problem_statement",
    "summary_of_invention",
    "brief_description_of_drawings",
    "detailed_description",
    "embodiment_summaries",
    "implementation_traceability_appendix",
    "figure_index",
    "acronym_glossary",
)

SECTION_TITLES = {
    "patent_title": "Patent Title",
    "technical_field": "Technical Field",
    "background": "Background",
    "problem_statement": "Problem Statement",
    "summary_of_invention": "Summary Of The Invention",
    "brief_description_of_drawings": "Brief Description Of Drawings",
    "detailed_description": "Detailed Description",
    "embodiment_summaries": "Embodiment Summaries",
    "implementation_traceability_appendix": "Implementation Traceability Appendix",
    "figure_index": "Figure Index",
    "acronym_glossary": "Acronym Glossary",
}


class PatentSpecificationGenerator:
    MODULE = "PAT-004"

    def __init__(self, patent_framework: PatentPreparationFramework | None = None) -> None:
        self.patent_framework = patent_framework or create_patent_preparation_framework()
        self.claims_framework = ClaimsMappingFramework(self.patent_framework)
        self.novelty_framework = NoveltyAnalysisFramework(self.patent_framework, self.claims_framework)
        self.runtime_registry = self.patent_framework.runtime_registry
        self._patent_manifest: dict[str, Any] | None = None
        self._claims_manifest: dict[str, Any] | None = None
        self._novelty_manifest: dict[str, Any] | None = None

    def generate_patent_specification(self) -> dict[str, Any]:
        innovations = self.patent_framework.discover_innovations()
        figures = default_patent_figures()
        sections = self._specification_sections(innovations, figures)
        specification = {
            "module": self.MODULE,
            "status": "generated",
            "section_count": len(sections),
            "sections": sections,
            "innovation_ids": tuple(innovation.innovation_id for innovation in innovations),
            "claim_count": self._claims_manifest_cached()["claim_count"],
            "figure_count": len(figures),
            "legal_notice": "Drafting support only; this artifact is not legal advice and does not assert patentability.",
        }
        self.validate_specification(specification)
        return specification

    def generate_figure_manifest(self, figures: tuple[PatentFigure, ...] | None = None) -> dict[str, Any]:
        return build_figure_manifest(figures or default_patent_figures())

    def generate_specification_manifest(self) -> dict[str, Any]:
        specification = self.generate_patent_specification()
        figure_manifest = self.generate_figure_manifest()
        completeness = self._completeness_report(specification, figure_manifest)
        return build_specification_manifest(
            specification,
            figure_manifest,
            self._patent_manifest_cached(),
            self._claims_manifest_cached(),
            self._novelty_manifest_cached(),
            self.patent_framework._documentation_trace(),
            self.runtime_registry.export_registry_snapshot(),
            completeness,
        )

    def export_markdown_specification(self, specification: dict[str, Any] | None = None) -> str:
        active_specification = specification or self.generate_patent_specification()
        self.validate_specification(active_specification)
        lines = ["# Patent Specification Draft", ""]
        for section in active_specification["sections"]:
            lines.append(f"## {section['title']}")
            lines.append("")
            if isinstance(section["content"], tuple):
                for item in section["content"]:
                    lines.append(f"- {item}")
            else:
                lines.append(section["content"])
            lines.append("")
        lines.append("> Drafting support artifact only; professional legal review is required before filing.")
        return "\n".join(lines) + "\n"

    def export_json_manifest(self) -> dict[str, Any]:
        return self.generate_specification_manifest()

    def validate_specification(self, specification: dict[str, Any] | None = None) -> dict[str, Any]:
        active = specification or self.generate_patent_specification()
        if active.get("module") != self.MODULE:
            raise MalformedSpecificationSectionError("malformed specification module")
        sections = active.get("sections")
        if not isinstance(sections, tuple):
            raise MalformedSpecificationSectionError("specification sections must be deterministic tuple")
        section_by_id = {section.get("section_id"): section for section in sections if isinstance(section, dict)}
        for section_id in REQUIRED_SPECIFICATION_SECTIONS:
            section = section_by_id.get(section_id)
            if not section or not section.get("title") or not section.get("content"):
                raise MalformedSpecificationSectionError(f"malformed specification section: {section_id}")
        if tuple(section["section_id"] for section in sections) != REQUIRED_SPECIFICATION_SECTIONS:
            raise MalformedSpecificationSectionError("specification section ordering is not deterministic")
        innovation_ids = {innovation.innovation_id for innovation in self.patent_framework.discover_innovations()}
        referenced = set(active.get("innovation_ids", ()))
        appendix_content = section_by_id["implementation_traceability_appendix"]["content"]
        appendix_text = " ".join(appendix_content) if isinstance(appendix_content, tuple) else str(appendix_content)
        missing = tuple(sorted(innovation_id for innovation_id in innovation_ids if innovation_id not in referenced or innovation_id not in appendix_text))
        if missing:
            raise IncompleteSpecificationTraceabilityError(f"incomplete innovation traceability: {', '.join(missing)}")
        figure_manifest = self.generate_figure_manifest()
        if figure_manifest["figure_count"] != active.get("figure_count"):
            raise IncompleteSpecificationTraceabilityError("figure index does not match figure manifest")
        return {
            "module": self.MODULE,
            "status": "valid",
            "section_count": len(sections),
            "innovation_count": len(innovation_ids),
            "figure_count": figure_manifest["figure_count"],
        }

    def _specification_sections(
        self,
        innovations: tuple[InnovationRecord, ...],
        figures: tuple[PatentFigure, ...],
    ) -> tuple[dict[str, Any], ...]:
        innovation_titles = tuple(f"{innovation.innovation_id}: {innovation.title}" for innovation in innovations)
        claim_manifest = self._claims_manifest_cached()
        novelty_manifest = self._novelty_manifest_cached()
        figure_lines = tuple(f"{figure.figure_id}: {figure.title} - {figure.description}" for figure in sorted(figures, key=lambda item: item.figure_id))
        traceability = tuple(
            f"{innovation.innovation_id} -> modules {', '.join(innovation.related_modules)} -> claims "
            f"{', '.join(claim['claim_id'] for claim in claim_manifest['claims'] if claim['innovation_id'] == innovation.innovation_id)} -> "
            f"novelty analyses {sum(1 for analysis in novelty_manifest['analyses'] if analysis['innovation_id'] == innovation.innovation_id)}"
            for innovation in innovations
        )
        section_content: dict[str, Any] = {
            "patent_title": "Deterministic AI Decision Intelligence Platform With Integrated Governance, Provenance, Runtime Registry, Validation, And Documentation Infrastructure",
            "technical_field": "The disclosure relates to deterministic enterprise decision intelligence platforms, cross-engine integration, governance validation, provenance tracking, observability, validation benchmarking, documentation generation, and patent-support metadata generation.",
            "background": "Enterprise decision systems often expose fragmented engines, inconsistent contracts, disconnected governance evidence, and manually maintained documentation. The implemented platform consolidates these concerns behind deterministic integration, registry, validation, and artifact-generation layers.",
            "problem_statement": "A need exists for a stable platform architecture that can connect heterogeneous decision intelligence components while preserving deterministic behavior, traceable governance, reproducible validation, and automatically synchronized supporting artifacts.",
            "summary_of_invention": innovation_titles,
            "brief_description_of_drawings": figure_lines,
            "detailed_description": tuple(
                f"{innovation.title}: {innovation.architectural_contribution} {innovation.novelty_summary}"
                for innovation in innovations
            ),
            "embodiment_summaries": tuple(
                "A deterministic embodiment includes " + innovation.description for innovation in innovations
            ),
            "implementation_traceability_appendix": traceability,
            "figure_index": tuple(figure.figure_id for figure in sorted(figures, key=lambda item: item.figure_id)),
            "acronym_glossary": (
                "ADBM: Adaptive Decision Behavior Model",
                "ADWG: Adaptive Decision Workflow Graph",
                "DDGM: Dynamic Decision Governance Mesh",
                "DHMF: Decision Health Monitoring Framework",
                "DIE: Decision Intelligence Engine",
                "DKE: Domain Knowledge Extraction",
                "DPG: Decision Provenance Graph",
                "DRIF: Decision Recommendation Interface Framework",
                "EDOF: Enterprise Decision Orchestration Framework",
                "PI: Platform Integration",
                "TDLL: Temporal Decision Lineage Ledger",
                "VB: Validation And Benchmarking",
            ),
        }
        return tuple(
            {"section_id": section_id, "title": SECTION_TITLES[section_id], "content": section_content[section_id]}
            for section_id in REQUIRED_SPECIFICATION_SECTIONS
        )

    def _completeness_report(self, specification: dict[str, Any], figure_manifest: dict[str, Any]) -> dict[str, Any]:
        validation = self.validate_specification(specification)
        return {
            "module": self.MODULE,
            "report_type": "specification_completeness",
            "status": "complete",
            "section_count": validation["section_count"],
            "innovation_count": validation["innovation_count"],
            "claim_count": specification["claim_count"],
            "figure_count": figure_manifest["figure_count"],
            "traceability_complete": True,
        }

    def _patent_manifest_cached(self) -> dict[str, Any]:
        if self._patent_manifest is None:
            self._patent_manifest = self.patent_framework.export_patent_manifest()
        return self._patent_manifest

    def _claims_manifest_cached(self) -> dict[str, Any]:
        if self._claims_manifest is None:
            self._claims_manifest = self.claims_framework.generate_claims_manifest()
        return self._claims_manifest

    def _novelty_manifest_cached(self) -> dict[str, Any]:
        if self._novelty_manifest is None:
            self._novelty_manifest = self.novelty_framework.export_novelty_manifest()
        return self._novelty_manifest


def create_patent_specification_generator() -> PatentSpecificationGenerator:
    return PatentSpecificationGenerator()


def generate_patent_specification() -> dict[str, Any]:
    return create_patent_specification_generator().generate_patent_specification()


def generate_figure_manifest() -> dict[str, Any]:
    return create_patent_specification_generator().generate_figure_manifest()


def generate_specification_manifest() -> dict[str, Any]:
    return create_patent_specification_generator().generate_specification_manifest()


def export_markdown_specification() -> str:
    return create_patent_specification_generator().export_markdown_specification()


def export_json_manifest() -> dict[str, Any]:
    return create_patent_specification_generator().export_json_manifest()


def validate_specification() -> dict[str, Any]:
    return create_patent_specification_generator().validate_specification()
