import pytest

from validation import (
    BenchmarkBaselineMismatchError,
    BenchmarkDefinition,
    BenchmarkDefinitionError,
    BenchmarkInputError,
    BenchmarkProfileError,
    DuplicateBenchmarkError,
    MissingBenchmarkMetricError,
    QUALITY_METRICS,
    create_baseline_snapshot,
    create_decision_quality_benchmark_suite,
    create_weighted_profile,
)


def test_benchmark_registration():
    suite = create_decision_quality_benchmark_suite()
    benchmark = BenchmarkDefinition("custom", "Custom benchmark", {"query": "quality"})
    suite.register_benchmark(benchmark)
    assert suite.registry.get_benchmark("custom") == benchmark


def test_duplicate_benchmark_rejection():
    suite = create_decision_quality_benchmark_suite()
    duplicate = BenchmarkDefinition("decision-quality-default", "Duplicate", {"query": "quality"})
    with pytest.raises(DuplicateBenchmarkError, match="already registered"):
        suite.register_benchmark(duplicate)


def test_deterministic_scoring():
    suite = create_decision_quality_benchmark_suite()
    first = suite.execute_benchmark("decision-quality-default")
    second = suite.execute_benchmark("decision-quality-default")
    assert first == second
    assert first["status"] == "passed"
    assert first["weighted_score"] == 1.0


def test_weighted_profile_evaluation():
    weights = {metric: 1.0 for metric in QUALITY_METRICS}
    weights["governance_compliance"] = 3.0
    profile = create_weighted_profile("governance-heavy", weights)
    suite = create_decision_quality_benchmark_suite(profile=profile)
    scorecard = suite.execute_benchmark("decision-quality-default")
    assert scorecard["profile_id"] == "governance-heavy"
    assert scorecard["weighted_score"] == 1.0


def test_baseline_comparison():
    suite = create_decision_quality_benchmark_suite()
    snapshot = suite.export_benchmark_snapshot()
    baseline = create_baseline_snapshot("benchmark-baseline", snapshot)
    assert suite.compare_to_baseline(baseline) == {"status": "matched", "snapshot_id": "benchmark-baseline"}


def test_baseline_mismatch_rejected():
    suite = create_decision_quality_benchmark_suite()
    baseline = create_baseline_snapshot("bad", {"module": "VB-002", "status": "failed"})
    with pytest.raises(BenchmarkBaselineMismatchError, match="snapshot mismatch"):
        suite.compare_to_baseline(baseline)


def test_scorecard_generation():
    suite = create_decision_quality_benchmark_suite()
    scorecard = suite.generate_scorecard("decision-quality-default")
    assert scorecard["benchmark_id"] == "decision-quality-default"
    assert tuple(metric for metric, _ in scorecard["metrics"]) == QUALITY_METRICS


def test_invalid_profile_rejection():
    weights = {metric: 1.0 for metric in QUALITY_METRICS if metric != "robustness"}
    profile = create_weighted_profile("missing", weights)
    with pytest.raises(MissingBenchmarkMetricError, match="missing benchmark metric"):
        create_decision_quality_benchmark_suite(profile=profile)


def test_incompatible_scoring_profile_rejection():
    weights = {metric: 1.0 for metric in QUALITY_METRICS}
    weights["robustness"] = -1.0
    profile = create_weighted_profile("bad", weights)
    with pytest.raises(BenchmarkProfileError, match="invalid benchmark metric weight"):
        create_decision_quality_benchmark_suite(profile=profile)


def test_malformed_input_rejection():
    suite = create_decision_quality_benchmark_suite()
    with pytest.raises(BenchmarkInputError, match="non-empty mapping"):
        suite.evaluate_decision_quality({})
    with pytest.raises(BenchmarkDefinitionError, match="decision_input is required"):
        BenchmarkDefinition("bad", "Bad", {})


def test_integration_with_vb001_and_pi_layers():
    suite = create_decision_quality_benchmark_suite()
    snapshot = suite.export_benchmark_snapshot()
    assert snapshot["regression_summary"]["module"] == "VB-001"
    assert snapshot["runtime_registry"]["module"] == "PI-002"
    assert snapshot["summary"]["status"] == "passed"
