from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import ExecutionPhase, Milestone


class ExecutionPlanner:
    PHASES = (
        ("preparation", "Preparation", "Confirm owners, assumptions, resources, and constraints."),
        ("planning", "Planning", "Sequence strategic work and lock success measures."),
        ("execution", "Execution", "Execute milestones and coordinate dependencies."),
        ("validation", "Validation", "Validate KPI progress and decision quality."),
        ("optimization", "Optimization", "Optimize plan balance and resolve tradeoffs."),
        ("completion", "Completion", "Close plan, capture learning, and hand off monitoring."),
    )

    def generate(self, alternative_id: str, milestones: tuple[Milestone, ...]) -> tuple[ExecutionPhase, ...]:
        milestone_ids = tuple(milestone.milestone_id for milestone in milestones)
        phases: list[ExecutionPhase] = []
        for index, (phase_key, title, description) in enumerate(self.PHASES, start=1):
            assigned = self._assigned_milestones(index, milestone_ids)
            effort = clamp_confidence(0.12 + (index * 0.08) + (len(assigned) * 0.06))
            phases.append(
                ExecutionPhase(
                    phase_id=f"phase-{self._clean(alternative_id)}-{index}-{phase_key}",
                    title=title,
                    description=description,
                    sequence=index,
                    milestones=assigned,
                    estimated_effort=effort,
                    metadata={"relative_duration": f"{index * 2} weeks", "priority": "high" if index <= 3 else "medium"},
                )
            )
        return tuple(phases)

    def _assigned_milestones(self, index: int, milestone_ids: tuple[str, ...]) -> tuple[str, ...]:
        if not milestone_ids:
            return ()
        if index <= len(milestone_ids):
            return (milestone_ids[index - 1],)
        return (milestone_ids[-1],) if index in {4, 5} else ()

    def _clean(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("_", "-")
