from __future__ import annotations

from .models import GovernancePolicy


class PolicyRegistry:
    DEFAULT_POLICIES = (
        ("policy-business-alignment", "Business Alignment", "Business", "high", "1.0", "Decision must support organizational objectives."),
        ("policy-risk-threshold", "Risk Threshold", "Risk", "critical", "1.0", "Decision must remain inside approved risk posture."),
        ("policy-regulatory-compliance", "Regulatory Compliance", "Compliance", "critical", "1.0", "Decision must preserve compliance evidence and traceability."),
        ("policy-ethical-use", "Ethical Use", "Ethics", "high", "1.0", "Decision must support fairness, transparency, and accountability."),
        ("policy-security-control", "Security Control", "Security", "high", "1.0", "Decision must avoid ungoverned security exposure."),
        ("policy-operational-readiness", "Operational Readiness", "Operational", "medium", "1.0", "Decision must have executable ownership and checkpoints."),
    )

    def __init__(self, custom_policies: tuple[GovernancePolicy, ...] = ()) -> None:
        self.custom_policies = custom_policies

    def default_policies(self) -> tuple[GovernancePolicy, ...]:
        defaults = tuple(
            GovernancePolicy(
                policy_id=policy_id,
                name=name,
                category=category,
                priority=priority,
                version=version,
                description=description,
                enabled=True,
                metadata={"source": "default_registry"},
            )
            for policy_id, name, category, priority, version, description in self.DEFAULT_POLICIES
        )
        return (*defaults, *self.custom_policies)

    def active_policies(self) -> tuple[GovernancePolicy, ...]:
        return tuple(policy for policy in self.default_policies() if policy.enabled)
