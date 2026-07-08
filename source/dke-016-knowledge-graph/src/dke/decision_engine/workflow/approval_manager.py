from __future__ import annotations

from decision_engine.adaptive import AdaptiveDecision

from .models import ApprovalGate, WorkflowStage


class ApprovalManager:
    def build(self, decision: AdaptiveDecision, stages: tuple[WorkflowStage, ...]) -> tuple[ApprovalGate, ...]:
        gates: list[ApprovalGate] = []
        mode = decision.behavior_profile.recommendation_mode
        sensitivity = decision.behavior_profile.governance_sensitivity
        for stage in stages:
            approval_required = stage.name in {"Validation", "Approval"} or sensitivity >= 0.78
            if stage.name == "Execution" and mode == "conservative":
                approval_required = True
            gates.append(
                ApprovalGate(
                    gate_id=f"gate-{stage.stage_id}",
                    stage_id=stage.stage_id,
                    approval_required=approval_required,
                    approval_type=self._approval_type(stage, mode, sensitivity),
                    metadata={"governance_sensitivity": sensitivity},
                )
            )
        return tuple(gates)

    def _approval_type(self, stage: WorkflowStage, mode: str, sensitivity: float) -> str:
        if stage.name == "Approval":
            return "governance approval"
        if stage.name == "Validation":
            return "policy approval"
        if mode == "conservative" or sensitivity >= 0.80:
            return "manual approval"
        return "automatic approval"
