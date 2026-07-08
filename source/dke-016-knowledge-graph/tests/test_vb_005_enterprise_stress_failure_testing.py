import pytest

from validation import (
    DuplicateStressScenarioError,
    MalformedWorkloadError,
    STRESS_BASELINE_VERSION,
    StressBaselineError,
    StressScenarioDefinition,
    StressScenarioDefinitionError,
    UnsupportedFailureSimulationError,
    create_baseline_snapshot,
    create_enterprise_stress_test_engine,
)


def test_stress_scenario_registration():
    engine = create_enterprise_stress_test_engine()
    scenario = StressScenarioDefinition("custom", "Custom stress", "repeated_execution", {"units": 2, "payload_size": 1})
    engine.register_stress_scenario(scenario)
    assert engine.scenarios()["custom"] == scenario


def test_duplicate_scenario_rejection():
    engine = create_enterprise_stress_test_engine()
    duplicate = StressScenarioDefinition("high-volume", "Duplicate", "high_workflow_volume", {"units": 1})
    with pytest.raises(DuplicateStressScenarioError, match="already registered"):
        engine.register_stress_scenario(duplicate)


def test_deterministic_workload_execution():
    engine = create_enterprise_stress_test_engine()
    first = engine.execute_stress_test("high-volume")
    second = engine.execute_stress_test("high-volume")
    assert first == second
    assert first["status"] == "completed"
    assert first["scorecard"]["status"] == "passed"


def test_simulated_component_failure():
    engine = create_enterprise_stress_test_engine()
    result = engine.execute_stress_test("component-unavailable")
    assert result["platform_status"] == "degraded"
    assert result["failure"]["mode"] == "component_unavailable"
    assert result["failure"]["error"] == "DIE unavailable"


def test_graceful_degradation_and_recovery_validation():
    engine = create_enterprise_stress_test_engine()
    result = engine.execute_stress_test("dependency-failure")
    metrics = dict(result["scorecard"]["metrics"])
    assert metrics["graceful_degradation"] == 1.0
    assert metrics["recovery_behavior"] == 1.0
    assert metrics["retry_policy_behavior"] == 1.0


def test_resilience_scoring():
    engine = create_enterprise_stress_test_engine()
    scorecard = engine.generate_resilience_scorecard("large-payload")
    assert scorecard["scenario_id"] == "large-payload"
    assert scorecard["score"] == 1.0


def test_baseline_comparison():
    engine = create_enterprise_stress_test_engine()
    snapshot = engine.export_stress_snapshot()
    baseline = create_baseline_snapshot("stress-baseline", snapshot)
    assert engine.compare_stress_baseline(baseline) == {"status": "matched", "snapshot_id": "stress-baseline"}


def test_inconsistent_baseline_version_rejected():
    engine = create_enterprise_stress_test_engine()
    snapshot = engine.export_stress_snapshot()
    snapshot["baseline_version"] = "VB-999"
    baseline = create_baseline_snapshot("bad", snapshot)
    with pytest.raises(StressBaselineError, match="inconsistent stress baseline version"):
        engine.compare_stress_baseline(baseline)


def test_report_generation():
    engine = create_enterprise_stress_test_engine()
    report = engine.generate_stress_report()
    assert report["module"] == "VB-005"
    assert report["report_type"] == "enterprise_stress_failure_testing"
    assert report["scenario_count"] == 6
    assert report["status"] == "passed"


def test_invalid_stress_scenario_rejection():
    with pytest.raises(StressScenarioDefinitionError, match="invalid stress scenario type"):
        StressScenarioDefinition("bad", "Bad", "unknown", {"units": 1})


def test_unsupported_failure_simulation_rejection():
    with pytest.raises(UnsupportedFailureSimulationError, match="unsupported failure simulation"):
        StressScenarioDefinition("bad-failure", "Bad failure", "dependency_failure", {"units": 1}, failure_mode="network_outage")


def test_malformed_workload_rejection():
    with pytest.raises(MalformedWorkloadError, match="non-empty mapping"):
        StressScenarioDefinition("bad-workload", "Bad workload", "repeated_execution", {})
    engine = create_enterprise_stress_test_engine()
    engine.register_stress_scenario(StressScenarioDefinition("bad-units", "Bad units", "repeated_execution", {"units": 0}))
    with pytest.raises(MalformedWorkloadError, match="positive integer"):
        engine.execute_stress_test("bad-units")


def test_integration_with_vb001_through_vb004_and_pi_modules():
    engine = create_enterprise_stress_test_engine()
    snapshot = engine.export_stress_snapshot()
    assert snapshot["module"] == "VB-005"
    assert snapshot["baseline_version"] == STRESS_BASELINE_VERSION
    assert snapshot["regression_summary"]["module"] == "VB-001"
    assert snapshot["quality_summary"]["module"] == "VB-002"
    assert snapshot["performance_summary"]["module"] == "VB-003"
    assert snapshot["governance_summary"]["module"] == "VB-004"
    assert snapshot["runtime_registry"]["module"] == "PI-002"
    assert snapshot["validation_phase_complete"] is True
