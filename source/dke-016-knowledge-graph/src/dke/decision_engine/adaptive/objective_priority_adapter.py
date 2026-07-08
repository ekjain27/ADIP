from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import BehaviorAdjustment


class ObjectivePriorityAdapter:
    DEFAULT_PRIORITIES = {
        "value": 0.24,
        "risk": 0.20,
        "compliance": 0.20,
        "stability": 0.18,
        "confidence": 0.18,
    }

    def default_priorities(self) -> dict[str, float]:
        return self.normalize(dict(self.DEFAULT_PRIORITIES))

    def adjust(self, priorities: dict[str, float], governance_status: str, stability_score: float) -> tuple[dict[str, float], BehaviorAdjustment | None]:
        previous = self.normalize(dict(priorities))
        updated = dict(previous)
        if governance_status in {"conditional", "rejected"}:
            updated["compliance"] = updated.get("compliance", 0.0) + 0.07
            updated["risk"] = updated.get("risk", 0.0) + 0.05
        if stability_score < 0.70:
            updated["stability"] = updated.get("stability", 0.0) + 0.06
        normalized = self.normalize(updated)
        if normalized == previous:
            return normalized, None
        return normalized, BehaviorAdjustment(
            adjustment_id="adj-objective-priorities",
            adjustment_type="objective_priorities",
            previous_value=previous,
            new_value=normalized,
            reason="Objective priorities adapted for governance risk and temporal stability.",
            confidence=clamp_confidence(stability_score),
        )

    def normalize(self, priorities: dict[str, float]) -> dict[str, float]:
        if not priorities:
            raise ValueError("objective priorities are required")
        if any(value < 0.0 for value in priorities.values()):
            raise ValueError("objective priority weights cannot be negative")
        total = sum(priorities.values())
        if total <= 0.0:
            raise ValueError("objective priority weights must sum to a positive value")
        normalized = {key: round(value / total, 6) for key, value in priorities.items()}
        drift = round(1.0 - sum(normalized.values()), 6)
        if drift:
            first_key = next(iter(normalized))
            normalized[first_key] = round(normalized[first_key] + drift, 6)
        return normalized
