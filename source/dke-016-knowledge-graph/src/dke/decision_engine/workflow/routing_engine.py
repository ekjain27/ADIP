from __future__ import annotations

from decision_engine.adaptive import AdaptiveDecision

from .models import WorkflowStage, WorkflowTransition


class RoutingEngine:
    def route(self, decision: AdaptiveDecision, stages: tuple[WorkflowStage, ...]) -> tuple[WorkflowTransition, ...]:
        transitions: list[WorkflowTransition] = []
        for index, (source, target) in enumerate(zip(stages, stages[1:]), start=1):
            transitions.append(
                WorkflowTransition(
                    transition_id=f"tx-{index:02d}-{source.stage_id}-to-{target.stage_id}",
                    source_stage=source.stage_id,
                    target_stage=target.stage_id,
                    condition=self._condition(decision, source, target),
                    priority="high" if target.name in {"Approval", "Execution"} else "medium",
                    metadata={"routing_type": "success_path", "deterministic": True},
                )
            )
        if len(stages) >= 4 and decision.behavior_profile.recommendation_mode == "conservative":
            transitions.append(
                WorkflowTransition(
                    transition_id=f"tx-adaptive-{stages[1].stage_id}-to-{stages[2].stage_id}",
                    source_stage=stages[1].stage_id,
                    target_stage=stages[2].stage_id,
                    condition="adaptive_governance_review_required",
                    priority="critical",
                    metadata={"routing_type": "adaptive_path"},
                )
            )
        return tuple(transitions)

    def _condition(self, decision: AdaptiveDecision, source: WorkflowStage, target: WorkflowStage) -> str:
        if target.name == "Approval":
            return "validation_complete_and_approval_required"
        if target.name == "Monitoring":
            return f"execution_started_with_{decision.behavior_profile.checkpoint_frequency}_checkpoints"
        return f"{source.name.lower()}_complete"
