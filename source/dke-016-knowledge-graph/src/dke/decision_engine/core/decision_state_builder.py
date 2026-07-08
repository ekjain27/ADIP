from __future__ import annotations

from typing import Any

from .models import Constraint, DecisionState, Evidence, Goal, clamp_confidence


class DecisionStateBuilder:
    def build(
        self,
        evidence: tuple[Evidence, ...],
        goals: tuple[Goal, ...],
        constraints: tuple[Constraint, ...],
        loaded_context: dict[str, Any] | None = None,
    ) -> DecisionState:
        loaded_context = loaded_context or {}
        confidence = self._calculate_confidence(evidence, loaded_context)
        uncertainty = clamp_confidence(1.0 - confidence, default=1.0)
        metadata = {
            "evidence_count": len(evidence),
            "goal_count": len(goals),
            "constraint_count": len(constraints),
            "context_confidence": loaded_context.get("context_confidence", 0.0),
            "builder": "DIE-001",
        }
        assumptions = self._assumptions_for(evidence, goals)
        return DecisionState(
            evidence=evidence,
            goals=goals,
            constraints=constraints,
            assumptions=assumptions,
            uncertainty=uncertainty,
            confidence=confidence,
            metadata=metadata,
        )

    def _calculate_confidence(self, evidence: tuple[Evidence, ...], loaded_context: dict[str, Any]) -> float:
        values = [item.confidence for item in evidence]
        if loaded_context.get("context_confidence"):
            values.append(clamp_confidence(loaded_context["context_confidence"]))
        if not values:
            return 0.0
        return clamp_confidence(sum(values) / len(values))

    def _assumptions_for(self, evidence: tuple[Evidence, ...], goals: tuple[Goal, ...]) -> tuple[str, ...]:
        assumptions = []
        if not evidence:
            assumptions.append("No evidence was supplied by the context package.")
        if not goals:
            assumptions.append("No explicit goals were supplied by the context package.")
        return tuple(assumptions)
