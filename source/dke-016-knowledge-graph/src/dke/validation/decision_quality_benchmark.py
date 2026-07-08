from __future__ import annotations

from typing import Any, Mapping

from platform_integration import PlatformIntegrationLayer, UnifiedPlatformRuntimeRegistry, create_runtime_registry_from_platform_layer

from .baseline_snapshot import BaselineSnapshot, compare_snapshots, create_baseline_snapshot
from .benchmark_errors import BenchmarkBaselineMismatchError, BenchmarkInputError, MissingBenchmarkMetricError
from .benchmark_profiles import BenchmarkProfile, QUALITY_METRICS, create_equal_weight_profile, validate_profile
from .benchmark_registry import BenchmarkDefinition, BenchmarkRegistry
from .benchmark_scorecard import BenchmarkScorecard, generate_scorecard, summarize_scorecards
from .regression_validator import EndToEndRegressionValidator, create_regression_validator
from .workflow_runner import create_validation_platform_layer


class DecisionQualityBenchmarkSuite:
    MODULE = "VB-002"

    def __init__(
        self,
        regression_validator: EndToEndRegressionValidator | None = None,
        platform_layer: PlatformIntegrationLayer | None = None,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
        profile: BenchmarkProfile | None = None,
    ) -> None:
        self.regression_validator = regression_validator or create_regression_validator()
        self.platform_layer = platform_layer or self.regression_validator.platform_layer or create_validation_platform_layer()
        self.runtime_registry = runtime_registry or create_runtime_registry_from_platform_layer(self.platform_layer)
        self.profile = profile or create_equal_weight_profile()
        validate_profile(self.profile)
        self.registry = BenchmarkRegistry()
        self._last_scorecards: tuple[BenchmarkScorecard, ...] = ()

    def register_benchmark(self, benchmark: BenchmarkDefinition) -> BenchmarkDefinition:
        return self.registry.register_benchmark(benchmark)

    def execute_benchmark(self, benchmark_id: str, profile: BenchmarkProfile | None = None) -> dict[str, Any]:
        benchmark = self.registry.get_benchmark(benchmark_id)
        active_profile = profile or self.profile
        validate_profile(active_profile)
        decision_output = self._execute_decision(benchmark.decision_input)
        metrics = self.evaluate_decision_quality(decision_output, benchmark)
        diagnostics = self._diagnostics(metrics)
        scorecard = generate_scorecard(benchmark.benchmark_id, active_profile, metrics, decision_output, diagnostics)
        self._last_scorecards = tuple(sorted((*self._last_scorecards, scorecard), key=lambda item: item.benchmark_id))
        return scorecard.to_dict()

    def evaluate_decision_quality(self, decision_output: Mapping[str, Any], benchmark: BenchmarkDefinition | None = None) -> dict[str, float]:
        if not isinstance(decision_output, Mapping) or not decision_output:
            raise BenchmarkInputError("decision output must be a non-empty mapping")
        definition = benchmark or BenchmarkDefinition(
            benchmark_id="ad-hoc",
            name="Ad hoc decision quality evaluation",
            decision_input={"query": "ad hoc"},
        )
        metrics = {
            "completeness": self._score_presence(decision_output, definition.required_fields),
            "consistency": self._score_consistency(decision_output),
            "constraint_satisfaction": self._score_constraints(decision_output, definition.expected_constraints),
            "explainability_coverage": self._score_any(decision_output, ("reason", "explanation", "evidence_count", "recommendation")),
            "provenance_completeness": self._score_any(decision_output, ("provenance", "lineage")),
            "governance_compliance": 1.0 if decision_output.get("governance") == "compliant" else 0.0,
            "robustness": self._score_robustness(decision_output),
        }
        missing = tuple(metric for metric in QUALITY_METRICS if metric not in metrics)
        if missing:
            raise MissingBenchmarkMetricError(f"missing benchmark metric(s): {', '.join(missing)}")
        return {metric: round(metrics[metric], 6) for metric in QUALITY_METRICS}

    def compare_to_baseline(self, baseline: BaselineSnapshot | None = None) -> dict[str, Any]:
        snapshot = self.export_benchmark_snapshot()
        expected = baseline or create_baseline_snapshot("vb-002-current", snapshot)
        try:
            return compare_snapshots(snapshot, expected)
        except Exception as exc:
            raise BenchmarkBaselineMismatchError(str(exc)) from exc

    def generate_scorecard(self, benchmark_id: str, profile: BenchmarkProfile | None = None) -> dict[str, Any]:
        return self.execute_benchmark(benchmark_id, profile)

    def export_benchmark_snapshot(self) -> dict[str, Any]:
        scorecards = self._scorecards_for_snapshot()
        return {
            "module": self.MODULE,
            "status": "passed" if all(scorecard.status == "passed" for scorecard in scorecards) else "failed",
            "profile": self.profile.snapshot(),
            "registry": self.registry.export_registry_snapshot(),
            "runtime_registry": self.runtime_registry.export_registry_snapshot(),
            "regression_summary": self.regression_validator.summarize_results(),
            "scorecards": tuple(scorecard.to_dict() for scorecard in scorecards),
            "summary": summarize_scorecards(scorecards),
        }

    def summarize_results(self) -> dict[str, Any]:
        return summarize_scorecards(self._scorecards_for_snapshot())

    def _execute_decision(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping) or not payload:
            raise BenchmarkInputError("benchmark decision input must be a non-empty mapping")
        input_payload = dict(payload)
        if "query" not in input_payload:
            raise BenchmarkInputError("benchmark decision input requires query")
        result = self.platform_layer.execute_pipeline(("DKE", "DIE", "DPG", "DDGM", "TDLL", "DRIF"), input_payload)
        return dict(result.output_payload)

    def _scorecards_for_snapshot(self) -> tuple[BenchmarkScorecard, ...]:
        if not self._last_scorecards:
            for benchmark in self.registry.list_benchmarks():
                self.execute_benchmark(benchmark.benchmark_id)
        return tuple(sorted(self._last_scorecards, key=lambda item: item.benchmark_id))

    def _diagnostics(self, metrics: Mapping[str, float]) -> tuple[str, ...]:
        return tuple(f"{metric}:below-threshold" for metric in QUALITY_METRICS if metrics[metric] < 0.75)

    def _score_presence(self, payload: Mapping[str, Any], fields: tuple[str, ...]) -> float:
        present = sum(1 for field in fields if field in payload and payload[field] not in (None, ""))
        return present / len(fields)

    def _score_consistency(self, payload: Mapping[str, Any]) -> float:
        stage = payload.get("stage")
        if stage not in {"DIE", "DPG", "DDGM", "TDLL", "DRIF", "EDOF"}:
            return 0.0
        if "decision" in payload and payload["decision"] not in {"approve", "reject", "review"}:
            return 0.0
        return 1.0

    def _score_constraints(self, payload: Mapping[str, Any], constraints: tuple[str, ...]) -> float:
        if not constraints:
            return 1.0
        satisfied = sum(1 for field in constraints if payload.get(field) in (True, "compliant", "linked", "tracked", "ship", "ready"))
        return satisfied / len(constraints)

    def _score_any(self, payload: Mapping[str, Any], fields: tuple[str, ...]) -> float:
        return 1.0 if any(field in payload and payload[field] not in (None, "") for field in fields) else 0.0

    def _score_robustness(self, payload: Mapping[str, Any]) -> float:
        forbidden = ("random", "timestamp", "uuid", "nonce")
        keys = tuple(str(key).lower() for key in payload)
        return 0.0 if any(token in key for key in keys for token in forbidden) else 1.0


def create_decision_quality_benchmark_suite(profile: BenchmarkProfile | None = None) -> DecisionQualityBenchmarkSuite:
    suite = DecisionQualityBenchmarkSuite(profile=profile)
    suite.register_benchmark(
        BenchmarkDefinition(
            benchmark_id="decision-quality-default",
            name="Default platform decision quality benchmark",
            decision_input={"query": "Evaluate enterprise decision quality"},
            expected_constraints=("governance", "provenance", "lineage", "recommendation"),
            required_fields=("decision", "stage", "governance", "provenance", "lineage", "recommendation"),
        )
    )
    return suite
