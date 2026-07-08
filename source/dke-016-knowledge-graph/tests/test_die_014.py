import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.governance import (
    ComplianceChecker,
    DecisionGovernanceEngine,
    EthicsEvaluator,
    GovernanceMesh,
    GovernanceMeshBuilder,
    GovernancePackageBuilder,
    GovernancePolicy,
    GovernanceValidator,
    PolicyEvaluator,
    PolicyRegistry,
)
from decision_engine.learning import DecisionLearningEngine
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.provenance import DecisionProvenanceEngine
from decision_engine.provenance import DecisionProvenancePackage
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import StrategicPlanningEngine
from decision_engine.uncertainty import UncertaintyEngine


def test_policy_registry():
    policies = PolicyRegistry().active_policies()
    assert len(policies) == 6
    assert {policy.category for policy in policies} >= {"Business", "Risk", "Compliance", "Ethics", "Security", "Operational"}


def test_policy_evaluation():
    provenance = _provenance_package().selected_provenance
    results = PolicyEvaluator().evaluate(provenance, PolicyRegistry().active_policies())
    assert results
    assert all(0.0 <= result.score <= 1.0 for result in results)


def test_compliance_checking():
    provenance = _provenance_package().selected_provenance
    policy = PolicyRegistry().active_policies()[0]
    checked = ComplianceChecker().check(provenance, policy)
    assert checked["status"] in {"pass", "violation"}
    assert checked["recommendations"]


def test_ethics_evaluation():
    assessment = EthicsEvaluator().evaluate(_provenance_package().selected_provenance)
    assert 0.0 <= assessment.fairness_score <= 1.0
    assert 0.0 <= assessment.transparency_score <= 1.0
    assert 0.0 <= assessment.accountability_score <= 1.0
    assert 0.0 <= assessment.bias_risk <= 1.0


def test_governance_mesh():
    mesh = GovernanceMeshBuilder().build(PolicyRegistry().active_policies())
    assert mesh.evaluation_flow
    assert mesh.relationships["compliance"]
    assert mesh.metadata["mesh_type"] == "Dynamic Decision Governance Mesh"


def test_validator():
    package = DecisionGovernanceEngine().evaluate(_provenance_package())
    GovernanceValidator().validate_package(package)
    assert package.selected_evaluation.governance_status in GovernanceValidator.VALID_STATUSES


def test_empty_package():
    empty_provenance = DecisionProvenancePackage((), None, {"graph_count": 0}, "empty")
    package = DecisionGovernanceEngine().evaluate(empty_provenance)
    assert package.evaluations == ()
    assert package.selected_evaluation is None


def test_invalid_score():
    package = DecisionGovernanceEngine().evaluate(_provenance_package())
    evaluation = package.selected_evaluation
    bad = type(evaluation)(
        evaluation.alternative_id,
        evaluation.policy_results,
        evaluation.ethics_assessment,
        1.2,
        evaluation.governance_status,
        evaluation.violations,
        evaluation.recommendations,
        evaluation.metadata,
    )
    with pytest.raises(ValueError, match="overall governance score must be between 0 and 1"):
        GovernanceValidator().validate_evaluation(bad)


def test_mesh_consistency():
    policy = GovernancePolicy("policy-a", "A", "Business", "high", "1.0", "desc")
    mesh = GovernanceMesh((policy,), {"broken": ("missing-policy",)}, ("policy_registry",))
    with pytest.raises(ValueError, match="missing policies"):
        GovernanceValidator().validate_mesh(mesh)


def test_full_integration_die_001_to_die_014():
    package = DecisionGovernanceEngine().evaluate(_provenance_package())
    assert package.selected_evaluation is not None
    assert package.selected_evaluation.policy_results
    assert package.metadata["module"] == "DIE-014"


def _provenance_package():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    multi_objective_package = MultiObjectiveEngine().optimize(learning_package)
    strategic_package = StrategicPlanningEngine().plan(multi_objective_package)
    return DecisionProvenanceEngine().build(strategic_package)


def _scenario_package():
    decision_package = DIECore().process(
        {
            "query": "Select a reliable technical vendor with low risk and policy alignment",
            "semantic_results": [
                {"id": "e1", "text": "Vendor A has strong reliability and measurable value.", "confidence": 0.9},
                {"id": "e2", "text": "Vendor B has compliance concerns and uncertain delivery.", "confidence": 0.65},
            ],
            "metadata": {"constraints": [{"type": "policy", "severity": "medium"}]},
        }
    )
    alternative_package = AlternativeGenerator().generate(decision_package.decision_state)
    evaluated_package = DecisionEvaluator().evaluate(alternative_package)
    ranked_package = DecisionRanker().rank(evaluated_package)
    simulation_package = DecisionSimulator().simulate(ranked_package)
    explanation_package = ExplanationGenerator().explain(simulation_package)
    optimized_package = OptimizationEngine().optimize(explanation_package)
    uncertainty_package = UncertaintyEngine().analyze(optimized_package)
    return DecisionScenarioEngine().analyze(uncertainty_package)

