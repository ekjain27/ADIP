from __future__ import annotations

from decision_engine.provenance import DecisionProvenance

from .compliance_checker import ComplianceChecker
from .models import ComplianceResult, GovernancePolicy


class PolicyEvaluator:
    def __init__(self, compliance_checker: ComplianceChecker | None = None) -> None:
        self.compliance_checker = compliance_checker or ComplianceChecker()

    def evaluate(
        self,
        provenance: DecisionProvenance,
        policies: tuple[GovernancePolicy, ...],
    ) -> tuple[ComplianceResult, ...]:
        return tuple(self.evaluate_policy(provenance, policy) for policy in policies if policy.enabled)

    def evaluate_policy(self, provenance: DecisionProvenance, policy: GovernancePolicy) -> ComplianceResult:
        checked = self.compliance_checker.check(provenance, policy)
        return ComplianceResult(
            policy=policy,
            status=checked["status"],
            score=checked["score"],
            violations=checked["violations"],
            recommendations=checked["recommendations"],
            metadata={
                "alternative_id": provenance.alternative_id,
                "traceability_score": provenance.traceability_score,
            },
        )
