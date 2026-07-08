from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .governance_policies import GOVERNANCE_RULES, GovernanceValidationPolicy


@dataclass(frozen=True)
class GovernanceValidationScorecard:
    policy_id: str
    status: str
    rule_results: Mapping[str, bool]
    score: float
    diagnostics: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "status": self.status,
            "rule_results": tuple((rule, bool(self.rule_results[rule])) for rule in GOVERNANCE_RULES if rule in self.rule_results),
            "score": round(float(self.score), 6),
            "diagnostics": self.diagnostics,
        }


def generate_governance_scorecard(policy: GovernanceValidationPolicy, rule_results: Mapping[str, bool]) -> GovernanceValidationScorecard:
    results = {rule: bool(rule_results.get(rule, False)) for rule in policy.required_rules}
    passed = sum(1 for passed_rule in results.values() if passed_rule)
    score = round(passed / len(results), 6)
    diagnostics = tuple(f"{rule}:failed" for rule in sorted(results) if not results[rule])
    return GovernanceValidationScorecard(
        policy_id=policy.policy_id,
        status="passed" if score >= policy.minimum_score and not diagnostics else "failed",
        rule_results=results,
        score=score,
        diagnostics=diagnostics,
    )


def generate_governance_report(
    policy: GovernanceValidationPolicy,
    scorecard: GovernanceValidationScorecard,
    provenance_report: Mapping[str, Any],
    governance_report: Mapping[str, Any],
    lineage_report: Mapping[str, Any],
    audit_report: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "module": "VB-004",
        "report_type": "governance_provenance_validation",
        "status": scorecard.status,
        "policy": policy.snapshot(),
        "scorecard": scorecard.to_dict(),
        "provenance_integrity": dict(sorted(provenance_report.items())),
        "governance_compliance": dict(sorted(governance_report.items())),
        "lineage_consistency": dict(sorted(lineage_report.items())),
        "audit_completeness": dict(sorted(audit_report.items())),
    }
