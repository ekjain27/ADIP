from __future__ import annotations

from typing import Any

from .benchmark_importer import REQUIRED_BENCHMARK_MODULES, import_benchmark_results, validate_benchmark_results
from .evaluation_errors import (
    DuplicateExperimentIdentifierError,
    FabricatedBenchmarkValueError,
    InconsistentExperimentMappingError,
    MalformedEvaluationRecordError,
)
from .reproducibility_manager import generate_artifact_inventory, generate_reproducibility_report

EXPERIMENT_VERSION = "RP-004.1"


def generate_experiments(benchmark_results: dict[str, Any] | None = None) -> dict[str, Any]:
    active_results = benchmark_results or import_benchmark_results()
    validate_benchmark_results(active_results)
    experiments = tuple(_experiment_record(index, record) for index, record in enumerate(active_results["benchmarks"], start=1))
    evaluation = {
        "module": "RP-004",
        "experiment_version": EXPERIMENT_VERSION,
        "status": "generated",
        "experiment_catalog": {
            "catalog_type": "experimental_evaluation_catalog",
            "experiment_count": len(experiments),
            "experiment_ids": tuple(experiment["experiment_id"] for experiment in experiments),
        },
        "experiments": experiments,
        "benchmark_index": generate_benchmark_index(active_results),
        "evaluation_methodology": _evaluation_methodology(),
        "threats_to_validity": _threats_to_validity(),
        "limitations": _limitations(),
        "artifact_inventory": generate_artifact_inventory(active_results),
        "markdown": _markdown_experiments(experiments),
        "integrity": {
            "benchmark_values_fabricated": False,
            "statistical_analyses_fabricated": False,
            "external_benchmark_services_required": False,
        },
    }
    validate_experiments(evaluation)
    return evaluation


def generate_evaluation_summary(experiments: dict[str, Any] | None = None) -> dict[str, Any]:
    active = experiments or generate_experiments()
    validate_experiments(active)
    statuses = tuple(experiment["benchmark_status"] for experiment in active["experiments"])
    return {
        "module": "RP-004",
        "summary_type": "evaluation_summary",
        "status": "generated",
        "experiment_count": active["experiment_catalog"]["experiment_count"],
        "benchmark_modules": tuple(experiment["benchmark_id"] for experiment in active["experiments"]),
        "all_benchmarks_passed": all(status == "passed" for status in statuses),
        "artifact_count": active["artifact_inventory"]["artifact_count"],
        "fabricated_results": False,
    }


def generate_benchmark_index(benchmark_results: dict[str, Any] | None = None) -> dict[str, Any]:
    active_results = benchmark_results or import_benchmark_results()
    validate_benchmark_results(active_results)
    entries = tuple(
        {
            "benchmark_id": record["benchmark_id"],
            "name": record["name"],
            "source_module": record["source_module"],
            "artifact_type": record["artifact_type"],
            "status": record["status"],
            "summary_keys": tuple(sorted(record["summary"])),
        }
        for record in active_results["benchmarks"]
    )
    return {
        "index_version": EXPERIMENT_VERSION,
        "benchmark_count": len(entries),
        "entries": entries,
    }


