from __future__ import annotations

from typing import Any

from .evaluation_manifest import export_experiment_manifest
from .methodology_generator import generate_methodology
from .paper_generator import create_research_paper_generator
from .publication_errors import (
    DuplicatePublicationSectionError,
    FabricatedPublicationClaimError,
    InconsistentPublicationManifestError,
    MissingMandatoryPublicationSectionError,
    PublicationNumberingConsistencyError,
)
from .publication_package_profiles import generate_publication_profile, validate_publication_package_profile

MANUSCRIPT_VERSION = "RP-005.1"

MANDATORY_MANUSCRIPT_SECTION_IDS = (
    "title_page",
    "abstract",
    "keywords",
    "introduction",
    "related_work",
    "methodology",
    "experimental_evaluation",
    "discussion",
    "limitations",
    "conclusion",
    "figures_list",
    "tables_list",
    "references_placeholder",
    "appendices",
    "acknowledgements_placeholder",
    "funding_placeholder",
    "conflict_of_interest_placeholder",
    "data_availability_statement",
    "reproducibility_statement",
)


def assemble_manuscript(venue: str = "arXiv") -> dict[str, Any]:
    profile = generate_publication_profile(venue)
    paper_generator = create_research_paper_generator()
    paper = paper_generator.generate_paper(target_venue_profile=_rp001_compatible_venue(profile["venue"]))
    paper_manifest = paper_generator.generate_manifest()
    methodology = generate_methodology()
    evaluation_manifest = export_experiment_manifest()
    manuscript = {
        "module": "RP-005",
        "manuscript_version": MANUSCRIPT_VERSION,
        "status": "assembled",
        "publication_profile": profile,
        "sections": _sections(paper, methodology, evaluation_manifest),
        "figures_list": paper["figure_registry"],
        "tables_list": paper["table_registry"],
        "appendices": _appendices(paper, methodology, evaluation_manifest),
        "source_manifests": _source_manifests(paper_manifest, methodology, evaluation_manifest),
        "markdown": "",
        "integrity": {
            "references_fabricated": False,
            "reviewer_comments_fabricated": False,
            "acceptance_information_fabricated": False,
            "experimental_results_fabricated": False,
        },
    }
    manuscript["markdown"] = export_markdown_manuscript(manuscript)
    validate_manuscript(manuscript)
    return manuscript


def export_markdown_manuscript(manuscript: dict[str, Any] | None = None, venue: str = "arXiv") -> str:
    active = manuscript or assemble_manuscript(venue)
    if active.get("sections"):
        validate_manuscript(active, require_markdown=False)
    lines = [
        f"# {active['sections'][0]['content']['title']}",
        "",
        f"Publication profile: {active['publication_profile']['venue']}",
        "",
    ]
    for section in active["sections"][1:]:
        lines.append(f"## {section['title']}")
        lines.append("")
        content = section["content"]
        if isinstance(content, dict):
            for key in sorted(content):
                value = content[key]
                if isinstance(value, (tuple, list)):
                    lines.append(f"- {key}: {', '.join(str(item) for item in value)}")
                else:
                    lines.append(f"- {key}: {value}")
        elif isinstance(content, (tuple, list)):
            lines.extend(f"- {item}" for item in content)
        else:
            lines.append(str(content))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def validate_manuscript(manuscript: dict[str, Any], require_markdown: bool = True) -> dict[str, Any]:
    validate_publication_package_profile(manuscript["publication_profile"])
    section_ids = tuple(section.get("section_id") for section in manuscript.get("sections", ()))
    if len(section_ids) != len(set(section_ids)):
        raise DuplicatePublicationSectionError("duplicate publication section IDs are not allowed")
    if section_ids != MANDATORY_MANUSCRIPT_SECTION_IDS:
        missing = tuple(section_id for section_id in MANDATORY_MANUSCRIPT_SECTION_IDS if section_id not in section_ids)
        if missing:
            raise MissingMandatoryPublicationSectionError(f"missing mandatory manuscript section(s): {missing}")
        raise MissingMandatoryPublicationSectionError("mandatory manuscript section ordering is not deterministic")
    _validate_numbering(manuscript["figures_list"]["figures"], "figure_number")
    _validate_numbering(manuscript["tables_list"]["tables"], "table_number")
    appendix_ids = tuple(appendix["appendix_id"] for appendix in manuscript["appendices"]["appendices"])
    if len(appendix_ids) != len(set(appendix_ids)):
        raise PublicationNumberingConsistencyError("duplicate appendix IDs are not allowed")
    expected_sources = {"RP-001", "RP-002", "RP-003", "RP-004", "DOC", "PAT"}
    actual_sources = {appendix["source"] for appendix in manuscript["appendices"]["appendices"]}
    if not expected_sources.issubset(actual_sources):
        raise InconsistentPublicationManifestError("appendix sources do not cover RP, DOC, and PAT traces")
    integrity = manuscript.get("integrity", {})
    if any(integrity.get(key) is not False for key in integrity):
        raise FabricatedPublicationClaimError("publication package cannot fabricate references, reviews, acceptance, or results")
    if require_markdown and not manuscript.get("markdown", "").startswith("# "):
        raise InconsistentPublicationManifestError("markdown manuscript is missing")
    return {
        "module": "RP-005",
        "status": "valid",
        "section_count": len(section_ids),
        "figure_count": manuscript["figures_list"]["figure_count"],
        "table_count": manuscript["tables_list"]["table_count"],
        "appendix_count": manuscript["appendices"]["appendix_count"],
    }


