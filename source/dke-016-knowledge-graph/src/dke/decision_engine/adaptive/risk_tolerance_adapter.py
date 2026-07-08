from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import BehaviorAdjustment


class RiskToleranceAdapter:
    def adjust(self, current: float, stability_score: float, governance_status: str, change_frequency: float) -> tuple[float, BehaviorAdjustment | None]:
        previous = clamp_confidence(current)
        reduction = 0.0
        if stability_score < 0.65:
            reduction += 0.08
        if governance_status in {"conditional", "rejected"}:
            reduction += 0.10
        if change_frequency > 0.45:
            reduction += 0.05
        new_value = clamp_confidence(previous - reduction)
        if new_value == previous:
            return previous, None
        return new_value, BehaviorAdjustment(
            adjustment_id="adj-risk-tolerance",
            adjustment_type="risk_tolerance",
            previous_value=previous,
            new_value=new_value,
            reason="Risk tolerance lowered due to instability, governance concern, or frequent changes.",
            confidence=clamp_confidence((stability_score + (1.0 - change_frequency)) / 2.0),
        )
