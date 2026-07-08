import pytest

from commercial_release import (
    CERTIFICATION_GIT_TAG,
    CERTIFICATION_PRODUCT_VERSION,
    CERTIFICATION_REGRESSION_BASELINE,
    DuplicateReleaseIdentifierError,
    IncompleteReleaseCertificationError,
    MissingCertificationArtifactError,
    VersionConsistencyError,
    certify_production_release,
    create_certification_version_metadata,
    generate_certification_manifest,
    generate_production_readiness,
    generate_readiness_score,
    generate_release_certification,
    generate_release_metrics,
    validate_release_candidate,
    validate_release_metrics,
)


def test_production_readiness_generation_uses_current_baseline():
    readiness = generate_production_readiness()
    assert readiness["module"] == "REL-005"
    assert readiness["version_metadata"]["git_tag"] == CERTIFICATION_GIT_TAG
    assert readiness["version_metadata"]["product_version"] == CERTIFICATION_PRODUCT_VERSION
    assert readiness["release_metrics"]["regression"]["baseline"] == CERTIFICATION_REGRESSION_BASELINE
    assert readiness["scorecard"]["decision"] == "READY_FOR_PRODUCTION"
    assert readiness["scorecard"]["scores"]["Final Production Score"] == 100
    assert readiness["integrity"]["deployment_actions_performed"] is False
    assert validate_release_candidate(readiness)["status"] == "valid"


def test_certification_generation_produces_required_reports_and_json_artifacts():
    certification = generate_release_certification()
    assert certification["module"] == "REL-005"
    assert certification["status"] == "certified"
    assert certification["decision"] == "READY_FOR_PRODUCTION"
    assert set(certification["reports"]) == {
        "production_readiness_report.md",
        "release_certification.md",
        "deployment_readiness.md",
        "enterprise_readiness.md",
    }
    assert set(certification["json_artifacts"]) == {
        "production_readiness.json",
        "release_certification.json",
        "release_metrics.json",
        "release_scorecard.json",
    }
    assert certification["integrity"]["infrastructure_executed"] is False


def test_readiness_score_calculation_returns_not_ready_for_incomplete_area():
    readiness = generate_production_readiness()
    incomplete = {
        **readiness,
        "certification_areas": {
            **readiness["certification_areas"],
            "documentation": {
                **readiness["certification_areas"]["documentation"],
                "artifacts": (
                    {
                        **readiness["certification_areas"]["documentation"]["artifacts"][0],
                        "status": "missing",
                    },
                ),
            },
        },
    }
    scorecard = generate_readiness_score(incomplete)
    assert scorecard["scores"]["Documentation"] == 0
    assert scorecard["decision"] == "NOT_READY"


def test_missing_artifact_detection():
    readiness = generate_production_readiness()
    malformed = {
        **readiness,
        "certification_areas": {
            key: value
            for key, value in readiness["certification_areas"].items()
            if key != "documentation"
        },
    }
    with pytest.raises(MissingCertificationArtifactError, match="missing certification area"):
        validate_release_candidate(malformed)


def test_version_consistency_validation():
    metrics = generate_release_metrics()
    malformed = {
        **metrics,
        "version_metadata": {
            **metrics["version_metadata"],
            "git_tag": "v1.0.2-commercial-progress",
        },
    }
    with pytest.raises(VersionConsistencyError, match="git tag"):
        validate_release_metrics(malformed)


def test_duplicate_release_identifier_rejection():
    readiness = generate_production_readiness()
    duplicate = readiness["release_identifiers"][0]
    malformed = {**readiness, "release_identifiers": (duplicate, duplicate)}
    with pytest.raises(DuplicateReleaseIdentifierError, match="duplicate release identifiers"):
        validate_release_candidate(malformed)


def test_not_ready_candidate_rejected():
    readiness = generate_production_readiness()
    malformed = {
        **readiness,
        "scorecard": {
            **readiness["scorecard"],
            "decision": "NOT_READY",
            "scores": {**readiness["scorecard"]["scores"], "Final Production Score": 0},
        },
    }
    with pytest.raises(IncompleteReleaseCertificationError, match="not ready"):
        validate_release_candidate(malformed)


def test_certification_manifest_generation():
    manifest = generate_certification_manifest()
    assert manifest["module"] == "REL-005"
    assert manifest["decision"] == "READY_FOR_PRODUCTION"
    assert manifest["source_traces"]["REL"] == ("REL-001", "REL-002", "REL-003", "REL-004", "REL-005")
    assert manifest["source_traces"]["DOC"][0] == "DOC-001"
    assert manifest["source_traces"]["VB"][-1] == "VB-005"
    assert manifest["deployment_actions_performed"] is False


def test_integration_with_rel001_through_rel004_traces():
    readiness = generate_production_readiness()
    assert readiness["release_manifest"]["module"] == "REL-001"
    assert readiness["deployment_manifest"]["module"] == "REL-004"
    assert readiness["deployment_manifest"]["integration_traces"]["commercial_release"]["REL-002"] == "release bundle reference"
    assert readiness["deployment_manifest"]["integration_traces"]["commercial_release"]["REL-003"] == "security, compliance, and licensing reference"
    assert readiness["distribution_manifest"]["inventory_count"] == 7


def test_certify_production_release_alias():
    certification = certify_production_release()
    assert certification == generate_release_certification()


def test_deterministic_release_certification_output():
    first = generate_release_certification()
    second = generate_release_certification()
    assert first == second
    assert generate_production_readiness() == generate_production_readiness()
    assert generate_release_metrics() == generate_release_metrics()


def test_certification_version_metadata_is_valid():
    metadata = create_certification_version_metadata()
    assert metadata["product_version"] == "1.0.1-commercial-progress"
    assert metadata["git_tag"] == "v1.0.1-commercial-progress"
    assert metadata["regression_baseline"] == "606/606 passing"
    assert metadata["deployment_actions_performed"] is False
