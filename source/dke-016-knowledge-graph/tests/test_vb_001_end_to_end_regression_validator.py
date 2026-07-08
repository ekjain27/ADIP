import pytest

from platform_integration import PlatformIntegrationLayer
from validation import (
    EndToEndRegressionValidator,
    IncompleteWorkflowError,
    MissingPlatformComponentError,
    SnapshotMismatchError,
    WorkflowRunner,
    create_baseline_snapshot,
    create_regression_validator,
)


def test_complete_workflow_validation():
    validator = create_regression_validator()
    result = validator.execute_workflow("complete_platform_pipeline")
    assert result["status"] == "passed"
    assert result["output_payload"]["enterprise"] == "ready"
    assert result["output_payload"]["recommendation"] == "ship"


def test_deterministic_regression_execution():
    validator = create_regression_validator()
    first = validator.execute_full_regression()
    second = validator.execute_full_regression()
    assert first == second
    assert first["status"] == "passed"
    assert first["workflow_count"] == 4


def test_baseline_comparison():
    validator = create_regression_validator()
    snapshot = validator.export_regression_snapshot()
    baseline = create_baseline_snapshot("baseline", snapshot)
    assert validator.compare_against_baseline(baseline) == {"status": "matched", "snapshot_id": "baseline"}


def test_baseline_mismatch_rejected():
    validator = create_regression_validator()
    baseline = create_baseline_snapshot("bad", {"module": "VB-001", "status": "failed"})
    with pytest.raises(SnapshotMismatchError, match="snapshot mismatch"):
        validator.compare_against_baseline(baseline)


def test_report_generation():
    validator = create_regression_validator()
    report = validator.generate_validation_report()
    assert report["module"] == "VB-001"
    assert report["report_type"] == "end_to_end_regression"
    assert report["status"] == "passed"


def test_snapshot_export():
    validator = create_regression_validator()
    snapshot = validator.export_regression_snapshot()
    assert snapshot["module"] == "VB-001"
    assert snapshot["runtime_registry"]["module"] == "PI-002"
    assert snapshot["api_gateway"]["module"] == "PI-004"
    assert snapshot["persistence"]["module"] == "PI-006"
    assert snapshot["observability"]["module"] == "PI-007"


def test_failure_diagnostics_for_unknown_workflow():
    runner = WorkflowRunner()
    with pytest.raises(IncompleteWorkflowError, match="workflow is not registered"):
        runner.execute_workflow("missing")


def test_missing_platform_component_rejected():
    runner = WorkflowRunner(PlatformIntegrationLayer())
    with pytest.raises(MissingPlatformComponentError, match="missing platform component"):
        runner.execute_workflow("research_to_dke")


def test_summarize_results():
    validator = create_regression_validator()
    summary = validator.summarize_results()
    assert summary == {
        "module": "VB-001",
        "status": "passed",
        "workflow_count": 4,
        "failed_count": 0,
        "diagnostic_count": 0,
    }


def test_integration_across_research_dke_die_and_pi_layers():
    validator = create_regression_validator()
    research_to_dke = validator.execute_workflow("research_to_dke")
    dke_to_die = validator.execute_workflow("dke_to_die")
    die_to_platform = validator.execute_workflow("die_to_platform")
    assert research_to_dke["output_payload"]["stage"] == "DKE"
    assert dke_to_die["output_payload"]["stage"] == "DIE"
    assert die_to_platform["output_payload"]["adaptive"] == "stable"


def test_full_regression_snapshot_is_deterministic():
    validator = create_regression_validator()
    first = validator.export_regression_snapshot()
    second = validator.export_regression_snapshot()
    assert first == second
    assert first["baseline_ready"] is True
