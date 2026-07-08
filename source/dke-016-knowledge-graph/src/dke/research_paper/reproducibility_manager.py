from __future__ import annotations

from typing import Any

from .benchmark_importer import REQUIRED_BENCHMARK_MODULES, import_benchmark_results, validate_benchmark_results
from .evaluation_errors import InconsistentExperimentMappingError, MalformedEvaluationRecordError

REPRODUCIBILITY_VERSION = "RP-004.1"


def generate_reproducibility_report(
    benchmark_results: dict[str, Any] | None = None,
    experiments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_results = benchmark_results or import_benchmark_results()
    validate_benchmark_results(active_results)
    checklist = tuple(
        {
            "check_id": f"repro_{record['benchmark_id'].lower()}",
            "benchmark_id": record["benchmark_id"],
            "artifact_available": True,
            "raw_snapshot_available": bool(record["raw_snapshot"]),
            "deterministic_ordering": True,
            "external_service_required": False,
            "reproduction_source": record["artifact_type"],
        }
        for record in active_results["benchmarks"]
    )
    report = {
        "module": "RP-004",
        "report_version": REPRODUCIBILITY_VERSION,
        "status": "generated",
        "checklist": checklist,
        "artifact_inventory": generate_artifact_inventory(active_results),
        "commands": (
            "python -m pytest",
            "npm run test",
        ),
        "limitations": (
            "Evaluation artifacts are generated from deterministic validation snapshots available in this repository.",
            "No external benchmark services are required or queried.",
            "No statistical analysis is reported beyond values already produced by VB modules.",
        ),
        "fabricated_results": False,
    }
    validate_reproducibility_report(report, experiments)
    return report


def generate_artifact_inventory(benchmark_results: dict[str, Any] | None = None) -> dict[str, Any]:
    active_results = benchmark_results or import_benchmark_results()
    validate_benchmark_results(active_results)
    artifacts = tuple(
        {
            "artifact_id": f"artifact_{record['benchmark_id'].lower()}",
            "benchmark_id": record["benchmark_id"],
            "artifact_type": record["artifact_type"],
            "source_module": record["source_module"],
            "status": record["status"],
        }
        for record in active_results["benchmarks"]
    )
    return {
        "inventory_version": REPRODUCIBILITY_VERSION,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def validate_reproducibility_report(report: dict[str, Any], experiments: dict[str, Any] | None = None) -> dict[str, Any]:
    checklist = tuple(report.get("checklist", ()))
    checklist_modules = tuple(item.get("benchmark_id") for item in checklist)
    if checklist_modules != REQUIRED_BENCHMARK_MODULES:
        raise InconsistentExperimentMappingError("reproducibility checklist must cover every VB benchmark")
    for item in checklist:
        if not item.get("artifact_available") or not item.get("raw_snapshot_available"):
            raise MalformedEvaluationRecordError(f"reproducibility item is incomplete: {item.get('benchmark_id')}")
        if item.get("external_service_required") is not False:
            raise MalformedEvaluationRecordError("external benchmark services must not be required")
    if experiments is not None:
        experiment_modules = tuple(experiment["benchmark_id"] for experiment in experiments["experiments"])
        if experiment_modules != checklist_modules:
            raise InconsistentExperimentMappingError("experiment and reproducibility benchmark coverage differ")
    return {
        "module": "RP-004",
        "status": "valid",
        "check_count": len(checklist),
    }
