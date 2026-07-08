from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowStep:
    name: str
    order: int


class DecisionWorkflow:
    def __init__(self) -> None:
        self.steps = (
            WorkflowStep("create_state", 1),
            WorkflowStep("retrieve_context", 2),
            WorkflowStep("validate_context", 3),
            WorkflowStep("reason", 4),
            WorkflowStep("validate_reasoning", 5),
            WorkflowStep("apply_fallback", 6),
            WorkflowStep("build_decision_package", 7),
        )

    def names(self) -> tuple[str, ...]:
        return tuple(step.name for step in sorted(self.steps, key=lambda step: step.order))