def _sections(paper: dict[str, Any], methodology: dict[str, Any], evaluation_manifest: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    citation_placeholders = tuple(citation["citation_id"] for citation in paper["citation_placeholder_registry"]["citations"])
    sections: dict[str, Any] = {
        "title_page": {
            "title": paper["title"],
            "subtitle": paper["subtitle"],
            "authors": tuple(author["name"] for author in paper["metadata"]["authors"]),
            "document_identifier": paper["metadata"]["document_identifier"],
        },
        "abstract": paper["abstract_template"],
        "keywords": paper["keyword_registry"],
        "introduction": "Introduction content is assembled from RP-001 structure and must be completed by the authors.",
        "related_work": {
            "status": "references_placeholder_only",
            "source": "RP-002",
            "citation_placeholders": citation_placeholders,
            "fabricated_citations": False,
        },
        "methodology": {
            "source": "RP-003",
            "section_count": methodology["architecture_summary"]["component_count"],
            "markdown_available": methodology["markdown"].startswith("# Methodology"),
        },
        "experimental_evaluation": {
            "source": "RP-004",
            "experiment_count": evaluation_manifest["evaluation_summary"]["experiment_count"],
            "benchmark_modules": evaluation_manifest["evaluation_summary"]["benchmark_modules"],
            "fabricated_results": False,
        },
        "discussion": "Discussion placeholder for author-supplied synthesis grounded in RP-001 through RP-004 artifacts.",
        "limitations": (
            "References remain placeholders until supplied by verified sources.",
            "Reviewer responses, acceptance claims, and unsupported experimental results are not generated.",
        ),
        "conclusion": "Conclusion placeholder for author completion after verified references and final venue formatting.",
        "figures_list": tuple(
            f"Figure {figure['figure_number']}: {figure['title']} ({figure['source']})"
            for figure in paper["figure_registry"]["figures"]
        ),
        "tables_list": tuple(
            f"Table {table['table_number']}: {table['title']} ({table['source']})"
            for table in paper["table_registry"]["tables"]
        ),
        "references_placeholder": {
            "status": "placeholder_only",
            "required_action": "replace placeholders with verified, user-supplied references",
            "citation_placeholders": citation_placeholders,
            "fabricated_references": False,
        },
        "appendices": tuple(
            f"{appendix['appendix_id']}: {appendix['title']} ({appendix['source']})"
            for appendix in _appendices(paper, methodology, evaluation_manifest)["appendices"]
        ),
        "acknowledgements_placeholder": "Acknowledgements are not generated and must be supplied by the authors if applicable.",
        "funding_placeholder": "Funding information is not generated and must be supplied by the authors if applicable.",
        "conflict_of_interest_placeholder": "Conflict-of-interest information is not generated and must be supplied by the authors.",
        "data_availability_statement": "Data availability statement template: repository-local validation artifacts are available in the project workspace; external datasets are not introduced by RP-005.",
        "reproducibility_statement": "Reproducibility statement: run `python -m pytest` and `npm run test`; RP-004 provides benchmark traceability and artifact inventory.",
    }
    return tuple(
        {
            "section_id": section_id,
            "title": section_id.replace("_", " ").title(),
            "content": sections[section_id],
            "fabricated_content": False,
        }
        for section_id in MANDATORY_MANUSCRIPT_SECTION_IDS
    )


def _appendices(paper: dict[str, Any], methodology: dict[str, Any], evaluation_manifest: dict[str, Any]) -> dict[str, Any]:
    base = tuple({**appendix, "source": appendix["source"]} for appendix in paper["appendix_registry"]["appendices"])
    additional = (
        {"appendix_id": "APP-E", "title": "Related Work Placeholder Trace", "source": "RP-002"},
        {"appendix_id": "APP-F", "title": "Methodology And Architecture Manifest", "source": methodology["module"]},
        {"appendix_id": "APP-G", "title": "Experimental Evaluation Manifest", "source": evaluation_manifest["module"]},
        {"appendix_id": "APP-H", "title": "Documentation Package Trace", "source": "DOC"},
        {"appendix_id": "APP-I", "title": "Patent Support Trace", "source": "PAT"},
    )
    appendices = tuple(sorted((*base, *additional), key=lambda item: item["appendix_id"]))
    return {
        "module": "RP-005",
        "registry_type": "publication_appendix_registry",
        "status": "generated",
        "appendix_count": len(appendices),
        "appendices": appendices,
    }


def _source_manifests(paper_manifest: dict[str, Any], methodology: dict[str, Any], evaluation_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "RP-001": paper_manifest["manifest_version"],
        "RP-002": "RP-002",
        "RP-003": methodology["methodology_version"],
        "RP-004": evaluation_manifest["manifest_version"],
        "documentation_trace": paper_manifest["documentation_trace"],
        "patent_trace": paper_manifest["patent_trace"],
        "runtime_registry": paper_manifest["runtime_registry"],
    }


def _validate_numbering(entries: tuple[dict[str, Any], ...], key: str) -> None:
    if tuple(entry[key] for entry in entries) != tuple(range(1, len(entries) + 1)):
        raise PublicationNumberingConsistencyError(f"inconsistent {key} numbering")


def _rp001_compatible_venue(venue: str) -> str:
    return "IEEE" if venue == "ACM" else venue
