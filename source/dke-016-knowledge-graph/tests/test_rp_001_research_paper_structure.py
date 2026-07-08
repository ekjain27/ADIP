import pytest

from research_paper import (
    AcronymEntry,
    DuplicateAcronymError,
    DuplicateSectionError,
    InconsistentPublicationProfileError,
    MalformedPaperMetadataError,
    NumberingConsistencyError,
    PAPER_MANIFEST_VERSION,
    PaperSection,
    create_research_paper_generator,
    default_acronyms,
    generate_acronym_registry,
    generate_metadata,
    generate_structure,
)


def test_generate_research_paper_structure():
    generator = create_research_paper_generator()
    paper = generator.generate_paper()
    assert paper["module"] == "RP-001"
    assert paper["status"] == "generated"
    assert paper["metadata"]["document_identifier"] == "AIDIP-PROJECT1-RP-001"
    assert paper["section_hierarchy"]["section_count"] == 10
    assert paper["figure_registry"]["figure_count"] == 8
    assert paper["table_registry"]["table_count"] == 3


def test_configurable_author_metadata():
    metadata = generate_metadata(
        authors=({"name": "Ada Engineer", "affiliation_id": "AFF-001", "orcid": "0000-0000"},),
        affiliations=("AFF-001: Decision Intelligence Lab",),
        correspondence={"name": "Ada Engineer", "email": "ada@example.invalid"},
        publication_profile="conference",
        target_venue_profile="IEEE",
    )
    assert metadata["authors"][0]["name"] == "Ada Engineer"
    assert metadata["publication_profile"] == "conference"
    assert metadata["target_venue_profile"] == "IEEE"


def test_malformed_metadata_rejection():
    with pytest.raises(MalformedPaperMetadataError, match="author metadata"):
        generate_metadata(authors=({"name": "", "affiliation_id": "AFF-001"},))


def test_invalid_publication_profile_rejection():
    with pytest.raises(InconsistentPublicationProfileError, match="unsupported publication profile"):
        generate_metadata(publication_profile="magazine")


def test_invalid_target_venue_rejection():
    with pytest.raises(InconsistentPublicationProfileError, match="unsupported target venue profile"):
        generate_metadata(target_venue_profile="UnknownVenue")


def test_duplicate_section_rejection():
    sections = (
        PaperSection("abstract", "Abstract"),
        PaperSection("abstract", "Abstract Again"),
    )
    with pytest.raises(DuplicateSectionError, match="duplicate section ID"):
        generate_structure(sections)


def test_duplicate_acronym_rejection():
    acronym = default_acronyms()[0]
    with pytest.raises(DuplicateAcronymError, match="duplicate acronym"):
        generate_acronym_registry((acronym, acronym))


def test_deterministic_paper_output():
    generator = create_research_paper_generator()
    first = generator.generate_paper()
    second = generator.generate_paper()
    assert first == second
    assert generator.generate_manifest() == generator.generate_manifest()


def test_manifest_generation():
    generator = create_research_paper_generator()
    manifest = generator.generate_manifest()
    assert manifest["module"] == "RP-001"
    assert manifest["manifest_version"] == PAPER_MANIFEST_VERSION
    assert manifest["completeness_report"]["status"] == "complete"
    assert manifest["integrity"]["citations_fabricated"] is False
    assert manifest["integrity"]["experimental_results_fabricated"] is False


def test_markdown_paper_template_export():
    generator = create_research_paper_generator()
    markdown = generator.export_markdown_paper()
    assert markdown.startswith("# Deterministic AI Decision Intelligence Platform")
    assert "## Abstract" in markdown
    assert "Content placeholder derived from platform metadata" in markdown


def test_validate_paper_numbering_rejection():
    generator = create_research_paper_generator()
    paper = generator.generate_paper()
    malformed_figures = (
        {**paper["figure_registry"]["figures"][0], "figure_number": 2},
        *paper["figure_registry"]["figures"][1:],
    )
    malformed_registry = {**paper["figure_registry"], "figures": malformed_figures}
    malformed = {**paper, "figure_registry": malformed_registry}
    with pytest.raises(NumberingConsistencyError, match="inconsistent figure_number numbering"):
        generator.validate_paper(malformed)


def test_validate_paper_success():
    generator = create_research_paper_generator()
    validation = generator.validate_paper()
    assert validation["module"] == "RP-001"
    assert validation["status"] == "valid"
    assert validation["citation_placeholder_count"] == 4


def test_integration_with_doc_pat_and_runtime_registry():
    generator = create_research_paper_generator()
    manifest = generator.generate_manifest()
    assert manifest["runtime_registry"]["module"] == "PI-002"
    assert manifest["documentation_trace"]["DOC-001"] == "DOC-001"
    assert manifest["documentation_trace"]["DOC-005"] == "DOC-005"
    assert manifest["patent_trace"]["PAT-001"] == "PAT-001.1"
    assert manifest["patent_trace"]["PAT-004"] == "PAT-004.1"


def test_acronym_entry_requires_values():
    with pytest.raises(MalformedPaperMetadataError, match="acronym and expansion"):
        AcronymEntry("", "Missing acronym")
