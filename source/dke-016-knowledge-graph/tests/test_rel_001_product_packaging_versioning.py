import pytest

from commercial_release import (
    DEFAULT_GIT_TAG,
    DEFAULT_PRODUCT_NAME,
    DEFAULT_PRODUCT_VERSION,
    DEFAULT_REGRESSION_BASELINE,
    RELEASE_MANIFEST_VERSION,
    SUPPORTED_RELEASE_CHANNELS,
    InconsistentReleaseManifestError,
    InvalidGitTagError,
    InvalidRegressionBaselineError,
    InvalidVersionMetadataError,
    UnsupportedReleaseChannelError,
    create_version_metadata,
    export_release_snapshot,
    generate_changelog,
    generate_package_metadata,
    generate_release_manifest,
    validate_release_manifest,
    validate_version_metadata,
)


def test_version_metadata_creation_uses_official_baseline():
    metadata = create_version_metadata()
    assert metadata["module"] == "REL-001"
    assert metadata["product_name"] == DEFAULT_PRODUCT_NAME
    assert metadata["product_version"] == DEFAULT_PRODUCT_VERSION
    assert metadata["release_channel"] == "pre_release"
    assert metadata["git_tag"] == DEFAULT_GIT_TAG
    assert metadata["regression_baseline"] == DEFAULT_REGRESSION_BASELINE
    assert metadata["deployment_actions_performed"] is False


def test_semantic_version_validation_success():
    validation = validate_version_metadata(create_version_metadata(product_version="2.3.4-beta.1", git_tag="v2.3.4-beta.1"))
    assert validation["status"] == "valid"
    assert validation["product_version"] == "2.3.4-beta.1"
    assert validation["regression_passed"] == 535
    assert validation["regression_total"] == 535


def test_invalid_version_rejection():
    with pytest.raises(InvalidVersionMetadataError, match="invalid semantic version"):
        create_version_metadata(product_version="1.0")


def test_empty_product_name_rejection():
    with pytest.raises(InvalidVersionMetadataError, match="product_name is required"):
        create_version_metadata(product_name="")


def test_release_channel_validation():
    assert tuple(
        create_version_metadata(release_channel=channel)["release_channel"]
        for channel in SUPPORTED_RELEASE_CHANNELS
    ) == SUPPORTED_RELEASE_CHANNELS
    with pytest.raises(UnsupportedReleaseChannelError, match="unsupported release channel"):
        create_version_metadata(release_channel="nightly")


def test_git_tag_validation():
    with pytest.raises(InvalidGitTagError, match="invalid git tag"):
        create_version_metadata(git_tag="1.0.0-pre-release")


def test_regression_baseline_validation():
    with pytest.raises(InvalidRegressionBaselineError, match="invalid regression baseline"):
        create_version_metadata(regression_baseline="535 passing")
    with pytest.raises(InvalidRegressionBaselineError, match="invalid regression baseline"):
        create_version_metadata(regression_baseline="536/535 passing")


def test_changelog_generation():
    changelog = generate_changelog()
    assert changelog["module"] == "REL-001"
    assert changelog["entry_count"] == 4
    assert tuple(entry["change_id"] for entry in changelog["entries"]) == (
        "REL-001-001",
        "REL-001-002",
        "REL-001-003",
        "REL-001-004",
    )
    assert all(entry["new_ai_capability"] is False for entry in changelog["entries"])


def test_package_metadata_generation():
    package = generate_package_metadata()
    assert package["module"] == "REL-001"
    assert package["product"]["git_tag"] == "v1.0.0-pre-release"
    assert package["baseline"]["regression_baseline"] == "535/535 passing"
    assert package["package_scope"]["release_infrastructure_only"] is True
    assert package["package_scope"]["deployment_actions_performed"] is False


def test_release_manifest_generation_and_integrations():
    manifest = generate_release_manifest()
    assert manifest["module"] == "REL-001"
    assert manifest["manifest_version"] == RELEASE_MANIFEST_VERSION
    assert manifest["source_traces"]["documentation"]["DOC-001"] == "DOC-001"
    assert manifest["source_traces"]["documentation"]["DOC-005"] == "DOC-005"
    assert manifest["source_traces"]["validation"]["VB-001"] == "VB-001"
    assert manifest["source_traces"]["validation"]["VB-005"] == "VB-005"
    assert manifest["source_traces"]["patent"]["PAT-001"] == "PAT-001.1"
    assert manifest["source_traces"]["patent"]["PAT-004"] == "PAT-004.1"
    assert manifest["source_traces"]["research_paper"]["RP-001"] == "RP-001.1"
    assert manifest["source_traces"]["research_paper"]["RP-005"] == "RP-005.1"
    assert manifest["integrity"]["external_services_required"] is False
    assert manifest["integrity"]["deployment_actions_performed"] is False


def test_release_manifest_validation_rejects_inconsistent_package_metadata():
    manifest = generate_release_manifest()
    malformed = {
        **manifest,
        "package_metadata": {
            **manifest["package_metadata"],
            "product": {**manifest["package_metadata"]["product"], "version": "9.9.9"},
        },
    }
    with pytest.raises(InconsistentReleaseManifestError, match="package metadata does not match"):
        validate_release_manifest(malformed)


def test_deterministic_snapshot_export():
    first = export_release_snapshot()
    second = export_release_snapshot()
    assert first == second
    assert first["version_metadata"] == create_version_metadata()
    assert validate_release_manifest(first)["status"] == "valid"
