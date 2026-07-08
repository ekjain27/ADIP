from __future__ import annotations

from .models import MultiObjective


class ObjectiveRegistry:
    DEFAULT_WEIGHTS = {
        "value": 0.24,
        "risk": 0.18,
        "confidence": 0.18,
        "feasibility": 0.15,
        "compliance": 0.13,
        "stability": 0.12,
    }

    MINIMIZE_OBJECTIVES = {"risk"}

    DESCRIPTIONS = {
        "value": "Expected decision value from learned outcome quality.",
        "risk": "Risk-adjusted resilience, scored higher when risk is lower.",
        "confidence": "Updated confidence after learning feedback.",
        "feasibility": "Practical achievability from prediction and feedback signals.",
        "compliance": "Policy and assumption alignment inferred from deterministic signals.",
        "stability": "Sensitivity of the decision to confidence adjustment and variance.",
    }

    def default_objectives(self) -> tuple[MultiObjective, ...]:
        return self.build(self.DEFAULT_WEIGHTS)

    def build(self, weights: dict[str, float]) -> tuple[MultiObjective, ...]:
        normalized = self.normalize_weights(weights)
        return tuple(
            MultiObjective(
                objective_id=f"mo-{name}",
                name=name,
                weight=weight,
                target="minimize" if name in self.MINIMIZE_OBJECTIVES else "maximize",
                description=self.DESCRIPTIONS.get(name, name.replace("_", " ")),
            )
            for name, weight in normalized.items()
        )

    def normalize_weights(self, weights: dict[str, float]) -> dict[str, float]:
        if not weights:
            raise ValueError("Objective weights are required")
        if any(value < 0.0 for value in weights.values()):
            raise ValueError("Objective weights cannot be negative")
        total = sum(weights.values())
        if total <= 0.0:
            raise ValueError("Objective weights must sum to a positive value")
        normalized = {name: round(value / total, 6) for name, value in weights.items()}
        drift = round(1.0 - sum(normalized.values()), 6)
        if normalized and drift:
            first_key = next(iter(normalized))
            normalized[first_key] = round(normalized[first_key] + drift, 6)
        return normalized
