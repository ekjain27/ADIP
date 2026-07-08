import pytest

from decision_engine.adaptive import AdaptiveDecisionEngine
from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.governance import DecisionGovernanceEngine
from decision_engine.learning import DecisionLearningEngine
from decision_engine.monitoring import (
    AlertGenerator,
    DecisionAlert,
    DecisionHealth,
    DecisionMonitoringEngine,
    DriftDetector,
    HealthMonitor,
    MetricCollector,
    MonitoringValidator,
)
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.provenance import DecisionProvenanceEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import StrategicPlanningEngine
from decision_engine.temporal import TemporalDecisionEngine
from decision_engine.uncertainty import UncertaintyEngine
from decision_engine.workflow import DecisionWorkflowEngine, WorkflowDecisionPackage


def test_metric_collector_works():
    metrics = MetricCollector().collect(_workflow_package().selected_workflow)
    assert {metric.name for metric in metrics} == {"completion_score", "stage_count", "approval_count", "exception_count", "routing_complexity"}
    assert all(0.0 <= metric.value <= 1.0 for metric in metrics)


def test_health_score_is_between_zero_and_one():
    metrics = MetricCollector().collect(_workflow_package().selected_workflow)
    drift = DriftDetector().detect(_workflow_package().selected_workflow, metrics)
    health = HealthMonitor().evaluate("alt", metrics, drift)
    assert 0.0 <= health.health_score <= 1.0


def test_workflow_status_is_valid():
    package = DecisionMonitoringEngine().monitor(_workflow_package())
    assert package.selected_monitoring.workflow_status in MonitoringValidator.VALID_WORKFLOW_STATUSES


def test_drift_detector_works():
    workflow = _workflow_package().selected_workflow
    metrics = MetricCollector().collect(workflow)
    drift = DriftDetector().detect(workflow, metrics)
    assert set(drift) == {"risk_drift", "confidence_drift", "governance_drift"}
    assert all(0.0 <= value <= 1.0 for value in drift.values())


def test_alert_generator_creates_alerts_when_degraded():
    alerts = AlertGenerator().generate("alt", 0.3, "critical", (), {"risk_drift": 0.8, "confidence_drift": 0.2, "governance_drift": 0.7})
    assert alerts
    assert any(alert.severity == "critical" for alert in alerts)


def test_monitoring_engine_handles_empty_package():
    package = DecisionMonitoringEngine().monitor(WorkflowDecisionPackage((), None, "empty", "empty"))
    assert package.monitoring_results == ()
    assert package.selected_monitoring is None


def test_monitoring_engine_creates_monitoring_results():
    package = DecisionMonitoringEngine().monitor(_workflow_package())
    assert package.monitoring_results
    assert package.selected_monitoring is not None
    assert package.selected_monitoring.metrics


def test_validator_catches_invalid_health_score():
    health = DecisionMonitoringEngine().monitor(_workflow_package()).selected_monitoring
    bad = DecisionHealth(health.alternative_id, 1.2, health.workflow_status, health.risk_drift, health.confidence_drift, health.governance_drift, health.metrics, health.alerts, health.metadata)
    with pytest.raises(ValueError, match="health score must be between 0 and 1"):
        MonitoringValidator().validate_health(bad)


def test_validator_catches_invalid_alert_severity():
    alert = DecisionAlert("a1", "risk", "severe", "bad", "m1", "fix")
    with pytest.raises(ValueError, match="invalid alert severity"):
        MonitoringValidator().validate_alert(alert)


def test_full_integration_die_001_to_die_018():
    package = DecisionMonitoringEngine().monitor(_workflow_package())
    assert package.selected_monitoring is not None
    assert package.metadata["module"] == "DIE-018"
    assert package.selected_monitoring.health_score >= 0.0


def _workflow_package():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    multi_objective_package = MultiObjectiveEngine().optimize(learning_package)
    strategic_package = StrategicPlanningEngine().plan(multi_objective_package)
    provenance_package = DecisionProvenanceEngine().build(strategic_package)
    governance_package = DecisionGovernanceEngine().evaluate(provenance_package)
    temporal_package = TemporalDecisionEngine().track(governance_package)
    adaptive_package = AdaptiveDecisionEngine().adapt(temporal_package)
    return DecisionWorkflowEngine().orchestrate(adaptive_package)


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
