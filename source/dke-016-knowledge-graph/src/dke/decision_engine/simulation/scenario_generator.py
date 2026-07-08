from __future__ import annotations

from hashlib import sha256

from decision_engine.core.models import clamp_confidence
from decision_engine.ranking import RankedAlternative

from .models import Scenario


class ScenarioGenerator:
    def generate(self, ranked_alternative: RankedAlternative) -> tuple[Scenario, ...]:
        probabilities = self._normalized_probabilities(ranked_alternative)
        assumptions = ranked_alternative.evaluated_alternative.alternative.assumptions or (
            "Simulation assumes the ranked alternative is selected.",
        )
        return (
            self._scenario(
                ranked_alternative,
                "best_case",
                "Best-case outcome",
                "The decision performs better than expected and advantages are realized quickly.",
                assumptions,
                probabilities["best_case"],
                self._impact(ranked_alternative, 0.18),
                self._confidence(ranked_alternative, 0.08),
            ),
            self._scenario(
                ranked_alternative,
                "expected_case",
                "Expected-case outcome",
                "The decision follows the most likely path based on ranking and evaluation signals.",
                assumptions,
                probabilities["expected_case"],
                self._impact(ranked_alternative, 0.0),
                self._confidence(ranked_alternative, 0.0),
            ),
            self._scenario(
                ranked_alternative,
                "worst_case",
                "Worst-case outcome",
                "Known risks materialize and reduce the value of the selected decision.",
                assumptions,
                probabilities["worst_case"],
                self._impact(ranked_alternative, -0.22),
                self._confidence(ranked_alternative, -0.12),
            ),
        )

    def _normalized_probabilities(self, ranked_alternative: RankedAlternative) -> dict[str, float]:
        confidence = ranked_alternative.evaluated_alternative.confidence
        recommendation = ranked_alternative.evaluated_alternative.recommendation_level
        risk_count = len(ranked_alternative.evaluated_alternative.alternative.risks)
        best = 0.25
        expected = 0.50 + ((confidence - 0.5) * 0.12)
        worst = 0.25 + min(0.15, risk_count * 0.03)
        if recommendation == "strong":
            best += 0.04
            expected += 0.04
            worst -= 0.04
        elif recommendation == "not_recommended":
            best -= 0.04
            expected -= 0.03
            worst += 0.07
        values = {
            "best_case": max(0.05, best),
            "expected_case": max(0.05, expected),
            "worst_case": max(0.05, worst),
        }
        total = sum(values.values())
        normalized = {key: round(value / total, 6) for key, value in values.items()}
        drift = round(1.0 - sum(normalized.values()), 6)
        normalized["expected_case"] = round(normalized["expected_case"] + drift, 6)
        return normalized

    def _scenario(
        self,
        ranked_alternative: RankedAlternative,
        scenario_type: str,
        title: str,
        description: str,
        assumptions: tuple[str, ...],
        probability: float,
        impact_score: float,
        confidence: float,
    ) -> Scenario:
        return Scenario(
            scenario_id=self._stable_id(ranked_alternative.alternative_id, scenario_type),
            scenario_type=scenario_type,
            title=title,
            description=description,
            assumptions=assumptions,
            probability=clamp_confidence(probability),
            impact_score=clamp_confidence(impact_score),
            confidence=clamp_confidence(confidence),
            metadata={"alternative_id": ranked_alternative.alternative_id, "rank": ranked_alternative.rank},
        )

    def _impact(self, ranked_alternative: RankedAlternative, delta: float) -> float:
        base = (ranked_alternative.ranking_score + ranked_alternative.overall_score) / 2.0
        return clamp_confidence(base + delta)

    def _confidence(self, ranked_alternative: RankedAlternative, delta: float) -> float:
        return clamp_confidence(ranked_alternative.evaluated_alternative.confidence + delta)

    def _stable_id(self, alternative_id: str, scenario_type: str) -> str:
        digest = sha256(f"{alternative_id}|{scenario_type}".encode("utf-8")).hexdigest()[:16]
        return f"scenario-{digest}"
