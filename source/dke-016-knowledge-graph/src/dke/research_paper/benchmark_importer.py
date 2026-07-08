from __future__ import annotations

from copy import deepcopy
from typing import Any

from validation import (
    create_decision_quality_benchmark_suite,
    create_enterprise_stress_test_engine,
    create_governance_validation_framework,
    create_performance_benchmark_harness,
    create_regression_validator,
)

from .evaluation_errors import (
    FabricatedBenchmarkValueError,
    MissingBenchmarkMetadataError,
)

BENCHMARK_IMPORT_VERSION = "RP-004.1"
REQUIRED_BENCHMARK_MODULES = ("VB-001", "VB-002", "VB-003", "VB-004", "VB-005")

_BENCHMARK_RESULT_CACHE: dict[str, Any] | None = None


def import_benchmark_results() -> dict[str, Any]:
    global _BENCHMARK_RESULT_CACHE
    if _BENCHMARK_RESULT_CACHE is None:
        _BENCHMARK_RESULT_CACHE = _build_benchmark_results()
    return deepcopy(_BENCHMARK_RESULT_CACHE)


def validate_benchmark_results(results: dict[str, Any]) -> dict[str, Any]:
    records = tuple(results.get("benchmarks", ()))
    module_ids = tuple(record.get("benchmark_id") for record in records)
    if module_ids != REQUIRED_BENCHMARK_MODULES:
        raise MissingBenchmarkMetadataError("benchmark import must cover VB-001 through VB-005 in order")
    for record in records:
        required = ("benchmark_id", "name", "source_module", "status", "artifact_type", "summary", "raw_snapshot")
        missing = tuple(field for field in required if field not in record or record[field] in ("", None))
        if missing:
            raise MissingBenchmarkMetadataError(f"missing benchmark metadata for {record.get('benchmark_id')}: {missing}")
        if record.get("fabricated_results") is not False:
            raise FabricatedBenchmarkValueError(f"fabricated benchmark values are not allowed: {record['benchmark_id']}")
        if record["raw_snapshot"].get("module") != record["source_module"]:
            raise MissingBenchmarkMetadataError(f"benchmark snapshot module mismatch: {record['benchmark_id']}")
    return {
        "module": "RP-004",
        "status": "valid",
        "benchmark_count": len(records),
        "benchmark_modules": module_ids,
    }


def _build_benchmark_results() -> dict[str, Any]:
    vb001 = create_regression_validator().export_regression_snapshot()
    vb002 = create_decision_quality_benchmark_suite().export_benchmark_snapshot()
    vb003 = create_performance_benchmark_harness("quick").export_performance_snapshot()
    vb004 = create_governance_validation_framework().export_governance_snapshot()
    vb005 = create_enterprise_stress_test_engine().export_stress_snapshot()
    records = (
        _record(
            "VB-001",
            "End-to-End Regression Validator",
            "regression_snapshot",
            vb001,
            {
                "status": vb001["status"],
                "workflow_count": vb001["report"]["workflow_count"],
                "runtime_component_count": vb001["runtime_registry"]["component_count"],
            },
        ),
        _record(
            "VB-002",
            "Decision Quality Benchmark Suite",
            "benchmark_snapshot",
            vb002,
            {
                "status": vb002["status"],
                "benchmark_count": vb002["registry"]["benchmark_count"],
                "scorecard_count": len(vb002["scorecards"]),
            },
        ),
        _record(
            "VB-003",
            "Performance Benchmark Harness",
            "performance_snapshot",
            vb003,
                {
                    "status": vb003["status"],
                    "benchmark_count": vb003["registry"]["benchmark_count"],
                    "scorecard_count": vb003["report"]["benchmark_count"],
                    "profile": vb003["profile"]["profile_id"],
                },
            ),
        _record(
            "VB-004",
            "Governance And Provenance Validation",
            "governance_snapshot",
            vb004,
                {
                    "status": vb004["status"],
                    "policy_id": vb004["policy"]["policy_id"],
                    "rule_count": len(vb004["report"]["scorecard"]["rule_results"]),
                },
            ),
        _record(
            "VB-005",
            "Enterprise Stress And Failure Testing",
            "stress_snapshot",
            vb005,
                {
                    "status": vb005["status"],
                    "scenario_count": len(vb005["scenarios"]),
                    "scorecard_count": vb005["report"]["scenario_count"],
                },
            ),
    )
    results = {
        "module": "RP-004",
        "import_version": BENCHMARK_IMPORT_VERSION,
        "status": "imported",
        "benchmarks": records,
        "benchmark_modules": tuple(record["benchmark_id"] for record in records),
        "external_benchmark_services_required": False,
        "fabricated_results": False,
    }
    validate_benchmark_results(results)
    return results


def _record(
    benchmark_id: str,
    name: str,
    artifact_type: str,
    raw_snapshot: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "benchmark_id": benchmark_id,
        "name": name,
        "source_module": raw_snapshot["module"],
        "status": raw_snapshot["status"],
        "artifact_type": artifact_type,
        "summary": summary,
        "raw_snapshot": raw_snapshot,
        "fabricated_results": False,
    }
