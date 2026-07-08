import pytest

from research_paper.literature_classifier import classify_literature
from research_paper.literature_errors import (
    DuplicateLiteratureEntryError,
    InconsistentLiteratureClassificationError,
    MalformedLiteratureRecordError,
)
from research_paper.literature_manifest import LITERATURE_MANIFEST_VERSION, export_literature_manifest
from research_paper.literature_registry import LiteratureEntry, register_literature, validate_literature_registry
from research_paper.paper_metadata import generate_metadata
from research_paper.related_work_generator import generate_literature_statistics, generate_related_work


def sample_entries():
    return (
        LiteratureEntry(
            title="Decision Intelligence Systems for Enterprise Decision Support",
            authors=("Ada Researcher", "Grace Analyst"),
            publication_venue="Journal of Decision Systems",
            publication_year=2021,
            identifier="10.1000/dis-enterprise",
            keywords=("decision intelligence", "decision support", "enterprise ai"),
            research_domain="Decision Intelligence",
            summary="Analyzes enterprise decision support systems and operational platform concerns.",
            relevance_tags=("Decision Intelligence", "Enterprise AI", "Decision Support Systems"),
        ),
        LiteratureEntry(
            title="Knowledge Graph Provenance for Explainable AI Governance",
            authors=("Lin Graph",),
            publication_venue="Knowledge Engineering Review",
            publication_year=2022,
            identifier="KG-PROV-2022",
            keywords=("knowledge graph", "provenance", "explainable AI", "governance"),
            research_domain="Knowledge Graphs",
            summary="Discusses graph lineage, traceability, and governance for explainable AI workflows.",
            relevance_tags=("Knowledge Graphs", "Provenance", "Governance", "Explainable AI"),
        ),
        LiteratureEntry(
            title="Monitoring Multi-objective Workflow Orchestration",
            authors=("Mo Opt",),
            publication_venue="Enterprise AI Systems",
            publication_year=2023,
            identifier=None,
            keywords=("multi-objective optimization", "workflow orchestration", "monitoring"),
            research_domain="Workflow Orchestration",
            summary="Frames telemetry and trade-off monitoring for orchestrated optimization pipelines.",
            relevance_tags=("Multi-objective Optimization", "Workflow Orchestration", "Monitoring"),
        ),
    )


def test_literature_registration_and_deterministic_ordering():
    registry = register_literature(tuple(reversed(sample_entries())))
    assert registry["module"] == "RP-002"
    assert registry["entry_count"] == 3
    assert registry["literature_ids"] == (
        "10.1000/dis-enterprise",
        "KG-PROV-2022",
        "opt-2023-monitoringmultiobjective",
    )
    assert registry == register_literature(tuple(reversed(sample_entries())))


def test_malformed_literature_record_rejection():
    malformed = LiteratureEntry(
        title="",
        authors=("Ada Researcher",),
        publication_venue="Journal",
        publication_year=2021,
        identifier=None,
        keywords=("decision intelligence",),
        research_domain="Decision Intelligence",
        summary="summary",
        relevance_tags=("Decision Intelligence",),
    )
    with pytest.raises(MalformedLiteratureRecordError, match="title is required"):
        register_literature((malformed,))


def test_duplicate_identifier_detection():
    first, second, *_ = sample_entries()
    duplicate = LiteratureEntry(
        title="Different Title",
        authors=("Different Author",),
        publication_venue="Different Venue",
        publication_year=2024,
        identifier=first.identifier,
        keywords=("governance",),
        research_domain="Governance",
        summary="Different supplied summary.",
        relevance_tags=("Governance",),
    )
    with pytest.raises(DuplicateLiteratureEntryError, match="duplicate literature IDs"):
        register_literature((first, second, duplicate))


def test_duplicate_citation_metadata_detection_without_identifier():
    original = sample_entries()[2]
    duplicate = LiteratureEntry(
        title=original.title,
        authors=original.authors,
        publication_venue="Another Venue",
        publication_year=original.publication_year,
        identifier="ALT-2023",
        keywords=original.keywords,
        research_domain=original.research_domain,
        summary=original.summary,
        relevance_tags=original.relevance_tags,
    )
    with pytest.raises(DuplicateLiteratureEntryError, match="duplicate literature citation metadata"):
        register_literature((original, duplicate))


def test_deterministic_classification_and_taxonomy_consistency():
    registry = register_literature(sample_entries())
    classification = classify_literature(registry["entries"])
    assert classification == classify_literature(registry["entries"])
    taxonomy = classification["taxonomy"]["themes"]
    assert taxonomy[0]["theme"] == "Decision Intelligence"
    assert "10.1000/dis-enterprise" in taxonomy[0]["literature_ids"]
    assert taxonomy[-1]["theme"] == "Monitoring"


def test_inconsistent_classification_rejection():
    entry = LiteratureEntry(
        title="A Paper Without Matching Theme",
        authors=("Neutral Author",),
        publication_venue="General Venue",
        publication_year=2020,
        identifier="NEUTRAL-2020",
        keywords=("unmapped",),
        research_domain="Unmapped",
        summary="No supported classification vocabulary is present.",
        relevance_tags=("unmapped",),
    )
    registry = register_literature((entry,))
    with pytest.raises(InconsistentLiteratureClassificationError, match="does not map"):
        classify_literature(registry["entries"])


def test_related_work_outputs_matrices_without_fabricated_claims():
    registry = register_literature(sample_entries())
    related_work = generate_related_work(registry, generate_metadata())
    assert related_work["rp001_document_identifier"] == "AIDIP-PROJECT1-RP-001"
    assert related_work["integrity"]["citations_fabricated"] is False
    assert related_work["comparison_matrix"]["rows"][0]["comparison_result"] == "not_supplied"
    assert related_work["research_gap_matrix"]["fabricated_gap_claims"] is False
    assert related_work["contribution_positioning_matrix"]["novelty_claims_fabricated"] is False
    assert all(row["novelty_claimed"] is False for row in related_work["contribution_positioning_matrix"]["rows"])


def test_literature_statistics_generation():
    registry = register_literature(sample_entries())
    statistics = generate_literature_statistics(registry)
    assert statistics["entry_count"] == 3
    assert statistics["unique_venue_count"] == 3
    assert statistics["unique_identifier_count"] == 2
    assert statistics["publication_year_min"] == 2021
    assert statistics["publication_year_max"] == 2023


def test_manifest_integrates_rp001_doc_and_pat_traces():
    registry = register_literature(sample_entries())
    manifest = export_literature_manifest(registry, generate_metadata())
    assert manifest["manifest_version"] == LITERATURE_MANIFEST_VERSION
    assert manifest["rp001_metadata"]["document_identifier"] == "AIDIP-PROJECT1-RP-001"
    assert manifest["documentation_trace"]["DOC-001"] == "DOC-001"
    assert manifest["documentation_trace"]["DOC-005"] == "DOC-005"
    assert manifest["patent_trace"]["PAT-001"] == "PAT-001"
    assert manifest["patent_trace"]["PAT-004"] == "PAT-004"
    assert manifest["integrity"]["external_literature_api_required"] is False
    assert manifest["integrity"]["novelty_claims_fabricated"] is False


def test_validate_literature_registry_success():
    registry = register_literature(sample_entries())
    validation = validate_literature_registry(registry)
    assert validation["status"] == "valid"
    assert validation["entry_count"] == 3
    assert validation["citation_fabricated"] is False
