from __future__ import annotations

from .models import GovernanceMesh, GovernancePolicy


class GovernanceMeshBuilder:
    FLOW = (
        "policy_registry",
        "provenance_integrity",
        "policy_evaluation",
        "compliance_check",
        "ethics_assessment",
        "governance_decision",
    )

    def build(self, policies: tuple[GovernancePolicy, ...]) -> GovernanceMesh:
        relationships = {
            "provenance_integrity": tuple(policy.policy_id for policy in policies if policy.category in {"Compliance", "Risk", "Operational"}),
            "recommendations": tuple(policy.policy_id for policy in policies),
            "compliance": tuple(policy.policy_id for policy in policies if policy.category in {"Compliance", "Security", "Operational"}),
            "ethics": tuple(policy.policy_id for policy in policies if policy.category == "Ethics"),
            "risk_controls": tuple(policy.policy_id for policy in policies if policy.category == "Risk"),
        }
        return GovernanceMesh(
            policies=policies,
            relationships=relationships,
            evaluation_flow=self.FLOW,
            metadata={
                "mesh_type": "Dynamic Decision Governance Mesh",
                "policy_count": len(policies),
                "relationship_count": len(relationships),
            },
        )
