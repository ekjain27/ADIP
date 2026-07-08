from __future__ import annotations

from .models import Milestone, ObjectiveNode


class MilestoneGenerator:
    WINDOWS = (("short-term", "30 days"), ("mid-term", "90 days"), ("long-term", "180 days"))

    def generate(self, alternative_id: str, objectives: tuple[ObjectiveNode, ...]) -> tuple[Milestone, ...]:
        if not objectives:
            return ()
        milestones: list[Milestone] = []
        previous = ""
        for index, (window, target) in enumerate(self.WINDOWS, start=1):
            objective = objectives[min(index - 1, len(objectives) - 1)]
            milestone_id = f"ms-{self._clean(alternative_id)}-{index}-{window}"
            dependencies = (previous,) if previous else (objective.objective_id,)
            milestones.append(
                Milestone(
                    milestone_id=milestone_id,
                    title=f"{window.title()} strategic milestone",
                    description=f"Advance {objective.description}",
                    target_completion=target,
                    priority=objective.priority,
                    dependencies=dependencies,
                    success_criteria=(
                        f"{objective.objective_id} has an accountable owner.",
                        f"{objective.objective_id} progress is measurable.",
                        "Decision risks and assumptions are reviewed.",
                    ),
                    metadata={"objective_id": objective.objective_id, "window": window},
                )
            )
            previous = milestone_id
        return tuple(milestones)

    def _clean(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("_", "-")
