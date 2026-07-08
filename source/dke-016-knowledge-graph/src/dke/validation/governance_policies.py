from __future__ import annotations

from dataclasses import dataclass

from .governance_errors import GovernancePolicyError, UnsupportedGovernanceRuleError

GOVERNANCE_RULES = (
    "provenance_required",
    "governance_compliant",
    "lineage_required",
    "audit_complete",
    "workflow_continuity",
    "trace_complete",
)


@dataclass(frozen=True)
class GovernanceValidationPolicy:
    policy_id: str
    required_rules: tuple[str, ...] = GOVERNANCE_RULES
    minimum_score: float = 1.0

    def snapshot(self) -> dict[str, object]:
        return {
            "policy_id": self.policy_id,
            "required_rules": tuple(sorted(self.required_rules)),
            "minimum_score": round(float(self.minimum_score), 6),
        }


def create_default_governance_policy(policy_id: str = "enterprise-governance-default") -> GovernanceValidationPolicy:
    return GovernanceValidationPolicy(policy_id=policy_id)


def validate_governance_policy(policy: GovernanceValidationPolicy) -> dict[str, object]:
    if not isinstance(policy, GovernanceValidationPolicy):
        raise GovernancePolicyError("policy must be GovernanceValidationPolicy")
    if not isinstance(policy.policy_id, str) or not policy.policy_id.strip():
        raise GovernancePolicyError("policy_id is required")
    if not isinstance(policy.required_rules, tuple) or not policy.required_rules:
        raise GovernancePolicyError("required_rules must be a non-empty tuple")
    unsupported = tuple(rule for rule in policy.required_rules if rule not in GOVERNANCE_RULES)
    if unsupported:
        raise UnsupportedGovernanceRuleError(f"unsupported governance rule(s): {', '.join(unsupported)}")
    if not isinstance(policy.minimum_score, (int, float)) or isinstance(policy.minimum_score, bool):
        raise GovernancePolicyError("minimum_score must be numeric")
    if policy.minimum_score < 0 or policy.minimum_score > 1:
        raise GovernancePolicyError("minimum_score must be between 0 and 1")
    return {
        "status": "valid",
        "policy_id": policy.policy_id,
        "rule_count": len(policy.required_rules),
        "rules": tuple(sorted(policy.required_rules)),
    }
