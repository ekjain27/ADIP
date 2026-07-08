import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.learning import DecisionLearningEngine
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import (
    CheckpointGenerator,
    DependencyGraphBuilder,
    ExecutionPlanner,
    GoalDecomposer,
    MilestoneGenerator,
    PlanningPackageBuilder,
    PlanningValidator,
    StrategicPlanningEngine,
)
from decision_engine.uncertainty import UncertaintyEngine


def test_goal_decomposition():
    result = _multi_objective_package().selected_result
    goals, objectives = GoalDecomposer().decompose(result)
    assert goals
    assert objectives
    assert goals[0].child_goals
    assert all(objective.goal_id in {goal.goal_id for goal in goals} for objective in objectives)


def test_milestone_generation():
    result = _multi_objective_package().selected_result
    _, objectives = GoalDecomposer().decompose(result)
    milestones = MilestoneGenerator().generate(result.alternative_id, objectives)
    assert len(milestones) == 3
    assert all(milestone.success_criteria for milestone in milestones)
    assert milestones[0].target_completion == "30 days"


def test_dependency_graph_is_dag():
    graph = _planning_package().selected_plan.planning_graph
    builder = DependencyGraphBuilder()
    assert not builder.has_cycle(dict(graph.dependencies))


def test_cycle_detection():
    dependencies = {"a": ("b",), "b": ("c",), "c": ("a",)}
    assert DependencyGraphBuilder().has_cycle(dependencies)


def test_execution_phases_generated():
    result = _multi_objective_package().selected_result
    _, objectives = GoalDecomposer().decompose(result)
    milestones = MilestoneGenerator().generate(result.alternative_id, objectives)
    phases = ExecutionPlanner().generate(result.alternative_id, milestones)
    assert [phase.title for phase in phases] == ["Preparation", "Planning", "Execution", "Validation", "Optimization", "Completion"]
    assert [phase.sequence for phase in phases] == [1, 2, 3, 4, 5, 6]


def test_checkpoint_generation():
    checkpoints = CheckpointGenerator().generate("alt-a")
    assert len(checkpoints) == 4
    assert {checkpoint.title for checkpoint in checkpoints} >= {"Budget exceeded", "Risk increases"}


def test_validator_catches_cycles():
    graph = _planning_package().selected_plan.planning_graph
    bad_dependencies = dict(graph.dependencies)
    bad_dependencies["cycle-a"] = ("cycle-b",)
    bad_dependencies["cycle-b"] = ("cycle-a",)
    bad_graph = _replace_graph(graph, dependencies=bad_dependencies)
    with pytest.raises(ValueError, match="cycle"):
        PlanningValidator().validate_graph(bad_graph)


def test_validator_catches_missing_dependency():
    graph = _planning_package().selected_plan.planning_graph
    bad_dependencies = dict(graph.dependencies)
    first_key = next(iter(bad_dependencies))
    bad_dependencies[first_key] = ("missing-node",)
    bad_graph = _replace_graph(graph, dependencies=bad_dependencies)
    with pytest.raises(ValueError, match="missing dependencies"):
        PlanningValidator().validate_graph(bad_graph)


def test_package_builder_works():
    package = _planning_package()
    rebuilt = PlanningPackageBuilder().build(package.strategic_plans, package.selected_plan)
    assert rebuilt.selected_plan == package.selected_plan
    assert rebuilt.metadata["module"] == "DIE-012"


def test_full_integration_die_001_to_die_012():
    package = StrategicPlanningEngine().plan(_multi_objective_package())
    assert package.selected_plan is not None
    assert package.selected_plan.planning_graph.execution_phases
    assert package.metadata["balanced_result_count"] >= 1


def _planning_package():
    return StrategicPlanningEngine().plan(_multi_objective_package())


def _multi_objective_package():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    return MultiObjectiveEngine().optimize(learning_package)


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


def _replace_graph(graph, **changes):
    values = {
        "vision": graph.vision,
        "strategic_goals": graph.strategic_goals,
        "objective_nodes": graph.objective_nodes,
        "milestones": graph.milestones,
        "execution_phases": graph.execution_phases,
        "dependencies": graph.dependencies,
        "checkpoints": graph.checkpoints,
        "metadata": graph.metadata,
    }
    values.update(changes)
    return type(graph)(**values)
