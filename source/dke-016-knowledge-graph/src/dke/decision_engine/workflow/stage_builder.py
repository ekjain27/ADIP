from __future__ import annotations

from decision_engine.adaptive import AdaptiveDecision

from .models import WorkflowStage


class StageBuilder:
    DEFAULT_STAGES = (
        ("preparation", "Preparation", "Prepare owners, context, resources, and workflow prerequisites."),
        ("validation", "Validation", "Validate adaptive profile, constraints, and execution readiness."),
        ("approval", "Approval", "Route required approvals and governance sign-off."),
        ("execution", "Execution", "Execute the approved adaptive decision workflow."),
        ("monitoring", "Monitoring", "Monitor checkpoints, exceptions, and adaptive routing signals."),
        ("closure", "Closure", "Close workflow, capture evidence, and publish completion state."),
    )

    def build(self, decision: AdaptiveDecision, custom_stages: tuple[WorkflowStage, ...] = ()) -> tuple[WorkflowStage, ...]:
        if custom_stages:
            return custom_stages
        clean = self._clean(decision.alternative_id)
        stages: list[WorkflowStage] = []
        previous = ""
        for sequence, (key, name, description) in enumerate(self.DEFAULT_STAGES, start=1):
            stage_id = f"stage-{clean}-{sequence}-{key}"
            stages.append(
                WorkflowStage(
                    stage_id=stage_id,
                    name=name,
                    description=description,
                    sequence=sequence,
                    status="pending" if sequence > 1 else "ready",
                    dependencies=(previous,) if previous else (),
                    metadata={
                        "recommendation_mode": decision.behavior_profile.recommendation_mode,
                        "checkpoint_frequency": decision.behavior_profile.checkpoint_frequency,
                    },
                )
            )
            previous = stage_id
        return tuple(stages)

    def _clean(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("_", "-")
