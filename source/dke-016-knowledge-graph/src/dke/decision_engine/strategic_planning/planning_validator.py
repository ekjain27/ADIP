from __future__ import annotations

from .dependency_graph import DependencyGraphBuilder
from .models import StrategicPlan, StrategicPlanDecisionPackage, StrategicPlanningGraph


class PlanningValidator:
    def __init__(self, dependency_graph_builder: DependencyGraphBuilder | None = None) -> None:
        self.dependency_graph_builder = dependency_graph_builder or DependencyGraphBuilder()

    def validate_graph(self, graph: StrategicPlanningGraph) -> None:
        if not graph.vision.strip():
            raise ValueError("StrategicPlanningGraph.vision is required")
        self._validate_goal_hierarchy(graph)
        self.dependency_graph_builder.validate(dict(graph.dependencies))
        self._validate_milestone_ordering(graph)
        self._validate_phase_ordering(graph)
        self._validate_checkpoint_uniqueness(graph)

    def validate_plan(self, plan: StrategicPlan) -> None:
        if not plan.alternative_id.strip():
            raise ValueError("StrategicPlan.alternative_id is required")
        self.validate_graph(plan.planning_graph)

    def validate_package(self, package: StrategicPlanDecisionPackage) -> None:
        if not isinstance(package, StrategicPlanDecisionPackage):
            raise ValueError("Expected StrategicPlanDecisionPackage")
        for plan in package.strategic_plans:
            self.validate_plan(plan)
        if package.strategic_plans and package.selected_plan is None:
            raise ValueError("selected plan is required when strategic plans exist")
        if not package.strategic_plans and package.selected_plan is not None:
            raise ValueError("selected plan must be None when no strategic plans exist")
        if package.selected_plan is not None and package.selected_plan not in package.strategic_plans:
            raise ValueError("selected plan must be present in strategic plans")

    def _validate_goal_hierarchy(self, graph: StrategicPlanningGraph) -> None:
        goal_ids = {goal.goal_id for goal in graph.strategic_goals}
        if len(goal_ids) != len(graph.strategic_goals):
            raise ValueError("goal hierarchy contains duplicate goals")
        for goal in graph.strategic_goals:
            if goal.parent_goal and goal.parent_goal not in goal_ids:
                raise ValueError(f"goal hierarchy missing parent {goal.parent_goal}")
            for child in goal.child_goals:
                if child not in goal_ids:
                    raise ValueError(f"goal hierarchy missing child {child}")
        for objective in graph.objective_nodes:
            if objective.goal_id not in goal_ids:
                raise ValueError(f"objective references missing goal {objective.goal_id}")

    def _validate_milestone_ordering(self, graph: StrategicPlanningGraph) -> None:
        milestone_ids = {milestone.milestone_id for milestone in graph.milestones}
        objective_ids = {objective.objective_id for objective in graph.objective_nodes}
        known = set(objective_ids)
        for milestone in graph.milestones:
            for dependency in milestone.dependencies:
                if dependency not in known and dependency not in milestone_ids:
                    raise ValueError(f"milestone references missing dependency {dependency}")
            known.add(milestone.milestone_id)

    def _validate_phase_ordering(self, graph: StrategicPlanningGraph) -> None:
        sequences = tuple(phase.sequence for phase in graph.execution_phases)
        if sequences != tuple(sorted(sequences)):
            raise ValueError("execution phases must be ordered by sequence")
        if len(sequences) != len(set(sequences)):
            raise ValueError("execution phases must have unique sequence values")

    def _validate_checkpoint_uniqueness(self, graph: StrategicPlanningGraph) -> None:
        checkpoint_ids = tuple(checkpoint.checkpoint_id for checkpoint in graph.checkpoints)
        if len(checkpoint_ids) != len(set(checkpoint_ids)):
            raise ValueError("checkpoints must be unique")
