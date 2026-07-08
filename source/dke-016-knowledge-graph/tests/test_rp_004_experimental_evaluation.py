import pytest

from research_paper.benchmark_importer import REQUIRED_BENCHMARK_MODULES, import_benchmark_results, validate_benchmark_results
from research_paper.evaluation_errors import (
    DuplicateExperimentIdentifierError,
    FabricatedBenchmarkValueError,
    InconsistentExperimentMappingError,
    MalformedEvaluationRecordError,
    MissingBenchmarkMetadataError,
)
from research_paper.evaluation_manifest import EVALUATION_MANIFEST_VERSION, export_experiment_manifest
from research_paper.experiment_generator import (
    generate_evaluation_summary,
    generate_experiments,
    validate_experiments,
)
from research_paper.reproducibility_manager import generate_reproducibility_report, validate_reproducibility_report


def test_benchmark_import_covers_vb001_through_vb005():
    results = import_benchmark_results()
    assert results["module"] == "RP-004"
    assert results["status"] == "imported"
    assert results["benchmark_modules"] == REQUIRED_BENCHMARK_MODULES
    assert tuple(record["source_module"] for record in results["benchmarks"]) == REQUIRED_BENCHMARK_MODULES
    assert all(record["fabricated_results"] is False for record in results["benchmarks"])


def test_benchmark_import_uses_real_validation_snapshots():
    results = import_benchmark_results()
    records = {record["benchmark_id"]: record for record in results["benchmarks"]}
    assert records["VB-001"]["summary"]["workflow_count"] == 4
    assert records["VB-002"]["summary"]["benchmark_count"] == 1
    assert records["VB-003"]["summary"]["benchmark_count"] == 3
    assert records["VB-004"]["summary"]["rule_count"] == 6
    assert records["VB-005"]["summary"]["scenario_count"] == 6
    assert records["VB-001"]["raw_snapshot"]["runtime_registry"]["module"] == "PI-002"


def test_deterministic_experiment_generation():
    first = generate_experiments()
    second = generate_experiments()
    assert first == second
    assert first["experiment_catalog"]["experiment_count"] == 5
    assert first["experiment_catalog"]["experiment_ids"][0] == "EXP-001-VB-001"
    assert first["markdown"].startswith("# Experimental Evaluation And Reproducibility")


def test_reproducibility_report_generation():
    experiments = generate_experiments()
    report = generate_reproducibility_report(import_benchmark_results(), experiments)
    assert report["status"] == "generated"
    assert len(report["checklist"]) == 5
    assert report["artifact_inventory"]["artifact_count"] == 5
    assert report["commands"] == ("python -m pytest", "npm run test")
    assert report["fabricated_results"] is False
    assert all(item["external_service_required"] is False for item in report["checklist"])


def test_benchmark_traceability_and_evaluation_summary():
    experiments = generate_experiments()
    summary = generate_evaluation_summary(experiments)
    assert summary["experiment_count"] == 5
    assert summary["benchmark_modules"] == REQUIRED_BENCHMARK_MODULES
    assert summary["artifact_count"] == 5
    assert summary["fabricated_results"] is False


def test_manifest_generation_integrates_rp_vb_and_doc_traces():
    manifest = export_experiment_manifest()
    assert manifest["module"] == "RP-004"
    assert manifest["manifest_version"] == EVALUATION_MANIFEST_VERSION
    assert manifest["rp_trace"] == {
        "RP-001": "RP-001",
        "RP-002": "RP-002",
        "RP-003": "RP-003",
        "RP-004": "RP-004",
    }
    assert manifest["documentation_trace"]["DOC-001"] == "DOC-001"
    assert manifest["documentation_trace"]["DOC-005"] == "DOC-005"
    assert manifest["validation_trace"]["VB-001"] == "VB-001"
    assert manifest["validation_trace"]["VB-005"] == "VB-005"
    assert manifest["integrity"]["benchmark_values_fabricated"] is False
    assert manifest["integrity"]["external_benchmark_services_required"] is False


def test_duplicate_experiment_identifier_rejection():
    experiments = generate_experiments()
    duplicate = {
        **experiments,
        "experiments": (
            experiments["experiments"][0],
            experiments["experiments"][0],
            *experiments["experiments"][2:],
        ),
    }
    with pytest.raises(DuplicateExperimentIdentifierError, match="duplicate experiment identifiers"):
        validate_experiments(duplicate)


def test_fabricated_benchmark_value_rejection():
    results = import_benchmark_results()
    malformed = {
        **results,
        "benchmarks": (
            {**results["benchmarks"][0], "fabricated_results": True},
            *results["benchmarks"][1:],
        ),
    }
    with pytest.raises(FabricatedBenchmarkValueError, match="fabricated benchmark values"):
        validate_benchmark_results(malformed)


def test_missing_benchmark_metadata_rejection():
    results = import_benchmark_results()
    malformed_record = dict(results["benchmarks"][0])
    del malformed_record["summary"]
    malformed = {**results, "benchmarks": (malformed_record, *results["benchmarks"][1:])}
    with pytest.raises(MissingBenchmarkMetadataError, match="missing benchmark metadata"):
        validate_benchmark_results(malformed)


def test_malformed_experiment_record_rejection():
    experiments = generate_experiments()
    malformed = {
        **experiments,
        "experiments": (
            {**experiments["experiments"][0], "source_summary": {}},
            *experiments["experiments"][1:],
        ),
    }
    with pytest.raises(MalformedEvaluationRecordError, match="malformed experiment record"):
        validate_experiments(malformed)


def test_inconsistent_experiment_mapping_rejection():
    experiments = generate_experiments()
    malformed = {**experiments, "experiments": experiments["experiments"][1:]}
    with pytest.raises(InconsistentExperimentMappingError, match="every VB benchmark"):
        validate_experiments(malformed)


def test_reproducibility_mapping_rejection():
    report = generate_reproducibility_report()
    malformed = {**report, "checklist": report["checklist"][1:]}
    with pytest.raises(InconsistentExperimentMappingError, match="cover every VB benchmark"):
        validate_reproducibility_report(malformed)