def validate_experiments(evaluation: dict[str, Any]) -> dict[str, Any]:
    experiments = tuple(evaluation.get("experiments", ()))
    experiment_ids = tuple(experiment.get("experiment_id") for experiment in experiments)
    if len(experiment_ids) != len(set(experiment_ids)):
        raise DuplicateExperimentIdentifierError("duplicate experiment identifiers are not allowed")
    benchmark_ids = tuple(experiment.get("benchmark_id") for experiment in experiments)
    if benchmark_ids != REQUIRED_BENCHMARK_MODULES:
        raise InconsistentExperimentMappingError("experiments must reference every VB benchmark in deterministic order")
    for experiment in experiments:
        required = (
            "experiment_id",
            "benchmark_id",
            "title",
            "description",
            "benchmark_status",
            "source_artifact_type",
            "source_summary",
            "raw_snapshot_module",
        )
        missing = tuple(field for field in required if field not in experiment or experiment[field] in ("", None))
        if missing:
            raise MalformedEvaluationRecordError(f"malformed experiment record {experiment.get('experiment_id')}: {missing}")
        if not experiment["source_summary"]:
            raise MalformedEvaluationRecordError(
                f"malformed experiment record {experiment.get('experiment_id')}: empty source_summary"
            )
        if experiment.get("fabricated_results") is not False:
            raise FabricatedBenchmarkValueError(f"fabricated experiment values are not allowed: {experiment['experiment_id']}")
        if experiment["raw_snapshot_module"] != experiment["benchmark_id"]:
            raise InconsistentExperimentMappingError(f"experiment source mismatch: {experiment['experiment_id']}")
    return {
        "module": "RP-004",
        "status": "valid",
        "experiment_count": len(experiments),
        "benchmark_modules": benchmark_ids,
    }


def _experiment_record(index: int, benchmark: dict[str, Any]) -> dict[str, Any]:
    return {
        "experiment_id": f"EXP-{index:03d}-{benchmark['benchmark_id']}",
        "benchmark_id": benchmark["benchmark_id"],
        "title": benchmark["name"],
        "description": f"Publication artifact generated from {benchmark['artifact_type']} exported by {benchmark['source_module']}.",
        "benchmark_status": benchmark["status"],
        "source_artifact_type": benchmark["artifact_type"],
        "source_summary": benchmark["summary"],
        "raw_snapshot_module": benchmark["raw_snapshot"]["module"],
        "reproducibility_notes": (
            "Uses repository-local deterministic validation outputs.",
            "Does not introduce new numerical values beyond the imported VB snapshot.",
        ),
        "fabricated_results": False,
    }


def _evaluation_methodology() -> dict[str, Any]:
    return {
        "methodology_type": "validation_snapshot_synthesis",
        "description": "Each experiment is generated from an exported VB validation or benchmark snapshot.",
        "data_sources": REQUIRED_BENCHMARK_MODULES,
        "external_services_required": False,
        "statistical_analysis_added": False,
    }


def _threats_to_validity() -> tuple[dict[str, str], ...]:
    return (
        {
            "threat_id": "construct_validity",
            "description": "Evaluation reflects implemented validation metrics and may not cover metrics not represented by VB modules.",
            "mitigation": "Every claim is tied to a VB snapshot and unsupported analyses are omitted.",
        },
        {
            "threat_id": "external_validity",
            "description": "Benchmarks are deterministic repository-local workflows rather than external production traffic.",
            "mitigation": "The artifact reports this scope as a limitation and does not generalize beyond implemented tests.",
        },
        {
            "threat_id": "conclusion_validity",
            "description": "No additional statistical inference is performed by RP-004.",
            "mitigation": "Publication text distinguishes validation summaries from statistical claims.",
        },
    )


def _limitations() -> tuple[str, ...]:
    return (
        "No new numerical results are invented by the evaluation framework.",
        "No statistical analyses are introduced beyond data already exported by VB modules.",
        "Evaluation depends on deterministic repository-local validation artifacts.",
        "External benchmark services are not required or queried.",
    )


def _markdown_experiments(experiments: tuple[dict[str, Any], ...]) -> str:
    lines = [
        "# Experimental Evaluation And Reproducibility",
        "",
        "## Evaluation Methodology",
        "Experiments are generated from repository-local VB validation snapshots. No external benchmark service is required.",
        "",
        "## Experiment Catalog",
    ]
    for experiment in experiments:
        lines.append(f"- {experiment['experiment_id']}: {experiment['title']} ({experiment['benchmark_status']})")
    lines.extend(
        [
            "",
            "## Reproducibility",
            "Each experiment retains its source benchmark module, artifact type, summary metadata, and raw validation snapshot.",
            "",
            "## Limitations",
        ]
    )
    lines.extend(f"- {item}" for item in _limitations())
    return "\n".join(lines) + "\n"
