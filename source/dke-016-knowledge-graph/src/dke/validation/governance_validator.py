from __future__ import annotations

from typing import Any, Mapping

from platform_integration import PlatformIntegrationLayer, UnifiedPlatformRuntimeRegistry, create_runtime_registry_from_platform_layer

from .baseline_snapshot import BaselineSnapshot, compare_snapshots, create_baseline_snapshot
from .decision_quality_benchmark import DecisionQualityBenchmarkSuite, create_decision_quality_benchmark_suite
from .governance_errors import GovernanceBaselineError
from .governance_policies import GovernanceValidationPolicy, create_default_governance_policy, validate_governance_policy
from .governance_report import GovernanceValidationScorecard, generate_governance_report, generate_governance_scorecard
from .performance_benchmark import PerformanceBenchmarkHarness, create_performance_benchmark_harness
from .provenance_validator import ProvenanceValidator
from .regression_validator import EndToEndRegressionValidator, create_regression_validator
from .workflow_runner import create_validation_platform_layer

GOVERNANCE_BASELINE_VERSION = "VB-004.1"


class GovernanceProvenanceValidationFramework:
    MODULE = "VB-004"

    def __init__(
        self,
        policy: GovernanceValidationPolicy | None = None,
        regression_validator: EndToEndRegressionValidator | None = None,
        quality_benchmark: DecisionQualityBenchmarkSuite | None = None,
        performance_harness: PerformanceBenchmarkHarness | None = None,
        platform_layer: PlatformIntegrationLayer | None = None,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
    ) -> None:
        self.policy = policy or create_default_governance_policy()
        validate_governance_policy(self.policy)
        self.regression_validator = regression_validator or create_regression_validator()
        self.quality_benchmark = quality_benchmark or create_decision_quality_benchmark_suite()
        self.performance_harness = performance_harness or create_performance_benchmark_harness("quick")
        self.platform_layer = platform_layer or self.regression_validator.platform_layer or create_validation_platform_layer()
        self.runtime_registry = runtime_registry or create_runtime_registry_from_platform_layer(self.platform_layer)
        self.provenance_validator = ProvenanceValidator()
        self._last_report: dict[str, Any] | None = None

    def validate_governance(self, decision_payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return self.provenance_validator.validate_governance(decision_payload or self._decision_payload(), self.policy)

    def validate_provenance(self, decision_payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return self.provenance_validator.validate_provenance(decision_payload or self._decision_payload(), self.policy)

    def validate_lineage(self, decision_payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return self.provenance_validator.validate_lineage(decision_payload or self._decision_payload(), self.policy)

    def execute_governance_validation(self) -> dict[str, Any]:
        payload = self._decision_payload()
        provenance = self.validate_provenance(payload)
        governance = self.validate_governance(payload)
        lineage = self.validate_lineage(payload)
        audit = self.provenance_validator.validate_audit(payload, self.policy)
        rule_results = self._rule_results(payload)
        scorecard = generate_governance_scorecard(self.policy, rule_results)
        self._last_report = generate_governance_report(self.policy, scorecard, provenance, governance, lineage, audit)
        return self._last_report

    def generate_governance_report(self) -> dict[str, Any]:
        return self._last_report or self.execute_governance_validation()

    def export_governance_snapshot(self) -> dict[str, Any]:
        report = self.generate_governance_report()
        return {
            "module": self.MODULE,
            "baseline_version": GOVERNANCE_BASELINE_VERSION,
            "status": report["status"],
            "policy": self.policy.snapshot(),
            "report": report,
            "regression_summary": self.regression_validator.summarize_results(),
            "quality_summary": self.quality_benchmark.summarize_results(),
            "performance_summary": self.performance_harness.generate_performance_report(),
            "runtime_registry": self.runtime_registry.export_registry_snapshot(),
        }

    def compare_governance_baseline(self, baseline: BaselineSnapshot | None = None) -> dict[str, Any]:
        snapshot = self.export_governance_snapshot()
        expected = baseline or create_baseline_snapshot("vb-004-current", snapshot)
        if expected.payload.get("baseline_version") not in (None, GOVERNANCE_BASELINE_VERSION):
            raise GovernanceBaselineError("incompatible governance baseline version")
        try:
            return compare_snapshots(snapshot, expected)
        except Exception as exc:
            raise GovernanceBaselineError(str(exc)) from exc

    def _decision_payload(self) -> Mapping[str, Any]:
        dke = self.platform_layer.execute_component("DKE", {"query": "Validate governance and provenance", "research": ("R-001", "R-010")})
        pipeline = self.platform_layer.execute_pipeline(("DIE", "DPG", "DDGM", "TDLL", "DRIF"), dke.output_payload)
        return dict(pipeline.output_payload)

    def _rule_results(self, payload: Mapping[str, Any]) -> dict[str, bool]:
        return {
            "provenance_required": payload.get("provenance") == "linked",
            "governance_compliant": payload.get("governance") == "compliant",
            "lineage_required": payload.get("lineage") == "tracked",
            "audit_complete": all(field in payload for field in ("decision", "provenance", "governance", "lineage", "recommendation")),
            "workflow_continuity": all(field in payload for field in ("decision", "provenance", "governance", "lineage")),
            "trace_complete": "decision" in payload,
        }


def create_governance_validation_framework(
    policy: GovernanceValidationPolicy | None = None,
) -> GovernanceProvenanceValidationFramework:
    return GovernanceProvenanceValidationFramework(policy=policy)
