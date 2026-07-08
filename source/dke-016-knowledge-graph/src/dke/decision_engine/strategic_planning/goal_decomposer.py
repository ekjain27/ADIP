from __future__ import annotations

from decision_engine.multi_objective import BalancedResult

from .models import ObjectiveNode, StrategicGoal


class GoalDecomposer:
    def decompose(self, result: BalancedResult) -> tuple[tuple[StrategicGoal, ...], tuple[ObjectiveNode, ...]]:
        alternative_id = self._clean(result.alternative_id)
        score = result.objective_score
        sorted_objectives = tuple(sorted(score.scores.items(), key=lambda item: (-item[1], item[0])))
        primary_objectives = sorted_objectives[:3] or (("value", score.weighted_score),)
        root_id = f"goal-{alternative_id}-vision"
        child_ids = tuple(f"goal-{alternative_id}-{name}" for name, _ in primary_objectives)
        goals = [
            StrategicGoal(
                goal_id=root_id,
                title=f"Execute strategy for {result.alternative_id}",
                description=f"Turn the balanced decision for {result.alternative_id} into an executable strategic plan.",
                priority="critical",
                child_goals=child_ids,
                metadata={"balance_score": result.balance_score},
            )
        ]
        objectives: list[ObjectiveNode] = []
        previous_objective_id = ""
        for index, (name, value) in enumerate(primary_objectives, start=1):
            goal_id = f"goal-{alternative_id}-{name}"
            objective_id = f"obj-{alternative_id}-{name}"
            goals.append(
                StrategicGoal(
                    goal_id=goal_id,
                    title=f"Strengthen {name}",
                    description=f"Improve and protect the {name} objective score of {value:.3f}.",
                    priority=self._priority(index),
                    parent_goal=root_id,
                    metadata={"objective_score": value},
                )
            )
            dependencies = (previous_objective_id,) if previous_objective_id else ()
            objectives.append(
                ObjectiveNode(
                    objective_id=objective_id,
                    goal_id=goal_id,
                    description=f"Deliver measurable progress for {name} while preserving portfolio balance.",
                    priority=self._priority(index),
                    dependencies=dependencies,
                    metadata={"objective_name": name, "objective_score": value},
                )
            )
            previous_objective_id = objective_id
        return tuple(goals), tuple(objectives)

    def _priority(self, index: int) -> str:
        return ("high", "medium", "medium", "low")[min(index - 1, 3)]

    def _clean(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("_", "-")
