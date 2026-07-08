import pytest

from validation import (
    DuplicatePerformanceBenchmarkError,
    InvalidPerformanceProfileError,
    PERFORMANCE_BASELINE_VERSION,
    PerformanceBaselineError,
    PerformanceBenchmarkDefinition,
    PerformanceBenchmarkDefinitionError,
    UnsupportedPerformanceMetricError,
    create_baseline_snapshot,
    create_performance_benchmark_harness,
)


def test_performance_benchmark_registration():
    harness = create_performance_benchmark_harness("quick")
    benchmark = PerformanceBenchmarkDefinition(
        benchmark_id="component-dke",
        name="DKE component benchmark",
        target_type="platform_component",
        target="DKE",
        payload={"query": "measure dke"},
    )
    harness.register_performance_benchmark(benchmark)
    assert harness.registry.get_performance_benchmark("component-dke") == benchmark


def test_duplicate_performance_benchmark_rejection():
    harness = create_performance_benchmark_harness()
    duplicate = PerformanceBenchmarkDefinition(
        benchmark_id="platform-component-die",
        name="Duplicate",
        target_type="platform_component",
        target="DIE",
        payload={"query": "duplicate"},
    )
    with pytest.raises(DuplicatePerformanceBenchmarkError, match="already registered"):
        harness.register_performance_benchmark(duplicate)


def test_deterministic_metric_collection():
    harness = create_performance_benchmark_harness("standard")
    first = harness.execute_performance_benchmark("platform-component-die")
    second = harness.execute_performance_benchmark("platform-component-die")
    assert first == second
    assert first["status"] == "passed"
    assert dict(first["metrics"])["operation_counts"] > 0


def test_profile_selection():
    quick = create_performance_benchmark_harness("quick").execute_performance_benchmark("platform-component-die")
    comprehensive = create_performance_benchmark_harness("comprehensive").execute_performance_benchmark("platform-component-die")
    assert quick["profile_id"] == "quick"
    assert comprehensive["profile_id"] == "comprehensive"
    assert dict(comprehensive["metrics"])["operation_counts"] > dict(quick["metrics"])["operation_counts"]


def test_baseline_comparison():
    harness = create_performance_benchmark_harness("quick")
    snapshot = harness.export_performance_snapshot()
    baseline = create_baseline_snapshot("performance-baseline", snapshot)
    assert harness.compare_performance_baseline(baseline) == {
        "status": "matched",
        "snapshot_id": "performance-baseline",
    }


def test_incompatible_baseline_version_rejected():
    harness = create_performance_benchmark_harness("quick")
    snapshot = harness.export_performance_snapshot()
    snapshot["baseline_version"] = "VB-999"
    baseline = create_baseline_snapshot("bad-version", snapshot)
    with pytest.raises(PerformanceBaselineError, match="incompatible performance baseline version"):
        harness.compare_performance_baseline(baseline)


def test_report_generation():
    harness = create_performance_benchmark_harness("standard")
    report = harness.generate_performance_report()
    assert report["module"] == "VB-003"
    assert report["report_type"] == "performance_benchmark"
    assert report["benchmark_count"] == 3


def test_invalid_profile_rejection():
    with pytest.raises(InvalidPerformanceProfileError, match="invalid performance benchmark profile"):
        create_performance_benchmark_harness("invalid")


def test_malformed_benchmark_rejection():
    with pytest.raises(PerformanceBenchmarkDefinitionError, match="payload is required"):
        PerformanceBenchmarkDefinition(
            benchmark_id="bad",
            name="Bad",
            target_type="workflow",
            target="complete_platform_pipeline",
            payload={},
        )


def test_unsupported_metric_rejection():
    with pytest.raises(UnsupportedPerformanceMetricError, match="unsupported performance metric"):
        PerformanceBenchmarkDefinition(
            benchmark_id="bad-metric",
            name="Bad metric",
            target_type="workflow",
            target="complete_platform_pipeline",
            payload={"query": "bad metric"},
            metrics=("execution_time", "cpu_cycles"),
        )


def test_integration_with_vb001_vb002_and_pi_modules():
    harness = create_performance_benchmark_harness("quick")
    snapshot = harness.export_performance_snapshot()
    assert snapshot["module"] == "VB-003"
    assert snapshot["baseline_version"] == PERFORMANCE_BASELINE_VERSION
    assert snapshot["regression_summary"]["module"] == "VB-001"
    assert snapshot["quality_summary"]["module"] == "VB-002"
    assert snapshot["runtime_registry"]["module"] == "PI-002"
    assert snapshot["deployment_snapshot"]["module"] == "PI-008"
