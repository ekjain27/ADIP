from __future__ import annotations

from hashlib import sha256
from typing import Any

from decision_engine.core import Constraint, Evidence, Goal
from decision_engine.core.models import clamp_confidence

from .models import AlternativeDecision


class AlternativeBuilder:
    def build(
        self,
        title: str,
        description: str,
        supporting_evidence: tuple[Evidence, ...] | tuple[str, ...] = (),
        supporting_goals: tuple[Goal, ...] | tuple[str, ...] = (),
        supporting_constraints: tuple[Constraint, ...] | tuple[str, ...] = (),
        assumptions: tuple[str, ...] = (),
        confidence: float = 0.0,
        feasibility: float | None = None,
        risks: tuple[str, ...] = (),
        advantages: tuple[str, ...] = (),
        disadvantages: tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
        alternative_id: str | None = None,
    ) -> AlternativeDecision:
        title = title.strip()
        description = description.strip()
        if not title:
            raise ValueError("AlternativeDecision.title is required")
        if not description:
            raise ValueError("AlternativeDecision.description is required")

        evidence_ids = self._evidence_ids(supporting_evidence)
        goal_refs = self._goal_refs(supporting_goals)
        constraint_refs = self._constraint_refs(supporting_constraints)
        normalized_confidence = clamp_confidence(confidence)
        normalized_feasibility = clamp_confidence(feasibility if feasibility is not None else normalized_confidence)
        alt_id = alternative_id or self._stable_id(title, description)
        data = {
            "generated_by": "DIE-002",
            "supporting_evidence_count": len(evidence_ids),
            "supporting_goal_count": len(goal_refs),
            "supporting_constraint_count": len(constraint_refs),
        }
        data.update(metadata or {})

        return AlternativeDecision(
            alternative_id=alt_id,
            title=title,
            description=description,
            supporting_evidence=evidence_ids,
            supporting_goals=goal_refs,
            supporting_constraints=constraint_refs,
            assumptions=self._as_string_tuple(assumptions),
            confidence=normalized_confidence,
            feasibility=normalized_feasibility,
            risks=self._as_string_tuple(risks),
            advantages=self._as_string_tuple(advantages),
            disadvantages=self._as_string_tuple(disadvantages),
            metadata=data,
        )

    def _stable_id(self, title: str, description: str) -> str:
        digest = sha256(f"{title}|{description}".encode("utf-8")).hexdigest()[:16]
        return f"alt-{digest}"

    def _evidence_ids(self, evidence: tuple[Evidence, ...] | tuple[str, ...]) -> tuple[str, ...]:
        return tuple(str(getattr(item, "id", item)) for item in evidence if str(getattr(item, "id", item)))

    def _goal_refs(self, goals: tuple[Goal, ...] | tuple[str, ...]) -> tuple[str, ...]:
        return tuple(str(getattr(item, "objective", item)) for item in goals if str(getattr(item, "objective", item)))

    def _constraint_refs(self, constraints: tuple[Constraint, ...] | tuple[str, ...]) -> tuple[str, ...]:
        return tuple(str(getattr(item, "type", item)) for item in constraints if str(getattr(item, "type", item)))

    def _as_string_tuple(self, values: tuple[Any, ...]) -> tuple[str, ...]:
        return tuple(str(value) for value in values if str(value))
