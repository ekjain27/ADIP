import pytest

from patent import (
    DuplicateAnalysisError,
    DuplicateReferenceError,
    InconsistentNoveltyTraceabilityError,
    MissingInnovationReferenceError,
    NOVELTY_MANIFEST_VERSION,
    NoveltyComparisonRecord,
    PriorArtReference,
    create_novelty_analysis_framework,
)


def test_reference_registration():
    framework = create_novelty_analysis_framework()
    reference = PriorArtReference("REF-001", "Workflow reference", "publication", "Workflow comparison", ("workflow",))
    framework.register_reference(reference)
    assert framework.reference_registry.list_references() == (reference,)


def test_duplicate_reference_rejection():
    framework = create_novelty_analysis_framework()
    reference = PriorArtReference("REF-001", "Workflow reference", "publication", "Workflow comparison")
    framework.register_reference(reference)
    with pytest.raises(DuplicateReferenceError, match="duplicate reference ID"):
        framework.register_reference(reference)


def test_deterministic_analysis():
    framework = create_novelty_analysis_framework()
    framework.register_reference(PriorArtReference("REF-001", "Workflow reference", "publication", "Workflow comparison"))
    first = framework.generate_novelty_matrix()
    second = framework.generate_novelty_matrix()
    assert first == second
    assert first["analysis_count"] == 8
    assert tuple(row["analysis_id"] for row in first["analyses"]) == tuple(sorted(row["analysis_id"] for row in first["analyses"]))


def test_analyze_innovation():
    framework = create_novelty_analysis_framework()
    innovation = framework.patent_framework.discover_innovations()[0]
    reference = PriorArtReference("REF-001", "Workflow reference", "publication", "Workflow comparison")
    record = framework.analyze_innovation(innovation, reference)
    assert record.innovation_id == innovation.innovation_id
    assert record.reference_id == "REF-001"
    assert record.implementation_evidence


def test_innovation_coverage():
    framework = create_novelty_analysis_framework()
    manifest = framework.export_novelty_manifest()
    coverage = manifest["innovation_coverage_report"]
    assert coverage["status"] == "complete"
    assert coverage["innovation_count"] == 8
    assert all(count >= 1 for _, count in coverage["coverage"])


def test_reference_coverage():
    framework = create_novelty_analysis_framework()
    framework.register_reference(PriorArtReference("REF-001", "Workflow reference", "publication", "Workflow comparison"))
    report = framework.generate_reference_coverage()
    assert report["status"] == "complete"
    assert report["reference_count"] == 1
    assert report["coverage"] == (("REF-001", 8),)


def test_traceability_validation():
    framework = create_novelty_analysis_framework()
    validation = framework.validate_novelty_analysis()
    assert validation["module"] == "PAT-003"
    assert validation["status"] == "valid"
    assert validation["innovation_count"] == 8


def test_duplicate_analysis_rejection():
    framework = create_novelty_analysis_framework()
    record = framework._comparison_records()[0]
    with pytest.raises(DuplicateAnalysisError, match="duplicate analysis ID"):
        framework.validate_novelty_analysis((record, record))


def test_missing_innovation_reference_rejection():
    framework = create_novelty_analysis_framework()
    record = NoveltyComparisonRecord(
        "PAT-003-ORPHAN",
        "PAT-001-UNKNOWN",
        "REF-001",
        "Orphan comparison",
        ("distinguishing",),
        ("evidence",),
        ("DPG",),
    )
    with pytest.raises(MissingInnovationReferenceError, match="missing innovation reference"):
        framework.validate_novelty_analysis((record,))


def test_inconsistent_traceability_rejection():
    with pytest.raises(InconsistentNoveltyTraceabilityError, match="lacks implementation evidence"):
        NoveltyComparisonRecord(
            "PAT-003-BAD",
            "PAT-001-DPG",
            "REF-001",
            "Bad comparison",
            ("distinguishing",),
            (),
            ("DPG",),
        )


def test_markdown_and_json_exports():
    framework = create_novelty_analysis_framework()
    matrix = framework.generate_novelty_matrix()
    manifest = framework.export_novelty_manifest()
    assert matrix["markdown"].startswith("# Novelty Matrix")
    assert manifest["module"] == "PAT-003"
    assert manifest["manifest_version"] == NOVELTY_MANIFEST_VERSION
    assert manifest["legal_notice"].startswith("Structured comparison support")


def test_integration_with_pat001_pat002_and_runtime_registry():
    framework = create_novelty_analysis_framework()
    manifest = framework.export_novelty_manifest()
    assert framework.patent_framework.export_patent_manifest()["module"] == "PAT-001"
    assert framework.claims_framework.generate_claims_manifest()["module"] == "PAT-002"
    assert manifest["runtime_registry"]["module"] == "PI-002"
