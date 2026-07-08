import pytest

from patent import (
    INNOVATION_MODULES,
    PATENT_MANIFEST_VERSION,
    DuplicateInnovationError,
    InnovationRecord,
    MalformedDisclosureError,
    UnsupportedInnovationMappingError,
    create_patent_preparation_framework,
    generate_innovation_registry,
    validate_invention_disclosure,
)


def test_discover_innovations():
    framework = create_patent_preparation_framework()
    innovations = framework.discover_innovations()
    assert tuple(record.related_modules[0] for record in innovations) == tuple(sorted(INNOVATION_MODULES))
    assert len(innovations) == 8


def test_generate_innovation_registry():
    framework = create_patent_preparation_framework()
    registry = framework.generate_innovation_registry()
    assert registry["module"] == "PAT-001"
    assert registry["registry_type"] == "innovation_registry"
    assert registry["innovation_count"] == 8


def test_validate_innovation_registry():
    framework = create_patent_preparation_framework()
    validation = framework.validate_innovation_registry()
    assert validation == {"module": "PAT-001", "status": "valid", "innovation_count": 8}


def test_duplicate_innovation_rejection():
    framework = create_patent_preparation_framework()
    innovation = framework.discover_innovations()[0]
    with pytest.raises(DuplicateInnovationError, match="duplicate innovation ID"):
        generate_innovation_registry((innovation, innovation))


def test_unsupported_mapping_rejection():
    bad = InnovationRecord(
        innovation_id="PAT-001-BAD",
        title="Bad",
        description="Bad mapping",
        related_modules=("UNKNOWN",),
        architectural_contribution="Bad",
        novelty_summary="Bad",
    )
    framework = create_patent_preparation_framework()
    with pytest.raises(UnsupportedInnovationMappingError, match="unsupported innovation mapping"):
        framework.validate_innovation_registry((bad,))


def test_generate_invention_disclosure():
    framework = create_patent_preparation_framework()
    disclosure = framework.generate_invention_disclosure()
    assert disclosure["module"] == "PAT-001"
    assert disclosure["artifact_type"] == "invention_disclosure"
    assert disclosure["innovation_count"] == 8


def test_malformed_disclosure_rejection():
    with pytest.raises(MalformedDisclosureError, match="malformed invention disclosure"):
        validate_invention_disclosure({"module": "PAT-001"})


def test_export_patent_manifest():
    framework = create_patent_preparation_framework()
    manifest = framework.export_patent_manifest()
    assert manifest["module"] == "PAT-001"
    assert manifest["manifest_version"] == PATENT_MANIFEST_VERSION
    assert manifest["innovation_summary_report"]["innovation_count"] == 8
    assert manifest["runtime_registry"]["module"] == "PI-002"


def test_markdown_disclosure_contains_mapped_innovations():
    framework = create_patent_preparation_framework()
    markdown = framework.export_patent_manifest()["markdown_disclosure"]
    assert markdown.startswith("# Invention Disclosure Draft")
    assert "PAT-001-DPG" in markdown
    assert "PAT-001-EDOF" in markdown


def test_documentation_traceability():
    framework = create_patent_preparation_framework()
    trace = framework.export_patent_manifest()["documentation_trace"]
    assert trace == {
        "DOC-001": "DOC-001",
        "DOC-002": "DOC-002",
        "DOC-003": "DOC-003",
        "DOC-004": "DOC-004",
        "DOC-005": "DOC-005",
        "PI-002": "PI-002",
    }


def test_deterministic_patent_artifacts():
    framework = create_patent_preparation_framework()
    assert framework.export_patent_manifest() == framework.export_patent_manifest()
