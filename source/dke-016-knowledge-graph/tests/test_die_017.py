import pytest

from decision_engine.adaptive import AdaptiveDecisionEngine
from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.governance import DecisionGovernanceEngine
from decision_engine.learning import DecisionLearningEngine
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.provenance import DecisionProvenanceEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import StrategicPlanningEngine
from decision_engine.temporal import TemporalDecisionEngine
from decision_engine.uncertainty import UncertaintyEngine
from decision_engine.workflow import (
    ApprovalManager,
    DecisionWorkflowEngine,
    ExceptionHandler,
    RoutingEngine,
    StageBuilder,
    WorkflowGraph,
    WorkflowDecisionPackage,
    WorkflowTransition,
    WorkflowValidator,
)


def test_stage_creation():
    stages = StageBuilder().build(_adaptive_package().selected_adaptive_result)
    assert [stage.name for stage in stages] == ["Preparation", "Validation", "Approval", "Execution", "Monitoring", "Closure"]
    assert stages[0].status == "ready"


def test_routing():
    decision = _adaptive_package().selected_adaptive_result
    stages = StageBuilder().build(decision)
    transitions = RoutingEngine().route(decision, stages)
    assert transitions
    assert transitions[0].source_stage == stages[0].stage_id


def test_approval_gates():
    decision = _adaptive_package().selected_adaptive_result
    stages = StageBuilder().build(decision)
    gates = ApprovalManager().build(decision, stages)
    assert len(gates) == len(stages)
    assert any(gate.approval_type == "governance approval" for gate in gates)


def test_exception_handling():
    paths = ExceptionHandler().build(_adaptive_package().selected_adaptive_result)
    assert {path.trigger for path in paths} >= {"approval failure", "policy violation", "execution failure"}


def test_workflow_graph():
    package = DecisionWorkflowEngine().orchestrate(_adaptive_package())
    graph = package.selected_workflow.workflow_graph
    assert graph.stages
    assert graph.transitions
    assert graph.approval_gates


def test_dag_validation():
    graph = DecisionWorkflowEngine().orchestrate(_adaptive_package()).selected_workflow.workflow_graph
    assert not WorkflowValidator().has_cycle(graph)


def test_validator():
    graph = DecisionWorkflowEngine().orchestrate(_adaptive_package()).selected_workflow.workflow_graph
    WorkflowValidator().validate_graph(graph)


def test_empty_package():
    from decision_engine.adaptive import AdaptiveDecisionPackage

    package = DecisionWorkflowEngine().orchestrate(AdaptiveDecisionPackage((), None, "empty", "empty"))
    assert package.workflow_results == ()
    assert package.selected_workflow is None


def test_invalid_transition():
    graph = DecisionWorkflowEngine().orchestrate(_adaptive_package()).selected_workflow.workflow_graph
    bad_transition = WorkflowTransition("bad-transition", "missing", graph.stages[0].stage_id, "bad", "high")
    bad_graph = WorkflowGraph(graph.stages, (*graph.transitions, bad_transition), graph.approval_gates, graph.exception_paths, graph.metadata)
    with pytest.raises(ValueError, match="transition references missing stage"):
        WorkflowValidator().validate_graph(bad_graph)


def test_full_integration_die_001_to_die_017():
    package = DecisionWorkflowEngine().orchestrate(_adaptive_package())
    assert package.selected_workflow is not None
    assert package.metadata["module"] == "DIE-017"
    assert package.selected_workflow.completion_score >= 0.0


def _adaptive_package():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    multi_objective_package = MultiObjectiveEngine().optimize(learning_package)
    strategic_package = StrategicPlanningEngine().plan(multi_objective_package)
    provenance_package = DecisionProvenanceEngine().build(strategic_package)
    governance_package = DecisionGovernanceEngine().evaluate(provenance_package)
    temporal_package = TemporalDecisionEngine().track(governance_package)
    return AdaptiveDecisionEngine().adapt(temporal_package)


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
