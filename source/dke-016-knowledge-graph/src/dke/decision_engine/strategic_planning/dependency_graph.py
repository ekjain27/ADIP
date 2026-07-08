from __future__ import annotations

from .models import ExecutionPhase, Milestone, ObjectiveNode, StrategicGoal


class DependencyGraphBuilder:
    def build(
        self,
        goals: tuple[StrategicGoal, ...],
        objectives: tuple[ObjectiveNode, ...],
        milestones: tuple[Milestone, ...],
        phases: tuple[ExecutionPhase, ...],
    ) -> dict[str, tuple[str, ...]]:
        dependencies: dict[str, tuple[str, ...]] = {}
        for goal in goals:
            dependencies[goal.goal_id] = (goal.parent_goal,) if goal.parent_goal else ()
        for objective in objectives:
            dependencies[objective.objective_id] = (objective.goal_id, *objective.dependencies)
        for milestone in milestones:
            dependencies[milestone.milestone_id] = milestone.dependencies
        for phase in phases:
            dependencies[phase.phase_id] = phase.milestones
        self.validate(dependencies)
        return dependencies

    def validate(self, dependencies: dict[str, tuple[str, ...]]) -> None:
        missing = sorted({dependency for values in dependencies.values() for dependency in values if dependency not in dependencies})
        if missing:
            raise ValueError(f"dependency graph contains missing dependencies: {', '.join(missing)}")
        if self.has_cycle(dependencies):
            raise ValueError("dependency graph contains a cycle")

    def has_cycle(self, dependencies: dict[str, tuple[str, ...]]) -> bool:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> bool:
            if node in visiting:
                return True
            if node in visited:
                return False
            visiting.add(node)
            for dependency in dependencies.get(node, ()):
                if visit(dependency):
                    return True
            visiting.remove(node)
            visited.add(node)
            return False

        return any(visit(node) for node in dependencies)
