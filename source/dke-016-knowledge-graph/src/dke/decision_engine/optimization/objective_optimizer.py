from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.explanation import DecisionExplanation

from .models import OptimizationObjective


class ObjectiveOptimizer:
    DEFAULT_WEIGHTS = {
        "value": 0.25,
        "risk": 0.20,
        "confidence": 0.15,
        "goal_alignment": 0.15,
        "feasibility": 0.15,
        "constraints": 0.10,
    }

    def default_objectives(self) -> tuple[OptimizationObjective, ...]:
        normalized = self.normalize_weights(self.DEFAULT_WEIGHTS)
        return tuple(
            OptimizationObjective(
                objective_id=f"obj-{name}",
                name=name,
                weight=weight,
                target="minimize" if name in {"risk", "constraints"} else "maximize",
                priority="high" if name in {"value", "risk"} else "medium",
            )
            for name, weight in normalized.items()
        )

    def normalize_weights(self, weights: dict[str, float]) -> dict[str, float]:
        if not weights:
            raise ValueError("Objective weights are required")
        if any(value < 0 for value in weights.values()):
            raise ValueError("Objective weights cannot be negative")
        total = sum(weights.values())
        if total <= 0:
            raise ValueError("Objective weights must sum to a positive value")
        return {key: round(value / total, 6) for key, value in weights.items()}

    def optimize(
        self,
        explanation: DecisionExplanation,
        objectives: tuple[OptimizationObjective, ...] | None = None,
    ) -> dict[str, float]:
        active_objectives = objectives or self.default_objectives()
        base = explanation.confidence
        return {
            objective.name: self._objective_score(explanation, objective, base)
            for objective in active_objectives
        }

    def improvement_score(self, objective_results: dict[str, float], objectives: tuple[OptimizationObjective, ...]) -> float:
        weighted = sum(objective_results.get(objective.name, 0.0) * objective.weight for objective in objectives)
        return clamp_confidence(weighted)

    def _objective_score(
        self,
        explanation: DecisionExplanation,
        objective: OptimizationObjective,
        base: float,
    ) -> float:
        text = " ".join(
            (
                explanation.summary,
                explanation.reasoning,
                explanation.evidence_explanation,
                explanation.risk_explanation,
                explanation.scenario_explanation,
                explanation.recommendation_explanation,
            )
        ).lower()
        if objective.name == "risk":
            severe = sum(1 for token in ("critical", "severe", "blocked", "failure", "deadline") if token in text)
            return clamp_confidence(0.85 - (severe * 0.12))
        if objective.name == "confidence":
            return clamp_confidence(base + 0.08)
        if objective.name == "goal_alignment":
            return clamp_confidence(0.65 + (0.1 if "ranked" in text or "selected" in text else 0.0))
        if objective.name == "feasibility":
            return clamp_confidence(0.62 + (0.1 if "simulation" in text or "outcome" in text else 0.0))
        if objective.name == "constraints":
            return clamp_confidence(0.7 + (0.08 if "constraint" in text or "budget" in text or "policy" in text else 0.0))
        return clamp_confidence(base + 0.12)
