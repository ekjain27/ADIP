import pytest

from documentation import (
    DEPLOYMENT_MANIFEST_VERSION,
    DuplicateOperationalProcedureError,
    InconsistentDeploymentManifestError,
    OPERATIONAL_PROCEDURES,
    SUPPORTED_DEPLOYMENT_ENVIRONMENTS,
    UnsupportedDeploymentEnvironmentError,
    create_enterprise_deployment_guide_framework,
    validate_deployment_manifest,
)


def test_deployment_guide_generation():
    framework = create_enterprise_deployment_guide_framework()
    guide = framework.generate_deployment_guide()
    assert guide["module"] == "DOC-005"
    assert guide["status"] == "generated"
    assert guide["deployment_manifest"]["manifest_version"] == DEPLOYMENT_MANIFEST_VERSION


def test_environment_documentation():
    framework = create_enterprise_deployment_guide_framework()
    docs = framework.generate_environment_documentation()
    environments = tuple(item["environment"] for item in docs["environments"])
    assert environments == SUPPORTED_DEPLOYMENT_ENVIRONMENTS
    assert all(item["external_services_required"] is False for item in docs["environments"])


def test_unsupported_environment_rejection():
    framework = create_enterprise_deployment_guide_framework()
    with pytest.raises(UnsupportedDeploymentEnvironmentError, match="unsupported deployment environment"):
        framework.generate_environment_documentation("qa")


def test_operational_checklist_generation():
    framework = create_enterprise_deployment_guide_framework()
    checklist = framework.generate_operational_checklist()
    assert checklist["checklist_type"] == "operational_checklist"
    assert checklist["item_count"] >= 7
    assert all(item["required"] for item in checklist["items"])


def test_maintenance_documentation():
    framework = create_enterprise_deployment_guide_framework()
    plan = framework.generate_maintenance_plan()
    guide = framework.generate_deployment_guide()
    assert plan["plan_type"] == "maintenance_plan"
    assert plan["status"] == "generated"
    assert guide["maintenance_checklist"]["checklist_type"] == "maintenance_checklist"


def test_environment_readiness_report():
    framework = create_enterprise_deployment_guide_framework()
    report = framework.generate_environment_readiness_report()
    assert report["report_type"] == "environment_readiness"
    assert report["status"] == "ready"
    assert report["environment_count"] == 4


def test_deployment_manifest_validation():
    framework = create_enterprise_deployment_guide_framework()
    manifest = framework.generate_deployment_manifest()
    assert validate_deployment_manifest(manifest) == {
        "module": "DOC-005",
        "status": "valid",
        "environment_count": 4,
    }


def test_inconsistent_manifest_rejection():
    framework = create_enterprise_deployment_guide_framework()
    manifest = framework.generate_deployment_manifest()
    mutated = {**manifest, "environments": ("local",)}
    with pytest.raises(InconsistentDeploymentManifestError, match="inconsistent deployment manifest environments"):
        validate_deployment_manifest(mutated)


def test_operations_manual_and_markdown_export():
    framework = create_enterprise_deployment_guide_framework()
    manual = framework.generate_operations_manual()
    markdown = framework.export_operations_markdown()
    procedure_ids = tuple(item["id"] for item in manual["procedures"])
    assert procedure_ids == OPERATIONAL_PROCEDURES
    assert markdown.startswith("# Enterprise Deployment Guide & Operations Manual")
    assert "## Monitoring Guide" in markdown
    assert "## Disaster Recovery Guide" in markdown


def test_duplicate_operational_procedure_rejection():
    framework = create_enterprise_deployment_guide_framework()
    guide = framework.generate_deployment_guide()
    procedures = guide["operations_manual"]["procedures"]
    mutated_manual = {**guide["operations_manual"], "procedures": (*procedures, procedures[0])}
    mutated = {**guide, "operations_manual": mutated_manual}
    with pytest.raises(DuplicateOperationalProcedureError, match="duplicate operational procedure"):
        framework.validate_operations_documentation(mutated)


def test_deterministic_output():
    framework = create_enterprise_deployment_guide_framework()
    assert framework.generate_deployment_guide() == framework.generate_deployment_guide()
    assert framework.export_operations_markdown() == framework.export_operations_markdown()


def test_integration_with_doc001_through_doc004_and_pi_layers():
    framework = create_enterprise_deployment_guide_framework()
    guide = framework.generate_deployment_guide()
    manifest = guide["deployment_manifest"]
    first_report = guide["environment_readiness_report"]["reports"][0]
    assert manifest["architecture_module"] == "DOC-001"
    assert manifest["developer_module"] == "DOC-004"
    assert first_report["checks"]["observability_ready"] is True
    assert first_report["checks"]["configuration_complete"] is True
