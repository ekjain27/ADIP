import pytest

from validation import (
    GOVERNANCE_BASELINE_VERSION,
    GovernanceBaselineError,
    GovernancePolicyError,
    GovernancePolicyViolationError,
    GovernanceValidationPolicy,
    LineageConsistencyError,
    ProvenanceIntegrityError,
    UnsupportedGovernanceRuleError,
    create_baseline_snapshot,
    create_governance_validation_framework,
    validate_governance_policy,
)


def test_governance_policy_validation():
    policy = GovernanceValidationPolicy("policy")
    result = validate_governance_policy(policy)
    assert result["status"] == "valid"
    assert result["rule_count"] == 6


def test_malformed_policy_rejection():
    with pytest.raises(GovernancePolicyError, match="policy_id is required"):
        validate_governance_policy(GovernanceValidationPolicy(""))


def test_unsupported_rule_rejection():
    policy = GovernanceValidationPolicy("bad", ("unknown_rule",))
    with pytest.raises(UnsupportedGovernanceRuleError, match="unsupported governance rule"):
        validate_governance_policy(policy)


def test_provenance_integrity_checks():
    framework = create_governance_validation_framework()
    result = framework.validate_provenance()
    assert result["status"] == "valid"
    assert result["validator"] == "DPG"
    assert result["provenance"] == "linked"


def test_lineage_validation():
    framework = create_governance_validation_framework()
    result = framework.validate_lineage()
    assert result["status"] == "valid"
    assert result["validator"] == "TDLL"
    assert result["lineage"] == "tracked"


def test_deterministic_reporting():
    framework = create_governance_validation_framework()
    first = framework.execute_governance_validation()
    second = framework.execute_governance_validation()
    assert first == second
    assert first["status"] == "passed"
    assert first["scorecard"]["score"] == 1.0


def test_policy_violation_detection():
    framework = create_governance_validation_framework()
    with pytest.raises(GovernancePolicyViolationError, match="governance policy violation"):
        framework.validate_governance({"decision": "approve", "provenance": "linked", "lineage": "tracked"})


def test_missing_provenance_link_rejected():
    framework = create_governance_validation_framework()
    with pytest.raises(ProvenanceIntegrityError, match="missing provenance link"):
        framework.validate_provenance({"decision": "approve", "governance": "compliant", "lineage": "tracked"})


def test_broken_lineage_chain_rejected():
    framework = create_governance_validation_framework()
    with pytest.raises(LineageConsistencyError, match="broken lineage chain"):
        framework.validate_lineage({"decision": "approve", "provenance": "linked", "governance": "compliant"})


def test_baseline_comparison():
    framework = create_governance_validation_framework()
    snapshot = framework.export_governance_snapshot()
    baseline = create_baseline_snapshot("governance-baseline", snapshot)
    assert framework.compare_governance_baseline(baseline) == {
        "status": "matched",
        "snapshot_id": "governance-baseline",
    }


def test_incompatible_governance_baseline_rejected():
    framework = create_governance_validation_framework()
    snapshot = framework.export_governance_snapshot()
    snapshot["baseline_version"] = "VB-999"
    baseline = create_baseline_snapshot("bad", snapshot)
    with pytest.raises(GovernanceBaselineError, match="incompatible governance baseline version"):
        framework.compare_governance_baseline(baseline)


def test_report_generation_and_integrations():
    framework = create_governance_validation_framework()
    snapshot = framework.export_governance_snapshot()
    assert snapshot["module"] == "VB-004"
    assert snapshot["baseline_version"] == GOVERNANCE_BASELINE_VERSION
    assert snapshot["regression_summary"]["module"] == "VB-001"
    assert snapshot["quality_summary"]["module"] == "VB-002"
    assert snapshot["performance_summary"]["module"] == "VB-003"
    assert snapshot["runtime_registry"]["module"] == "PI-002"
