import pytest

from decision_engine.adaptive import AdaptiveDecisionEngine
from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.enterprise_orchestrator import (
    DecisionManifestBuilder,
    EnterpriseDecision,
    EnterpriseDecisionOrchestrator,
    EnterprisePackageBuilder,
    LifecycleCoordinator,
    OrchestrationValidator,
    ReadinessAssessor,
)
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.governance import DecisionGovernanceEngine
from decision_engine.learning import DecisionLearningEngine
from decision_engine.monitoring import DecisionMonitoringEngine
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.provenance import DecisionProvenanceEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.recommendation_service import (
    DecisionRecommendationService,
    RecommendationServicePackage,
)
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import StrategicPlanningEngine
from decision_engine.temporal import TemporalDecisionEngine
from decision_engine.uncertainty import UncertaintyEngine
from decision_engine.workflow import DecisionWorkflowEngine


def test_decision_manifest_builder_creates_manifest():
    response = _recommendation_package().selected_response
    manifest = DecisionManifestBuilder().build(response)
    assert manifest.alternative_id == response.alternative_id
    assert manifest.confidence == response.confidence


def test_lifecycle_coordinator_creates_lifecycle_state():
    package = _recommendation_package()
    state = LifecycleCoordinator().coordinate(package, package.selected_response)
    assert state.state_id
    assert 0.0 <= state.readiness_score <= 1.0
    assert "recommendation" in state.completed_stages


def test_readiness_assessor_returns_score_between_zero_and_one():
    response = _recommendation_package().selected_response
    score, status = ReadinessAssessor().assess(response)
    assert 0.0 <= score <= 1.0
    assert status in ReadinessAssessor.VALID_STATUSES


def test_enterprise_status_is_valid():
    package = EnterpriseDecisionOrchestrator().orchestrate(_recommendation_package())
    assert package.selected_enterprise_decision.enterprise_status in ReadinessAssessor.VALID_STATUSES


def test_orchestrator_handles_empty_package():
    package = EnterpriseDecisionOrchestrator().orchestrate(
        RecommendationServicePackage((), None, (), "empty", "empty")
    )
    assert package.enterprise_decisions == ()
    assert package.selected_enterprise_decision is None


def test_orchestrator_creates_enterprise_decisions():
    package = EnterpriseDecisionOrchestrator().orchestrate(_recommendation_package())
    assert package.enterprise_decisions
    assert package.selected_enterprise_decision is not None
    assert package.lifecycle_summary


def test_validator_catches_invalid_readiness_score():
    decision = EnterpriseDecisionOrchestrator().orchestrate(_recommendation_package()).enterprise_decisions[0]
    bad = EnterpriseDecision(
        decision.alternative_id,
        decision.manifest,
        decision.lifecycle_state,
        1.2,
        decision.enterprise_status,
        decision.final_recommendation,
        decision.next_actions,
        decision.audit_notes,
        decision.metadata,
    )
    with pytest.raises(ValueError, match="enterprise readiness score must be between 0 and 1"):
        OrchestrationValidator().validate_decision(bad)


def test_validator_catches_invalid_enterprise_status():
    decision = EnterpriseDecisionOrchestrator().orchestrate(_recommendation_package()).enterprise_decisions[0]
    bad = EnterpriseDecision(
        decision.alternative_id,
        decision.manifest,
        decision.lifecycle_state,
        decision.readiness_score,
        "paused",
        decision.final_recommendation,
        decision.next_actions,
        decision.audit_notes,
        decision.metadata,
    )
    with pytest.raises(ValueError, match="invalid enterprise status"):
        OrchestrationValidator().validate_decision(bad)


def test_package_builder_works():
    orchestrator = EnterpriseDecisionOrchestrator()
    decision = orchestrator.orchestrate(_recommendation_package()).enterprise_decisions[0]
    package = EnterprisePackageBuilder().build((decision,), decision)
    assert package.selected_enterprise_decision == decision
    assert package.metadata["module"] == "DIE-020"


def test_full_integration_die_001_to_die_020():
    package = EnterpriseDecisionOrchestrator().orchestrate(_recommendation_package())
    assert package.selected_enterprise_decision is not None
    assert package.metadata["module"] == "DIE-020"
    assert package.selected_enterprise_decision.readiness_score >= 0.0


def _recommendation_package():
    monitoring_package = _monitoring_package()
    return DecisionRecommendationService().serve(monitoring_package)


def _monitoring_package():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    multi_objective_package = MultiObjectiveEngine().optimize(learning_package)
    strategic_package = StrategicPlanningEngine().plan(multi_objective_package)
    provenance_package = DecisionProvenanceEngine().build(strategic_package)
    governance_package = DecisionGovernanceEngine().evaluate(provenance_package)
    temporal_package = TemporalDecisionEngine().track(governance_package)
    adaptive_package = AdaptiveDecisionEngine().adapt(temporal_package)
    workflow_package = DecisionWorkflowEngine().orchestrate(adaptive_package)
    return DecisionMonitoringEngine().monitor(workflow_package)


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
