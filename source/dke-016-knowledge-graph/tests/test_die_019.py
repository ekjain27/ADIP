import pytest

from decision_engine.adaptive import AdaptiveDecisionEngine
from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.governance import DecisionGovernanceEngine
from decision_engine.learning import DecisionLearningEngine
from decision_engine.monitoring import DecisionMonitoringEngine, MonitoringDecisionPackage
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.provenance import DecisionProvenanceEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.recommendation_service import (
    DecisionRecommendationService,
    DeliveryRouter,
    PriorityAssigner,
    RecommendationFormatter,
    RecommendationResponse,
    RecommendationServicePackageBuilder,
    ResponseBuilder,
    ServiceValidator,
)
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import StrategicPlanningEngine
from decision_engine.temporal import TemporalDecisionEngine
from decision_engine.uncertainty import UncertaintyEngine
from decision_engine.workflow import DecisionWorkflowEngine


def test_response_builder_creates_response():
    package = _monitoring_package()
    responses = ResponseBuilder().build(package)
    assert responses
    assert responses[0].alternative_id == package.monitoring_results[0].alternative_id


def test_formatter_creates_all_formats():
    health = _monitoring_package().selected_monitoring
    formatter = RecommendationFormatter()
    for format_type in ("detailed", "summary", "executive", "technical"):
        assert formatter.format(health, format_type)


def test_priority_assigner_returns_valid_priority():
    priority = PriorityAssigner().assign(_monitoring_package().selected_monitoring)
    assert priority in PriorityAssigner.VALID_PRIORITIES


def test_delivery_router_creates_routes():
    responses = ResponseBuilder().build(_monitoring_package())
    deliveries = DeliveryRouter().route(responses)
    assert deliveries
    assert {delivery.channel for delivery in deliveries} == {"api", "dashboard", "report", "audit"}


def test_service_handles_empty_package():
    package = DecisionRecommendationService().serve(MonitoringDecisionPackage((), None, "empty", "empty"))
    assert package.responses == ()
    assert package.selected_response is None
    assert package.deliveries == ()


def test_service_creates_responses():
    package = DecisionRecommendationService().serve(_monitoring_package())
    assert package.responses
    assert package.selected_response is not None
    assert package.deliveries


def test_validator_catches_invalid_confidence():
    response = ResponseBuilder().build(_monitoring_package())[0]
    bad = RecommendationResponse(response.response_id, response.alternative_id, response.title, response.summary, response.recommendation, response.priority, 1.2, response.health_status, response.alerts, response.next_actions, response.metadata)
    with pytest.raises(ValueError, match="recommendation confidence must be between 0 and 1"):
        ServiceValidator().validate_response(bad)


def test_validator_catches_invalid_priority():
    response = ResponseBuilder().build(_monitoring_package())[0]
    bad = RecommendationResponse(response.response_id, response.alternative_id, response.title, response.summary, response.recommendation, "urgent", response.confidence, response.health_status, response.alerts, response.next_actions, response.metadata)
    with pytest.raises(ValueError, match="invalid recommendation priority"):
        ServiceValidator().validate_response(bad)


def test_package_builder_works():
    responses = ResponseBuilder().build(_monitoring_package())
    deliveries = DeliveryRouter().route(responses)
    package = RecommendationServicePackageBuilder().build(responses, responses[0], deliveries)
    assert package.selected_response == responses[0]
    assert package.metadata["module"] == "DIE-019"


def test_full_integration_die_001_to_die_019():
    package = DecisionRecommendationService().serve(_monitoring_package())
    assert package.selected_response is not None
    assert package.metadata["module"] == "DIE-019"
    assert package.selected_response.confidence >= 0.0


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
