from __future__ import annotations

from typing import Any

from .models import DecisionPackage, DecisionState


class DecisionPackageBuilder:
    def build(self, decision_state: DecisionState, loaded_context: dict[str, Any] | None = None) -> DecisionPackage:
        if not isinstance(decision_state, DecisionState):
            raise ValueError("decision_state must be a DecisionState")
        loaded_context = loaded_context or {}
        processing_metadata: dict[str, Any] = {
            "module": "DIE-001",
            "pipeline": (
                "ContextLoader",
                "EvidenceNormalizer",
                "GoalExtractor",
                "ConstraintEngine",
                "DecisionStateBuilder",
                "DecisionPackageBuilder",
            ),
            "evidence_count": len(decision_state.evidence),
            "goal_count": len(decision_state.goals),
            "constraint_count": len(decision_state.constraints),
            "context_confidence": loaded_context.get("context_confidence", 0.0),
        }
        return DecisionPackage(
            decision_state=decision_state,
            evidence_set=decision_state.evidence,
            goal_set=decision_state.goals,
            constraint_set=decision_state.constraints,
            confidence=decision_state.confidence,
            processing_metadata=processing_metadata,
        )
