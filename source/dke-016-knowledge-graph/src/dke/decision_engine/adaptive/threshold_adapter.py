from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import BehaviorAdjustment


class ThresholdAdapter:
    def adjust(self, current: float, confidence: float, stability_score: float) -> tuple[float, BehaviorAdjustment | None]:
        previous = clamp_confidence(current)
        pressure = 0.0
        if confidence < 0.70:
            pressure += 0.08
        if stability_score < 0.65:
            pressure += 0.05
        new_value = clamp_confidence(previous + pressure)
        if new_value == previous:
            return previous, None
        return new_value, BehaviorAdjustment(
            adjustment_id="adj-confidence-threshold",
            adjustment_type="confidence_threshold",
            previous_value=previous,
            new_value=new_value,
            reason="Confidence threshold increased due to lower confidence or temporal stability.",
            confidence=clamp_confidence((confidence + stability_score) / 2.0),
        )
