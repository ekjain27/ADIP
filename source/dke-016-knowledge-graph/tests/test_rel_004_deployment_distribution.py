import pytest

from commercial_release import (
    SUPPORTED_CONFIGURATION_PROFILES,
    SUPPORTED_DEPLOYMENT_TARGETS,
    DuplicateDeploymentIdentifierError,
    IncompleteConfigurationError,
    InconsistentUpgradePlanError,
    MalformedDeploymentManifestError,
    UnsupportedDeploymentProfileError,
    generate_all_deployment_profiles_manifest,
    generate_compatibility_matrix,
    generate_configuration,
    generate_configuration_manifest,
    generate_deployment_manifest,
    generate_deployment_profile,
    generate_distribution_manifest,
    generate_operations_checklist,
    generate_rollback_plan,
    generate_upgrade_plan,
    validate_compatibility_matrix,
    validate_deployment_package,
)


def test_supported_deployment_profile_generation():
    profiles = tuple(generate_deployment_profile(profile_name) for profile_name in SUPPORTED_DEPLOYMENT_TARGETS)
    assert tuple(profile["profile_name"] for profile in profiles) == SUPPORTED_DEPLOYMENT_TARGETS
    assert tuple(profile["display_name"] for profile in profiles) == (
        "Local Workstation",
        "Enterprise Server",
        "Docker",
        "Kubernetes",
        "Cloud VM",
        "Air-gapped Enterprise",
        "Evaluation Installation",
    )
    assert all(profile["deployment_actions_performed"] is False for profile in profiles)
    assert all(profile["external_services_required"] is False for profile in profiles)


def test_unsupported_deployment_profile_rejected():
    with pytest.raises(UnsupportedDeploymentProfileError, match="unsupported deployment profile"):
        generate_deployment_profile("mainframe")


def test_configuration_manifest_covers_required_profiles():
    manifest = generate_configuration_manifest()
    assert tuple(configuration["configuration_id"] for configuration in manifest["configurations"]) == SUPPORTED_CONFIGURATION_PROFILES
    assert manifest["configuration_count"] == 4
    production = generate_configuration("production")
    assert production["configuration"]["runtime"]["mode"] == "production"
    assert production["secrets_embedded"] is False


def test_invalid_configuration_rejected():
    with pytest.raises(IncompleteConfigurationError, match="unsupported configuration profile"):
        generate_configuration("staging")


def test_compatibility_matrix_is_deterministic_and_complete():
    first = generate_compatibility_matrix()
    second = generate_compatibility_matrix()
    assert first == second
    assert validate_compatibility_matrix(first)["status"] == "valid"
    assert tuple(row["profile_name"] for row in first["rows"]) == SUPPORTED_DEPLOYMENT_TARGETS
    assert all(row["deployment_execution_supported"] is False for row in first["rows"])


def test_duplicate_deployment_identifiers_rejected():
    matrix = generate_compatibility_matrix()
    malformed = {
        **matrix,
        "rows": (
            matrix["rows"][0],
            {**matrix["rows"][1], "deployment_id": matrix["rows"][0]["deployment_id"]},
            *matrix["rows"][2:],
        ),
    }
    with pytest.raises(DuplicateDeploymentIdentifierError, match="duplicate deployment identifiers"):
        validate_compatibility_matrix(malformed)


def test_upgrade_and_rollback_plans_are_consistent():
    upgrade = generate_upgrade_plan("kubernetes")
    rollback = generate_rollback_plan("kubernetes")
    assert upgrade["deployment_id"] == "deploy-kubernetes"
    assert rollback["deployment_id"] == "deploy-kubernetes"
    assert upgrade["deployment_actions_performed"] is False
    assert rollback["deployment_actions_performed"] is False
    assert "review compatibility matrix" in upgrade["upgrade_path"]
    assert "restore previous configuration snapshot" in rollback["rollback_path"]


def test_deployment_manifest_generation_and_integrations():
    manifest = generate_deployment_manifest("air_gapped_enterprise")
    assert manifest["module"] == "REL-004"
    assert manifest["deployment_profile"]["display_name"] == "Air-gapped Enterprise"
    assert manifest["integration_traces"]["commercial_release"]["REL-001"] == "version and release metadata"
    assert manifest["integration_traces"]["commercial_release"]["REL-002"] == "release bundle reference"
    assert manifest["integration_traces"]["commercial_release"]["REL-003"] == "security, compliance, and licensing reference"
    assert manifest["integration_traces"]["documentation"] == tuple(f"DOC-{index:03d}" for index in range(1, 6))
    assert manifest["integration_traces"]["validation"] == tuple(f"VB-{index:03d}" for index in range(1, 6))
    assert set(manifest["markdown_artifacts"]) == {
        "deployment_guide",
        "installation_guide",
        "upgrade_guide",
        "operations_guide",
    }
    assert validate_deployment_package(manifest)["status"] == "valid"


def test_distribution_manifest_contains_required_artifacts():
    manifest = generate_distribution_manifest("enterprise_server")
    assert manifest["deployment_id"] == "deploy-enterprise_server"
    assert manifest["deployment_bundle_manifest"]["deployment_actions_performed"] is False
    assert manifest["installation_manifest"]["installation_actions_performed"] is False
    assert tuple(item["artifact_id"] for item in manifest["distribution_inventory"]) == (
        "package-manifest",
        "deployment-bundle-manifest",
        "installation-manifest",
        "configuration-manifest",
        "security-compliance-manifest",
        "validation-baseline",
        "documentation-package",
    )


def test_operations_checklist_generation():
    checklist = generate_operations_checklist("docker")
    assert checklist["deployment_id"] == "deploy-docker"
    assert "verify runtime process status" in checklist["health_check_manifest"]
    assert "preserve logs and audit evidence" in checklist["shutdown_checklist"]
    assert checklist["deployment_actions_performed"] is False


def test_deployment_package_rejects_execution_flags():
    manifest = generate_deployment_manifest("docker")
    malformed = {**manifest, "integrity": {**manifest["integrity"], "docker_executed": True}}
    with pytest.raises(MalformedDeploymentManifestError, match="must not execute"):
        validate_deployment_package(malformed)


def test_deployment_package_rejects_inconsistent_upgrade_mapping():
    manifest = generate_deployment_manifest("cloud_vm")
    malformed = {**manifest, "upgrade_plan": {**manifest["upgrade_plan"], "deployment_id": "deploy-docker"}}
    with pytest.raises(InconsistentUpgradePlanError, match="upgrade plan deployment_id"):
        validate_deployment_package(malformed)


def test_all_profiles_manifest_is_deterministic():
    first = generate_all_deployment_profiles_manifest()
    second = generate_all_deployment_profiles_manifest()
    assert first == second
    assert tuple(profile["deployment_id"] for profile in first["profiles"]) == tuple(
        f"deploy-{profile_name}" for profile_name in SUPPORTED_DEPLOYMENT_TARGETS
    )
