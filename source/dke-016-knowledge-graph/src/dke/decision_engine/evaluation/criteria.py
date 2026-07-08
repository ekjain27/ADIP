from __future__ import annotations

from .models import EvaluationCriteria


def default_criteria() -> tuple[EvaluationCriteria, ...]:
    return (
        EvaluationCriteria("feasibility", 0.20, "How practical the alternative is to execute."),
        EvaluationCriteria("confidence", 0.15, "Confidence carried by the generated alternative."),
        EvaluationCriteria("goal_alignment", 0.20, "How strongly the alternative supports stated goals."),
        EvaluationCriteria("constraint_satisfaction", 0.15, "How well the alternative respects constraints."),
        EvaluationCriteria("evidence_support", 0.15, "How much evidence supports the alternative."),
        EvaluationCriteria("risk_balance", 0.10, "How favorable the risk profile is."),
        EvaluationCriteria("advantage_balance", 0.05, "Balance of advantages against disadvantages."),
    )


def validate_criteria_weights(criteria: tuple[EvaluationCriteria, ...]) -> None:
    if not criteria:
        raise ValueError("Evaluation criteria are required")
    total = sum(item.weight for item in criteria)
    if abs(total - 1.0) > 0.000001:
        raise ValueError(f"Evaluation criteria weights must sum to 1.0, got {total:.6f}")
    for item in criteria:
        if not item.name.strip():
            raise ValueError("Evaluation criteria name is required")
        if item.weight < 0.0:
            raise ValueError(f"Evaluation criteria weight cannot be negative: {item.name}")
