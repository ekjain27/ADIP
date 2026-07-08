import pytest

from patent import (
    DuplicateFigureError,
    FIGURE_MANIFEST_VERSION,
    IncompleteSpecificationTraceabilityError,
    MalformedSpecificationSectionError,
    PatentFigure,
    SPECIFICATION_MANIFEST_VERSION,
    create_patent_specification_generator,
    default_patent_figures,
    generate_patent_figure_manifest,
)


def test_specification_generation():
    generator = create_patent_specification_generator()
    specification = generator.generate_patent_specification()
    assert specification["module"] == "PAT-004"
    assert specification["status"] == "generated"
    assert specification["section_count"] == 11
    assert specification["claim_count"] == 16
    assert specification["figure_count"] == 8
    assert specification["sections"][0]["section_id"] == "patent_title"


def test_figure_manifest_generation():
    generator = create_patent_specification_generator()
    manifest = generator.generate_figure_manifest()
    assert manifest["module"] == "PAT-004"
    assert manifest["manifest_version"] == FIGURE_MANIFEST_VERSION
    assert manifest["figure_count"] == 8
    assert tuple(figure["figure_id"] for figure in manifest["figures"]) == tuple(
        sorted(figure["figure_id"] for figure in manifest["figures"])
    )


def test_deterministic_output():
    generator = create_patent_specification_generator()
    first_specification = generator.generate_patent_specification()
    second_specification = generator.generate_patent_specification()
    first_manifest = generator.export_json_manifest()
    second_manifest = generator.export_json_manifest()
    assert first_specification == second_specification
    assert first_manifest == second_manifest


def test_completeness_validation():
    generator = create_patent_specification_generator()
    validation = generator.validate_specification()
    assert validation["module"] == "PAT-004"
    assert validation["status"] == "valid"
    assert validation["innovation_count"] == 8
    assert validation["figure_count"] == 8


def test_duplicate_figure_rejection():
    figure = default_patent_figures()[0]
    with pytest.raises(DuplicateFigureError, match="duplicate figure ID"):
        generate_patent_figure_manifest((figure, figure))


def test_malformed_specification_section_rejection():
    generator = create_patent_specification_generator()
    specification = generator.generate_patent_specification()
    malformed_sections = tuple(
        {"section_id": section["section_id"], "title": section["title"], "content": ""}
        if section["section_id"] == "background"
        else section
        for section in specification["sections"]
    )
    malformed = {**specification, "sections": malformed_sections}
    with pytest.raises(MalformedSpecificationSectionError, match="malformed specification section"):
        generator.validate_specification(malformed)


def test_traceability_validation():
    generator = create_patent_specification_generator()
    specification = generator.generate_patent_specification()
    incomplete = {**specification, "innovation_ids": specification["innovation_ids"][1:]}
    with pytest.raises(IncompleteSpecificationTraceabilityError, match="incomplete innovation traceability"):
        generator.validate_specification(incomplete)


def test_markdown_specification_export():
    generator = create_patent_specification_generator()
    markdown = generator.export_markdown_specification()
    assert markdown.startswith("# Patent Specification Draft")
    assert "## Technical Field" in markdown
    assert "professional legal review" in markdown


def test_json_manifest_export():
    generator = create_patent_specification_generator()
    manifest = generator.export_json_manifest()
    assert manifest["module"] == "PAT-004"
    assert manifest["manifest_version"] == SPECIFICATION_MANIFEST_VERSION
    assert manifest["source_manifests"]["PAT-001"] == "PAT-001.1"
    assert manifest["source_manifests"]["PAT-002"] == "PAT-002.1"
    assert manifest["source_manifests"]["PAT-003"] == "PAT-003.1"
    assert manifest["completeness_report"]["status"] == "complete"


def test_integration_with_pat001_through_pat003():
    generator = create_patent_specification_generator()
    assert generator.patent_framework.export_patent_manifest()["module"] == "PAT-001"
    assert generator.claims_framework.generate_claims_manifest()["module"] == "PAT-002"
    assert generator.novelty_framework.export_novelty_manifest()["module"] == "PAT-003"
    assert generator.runtime_registry.export_registry_snapshot()["module"] == "PI-002"


def test_integration_with_doc001_through_doc005():
    generator = create_patent_specification_generator()
    documentation_trace = generator.export_json_manifest()["documentation_trace"]
    assert documentation_trace == {
        "DOC-001": "DOC-001",
        "DOC-002": "DOC-002",
        "DOC-003": "DOC-003",
        "DOC-004": "DOC-004",
        "DOC-005": "DOC-005",
        "PI-002": "PI-002",
    }


def test_malformed_figure_metadata_rejection():
    with pytest.raises(MalformedSpecificationSectionError, match="figure lacks related modules"):
        PatentFigure("FIG-999", "Empty", "No modules", ())
