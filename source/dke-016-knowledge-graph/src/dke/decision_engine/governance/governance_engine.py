from __future__ import annotations

import logging

from decision_engine.core.models import clamp_confidence
from decision_engine.provenance import DecisionProvenance, DecisionProvenancePackage

from .ethics_evaluator import EthicsEvaluator
from .governance_mesh import GovernanceMeshBuilder
from .governance_package import GovernancePackageBuilder
from .governance_validator import GovernanceValidator
from .models import GovernanceEvaluation
from .policy_evaluator import PolicyEvaluator
from .policy_registry import PolicyRegistry

logger = logging.getLogger(__name__)


class DecisionGovernanceEngine:
    def __init__(
        self,
        policy_registry: PolicyRegistry | None = None,
        policy_evaluator: PolicyEvaluator | None = None,
        ethics_evaluator: EthicsEvaluator | None = None,
        mesh_builder: GovernanceMeshBuilder | None = None,
        package_builder: GovernancePackageBuilder | None = None,
        validator: GovernanceValidator | None = None,
    ) -> None:
        self.policy_registry = policy_registry or PolicyRegistry()
        self.policy_evaluator = policy_evaluator or PolicyEvaluator()
        self.ethics_evaluator = ethics_evaluator or EthicsEvaluator()
        self.mesh_builder = mesh_builder or GovernanceMeshBuilder()
        self.package_builder = package_builder or GovernancePackageBuilder()
        self.validator = validator or GovernanceValidator()

    def evaluate(self, provenance_package: DecisionProvenancePackage):
        if not isinstance(provenance_package, DecisionProvenancePackage):
            raise ValueError("DecisionGovernanceEngine.evaluate requires a DecisionProvenancePackage")
        logger.info("Running deterministic decision governance evaluation")
        policies = self.policy_registry.active_policies()
        self.validator.validate_policies(policies)
        mesh = self.mesh_builder.build(policies)
        evaluations = tuple(self._evaluate_provenance(provenance, policies) for provenance in provenance_package.provenance_results)
        selected = self._selected_evaluation(evaluations, provenance_package.selected_provenance)
        return self.package_builder.build(
            evaluations,
            selected,
            mesh,
            metadata={
                "source_module": provenance_package.metadata.get("module", "DIE-013"),
                "provenance_result_count": len(provenance_package.provenance_results),
            },
        )

    def _evaluate_provenance(self, provenance: DecisionProvenance, policies) -> GovernanceEvaluation:
        policy_results = self.policy_evaluator.evaluate(provenance, policies)
        ethics = self.ethics_evaluator.evaluate(provenance)
        policy_score = sum(result.score for result in policy_results) / len(policy_results) if policy_results else 0.0
        ethics_score = (ethics.fairness_score + ethics.transparency_score + ethics.accountability_score + (1.0 - ethics.bias_risk)) / 4.0
        overall_score = clamp_confidence((policy_score * 0.70) + (ethics_score * 0.30))
        violations = tuple(violation for result in policy_results for violation in result.violations)
        recommendations = tuple(dict.fromkeys(recommendation for result in policy_results for recommendation in result.recommendations))
        status = self._status(overall_score, violations)
        return GovernanceEvaluation(
            alternative_id=provenance.alternative_id,
            policy_results=policy_results,
            ethics_assessment=ethics,
            overall_score=overall_score,
            governance_status=status,
            violations=violations,
            recommendations=recommendations,
            metadata={
                "traceability_score": provenance.traceability_score,
                "policy_count": len(policy_results),
                "governance_mesh": "DDGM",
            },
        )

    def _selected_evaluation(self, evaluations, selected_provenance: DecisionProvenance | None):
        if not evaluations:
            return None
        if selected_provenance is not None:
            for evaluation in evaluations:
                if evaluation.alternative_id == selected_provenance.alternative_id:
                    return evaluation
        return max(evaluations, key=lambda evaluation: (evaluation.overall_score, evaluation.alternative_id))

    def _status(self, score: float, violations: tuple[str, ...]) -> str:
        if score < 0.60 or len(violations) >= 2:
            return "rejected"
        if violations or score < 0.78:
            return "conditional"
        return "approved"
