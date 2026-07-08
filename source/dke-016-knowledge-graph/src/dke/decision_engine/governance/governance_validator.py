from __future__ import annotations

from .models import ComplianceResult, EthicsAssessment, GovernanceDecisionPackage, GovernanceEvaluation, GovernanceMesh, GovernancePolicy


class GovernanceValidator:
    VALID_STATUSES = {"approved", "conditional", "rejected", "not_applicable"}
    VALID_RESULT_STATUSES = {"pass", "violation"}

    def validate_policies(self, policies: tuple[GovernancePolicy, ...]) -> None:
        policy_ids = tuple(policy.policy_id for policy in policies)
        if len(policy_ids) != len(set(policy_ids)):
            raise ValueError("governance policies must be unique")
        for policy in policies:
            if not policy.policy_id.strip() or not policy.name.strip():
                raise ValueError("governance policy id and name are required")
            if not policy.category.strip():
                raise ValueError("governance policy category is required")

    def validate_result(self, result: ComplianceResult) -> None:
        if result.status not in self.VALID_RESULT_STATUSES:
            raise ValueError(f"invalid compliance status: {result.status}")
        self._validate_unit(result.score, "compliance score")

    def validate_ethics(self, assessment: EthicsAssessment) -> None:
        self._validate_unit(assessment.fairness_score, "fairness score")
        self._validate_unit(assessment.transparency_score, "transparency score")
        self._validate_unit(assessment.accountability_score, "accountability score")
        self._validate_unit(assessment.bias_risk, "bias risk")

    def validate_evaluation(self, evaluation: GovernanceEvaluation) -> None:
        if not evaluation.alternative_id.strip():
            raise ValueError("GovernanceEvaluation.alternative_id is required")
        if evaluation.governance_status not in self.VALID_STATUSES:
            raise ValueError(f"invalid governance status: {evaluation.governance_status}")
        self._validate_unit(evaluation.overall_score, "overall governance score")
        for result in evaluation.policy_results:
            self.validate_result(result)
        self.validate_ethics(evaluation.ethics_assessment)

    def validate_mesh(self, mesh: GovernanceMesh) -> None:
        self.validate_policies(mesh.policies)
        policy_ids = {policy.policy_id for policy in mesh.policies}
        if not mesh.evaluation_flow:
            raise ValueError("governance mesh evaluation flow is required")
        for relationship, policy_refs in mesh.relationships.items():
            if not relationship.strip():
                raise ValueError("governance mesh relationship name is required")
            missing = sorted(ref for ref in policy_refs if ref not in policy_ids)
            if missing:
                raise ValueError(f"governance mesh references missing policies: {', '.join(missing)}")

    def validate_package(self, package: GovernanceDecisionPackage) -> None:
        if not isinstance(package, GovernanceDecisionPackage):
            raise ValueError("Expected GovernanceDecisionPackage")
        self.validate_mesh(package.mesh)
        for evaluation in package.evaluations:
            self.validate_evaluation(evaluation)
        if package.evaluations and package.selected_evaluation is None:
            raise ValueError("selected evaluation is required when governance evaluations exist")
        if not package.evaluations and package.selected_evaluation is not None:
            raise ValueError("selected evaluation must be None when no governance evaluations exist")
        if package.selected_evaluation is not None and package.selected_evaluation not in package.evaluations:
            raise ValueError("selected evaluation must be present in evaluations")

    def _validate_unit(self, value: float, field_name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field_name} must be between 0 and 1")
