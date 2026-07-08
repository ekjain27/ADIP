import pytest

from research_paper.manuscript_assembler import (
    MANDATORY_MANUSCRIPT_SECTION_IDS,
    assemble_manuscript,
    export_markdown_manuscript,
    validate_manuscript,
)
from research_paper.publication_errors import (
    DuplicatePublicationSectionError,
    FabricatedPublicationClaimError,
    MalformedPublicationProfileError,
    MissingMandatoryPublicationSectionError,
    PublicationNumberingConsistencyError,
)
from research_paper.publication_manifest import PUBLICATION_MANIFEST_VERSION, generate_publication_manifest
from research_paper.publication_package import validate_publication_package
from research_paper.publication_package_profiles import SUPPORTED_PUBLICATION_VENUES, generate_publication_profile
from research_paper.submission_checklist import generate_artifact_checklist, generate_submission_checklist


def test_publication_profile_generation_for_supported_venues():
    profiles = tuple(generate_publication_profile(venue) for venue in SUPPORTED_PUBLICATION_VENUES)
    assert tuple(profile["venue"] for profile in profiles) == SUPPORTED_PUBLICATION_VENUES
    assert all(profile["submission_material_policy"]["references_must_be_user_supplied"] is True for profile in profiles)
    assert all(profile["submission_material_policy"]["reviewer_responses_fabricated"] is False for profile in profiles)


def test_malformed_publication_profile_rejection():
    with pytest.raises(MalformedPublicationProfileError, match="unsupported publication venue"):
        generate_publication_profile("UnknownVenue")


def test_manuscript_assembly_contains_mandatory_sections():
    manuscript = assemble_manuscript("ACM")
    section_ids = tuple(section["section_id"] for section in manuscript["sections"])
    assert manuscript["module"] == "RP-005"
    assert manuscript["publication_profile"]["venue"] == "ACM"
    assert section_ids == MANDATORY_MANUSCRIPT_SECTION_IDS
    assert manuscript["figures_list"]["figure_count"] == 8
    assert manuscript["tables_list"]["table_count"] == 3
    assert manuscript["sections"][12]["section_id"] == "references_placeholder"
    assert manuscript["sections"][12]["content"]["fabricated_references"] is False


def test_markdown_manuscript_export():
    manuscript = assemble_manuscript("arXiv")
    markdown = export_markdown_manuscript(manuscript)
    assert markdown.startswith("# Deterministic AI Decision Intelligence Platform")
    assert "## References Placeholder" in markdown
    assert "## Reproducibility Statement" in markdown
    assert "Publication profile: arXiv" in markdown


def test_submission_and_artifact_checklists():
    manuscript = assemble_manuscript("IEEE")
    submission = generate_submission_checklist(manuscript)
    artifacts = generate_artifact_checklist(manuscript)
    assert submission["status"] == "complete"
    assert submission["check_count"] == 8
    assert artifacts["status"] == "complete"
    assert artifacts["artifact_count"] == 8


def test_publication_manifest_generation_and_traces():
    manifest = generate_publication_manifest(venue="Springer")
    assert manifest["module"] == "RP-005"
    assert manifest["manifest_version"] == PUBLICATION_MANIFEST_VERSION
    assert manifest["publication_profile"]["venue"] == "Springer"
    assert manifest["publication_completeness_report"]["status"] == "complete"
    assert manifest["source_manifests"]["RP-001"] == "RP-001.1"
    assert manifest["source_manifests"]["RP-002"] == "RP-002"
    assert manifest["source_manifests"]["RP-003"] == "RP-003.1"
    assert manifest["source_manifests"]["RP-004"] == "RP-004.1"
    assert manifest["source_manifests"]["documentation_trace"]["DOC-001"] == "DOC-001"
    assert manifest["source_manifests"]["documentation_trace"]["DOC-005"] == "DOC-005"
    assert manifest["source_manifests"]["patent_trace"]["PAT-001"] == "PAT-001.1"
    assert manifest["source_manifests"]["patent_trace"]["PAT-004"] == "PAT-004.1"
    assert manifest["source_manifests"]["runtime_registry"]["module"] == "PI-002"


def test_validate_publication_package_success():
    validation = validate_publication_package(generate_publication_manifest(venue="Elsevier"))
    assert validation["module"] == "RP-005"
    assert validation["status"] == "valid"
    assert validation["venue"] == "Elsevier"
    assert validation["section_count"] == len(MANDATORY_MANUSCRIPT_SECTION_IDS)


def test_deterministic_publication_package_output():
    first = generate_publication_manifest(venue="arXiv")
    second = generate_publication_manifest(venue="arXiv")
    assert first == second
    assert assemble_manuscript("IEEE") == assemble_manuscript("IEEE")


def test_duplicate_section_id_rejection():
    manuscript = assemble_manuscript()
    malformed = {
        **manuscript,
        "sections": (
            manuscript["sections"][0],
            manuscript["sections"][0],
            *manuscript["sections"][2:],
        ),
    }
    with pytest.raises(DuplicatePublicationSectionError, match="duplicate publication section IDs"):
        validate_manuscript(malformed)


def test_missing_mandatory_section_rejection():
    manuscript = assemble_manuscript()
    malformed = {**manuscript, "sections": manuscript["sections"][:-1]}
    with pytest.raises(MissingMandatoryPublicationSectionError, match="missing mandatory manuscript section"):
        validate_manuscript(malformed)


def test_figure_numbering_rejection():
    manuscript = assemble_manuscript()
    malformed_figures = (
        {**manuscript["figures_list"]["figures"][0], "figure_number": 2},
        *manuscript["figures_list"]["figures"][1:],
    )
    malformed = {**manuscript, "figures_list": {**manuscript["figures_list"], "figures": malformed_figures}}
    with pytest.raises(PublicationNumberingConsistencyError, match="inconsistent figure_number numbering"):
        validate_manuscript(malformed)


def test_fabricated_claim_rejection():
    manuscript = assemble_manuscript()
    malformed = {
        **manuscript,
        "integrity": {**manuscript["integrity"], "acceptance_information_fabricated": True},
    }
    with pytest.raises(FabricatedPublicationClaimError, match="cannot fabricate"):
        validate_manuscript(malformed)
