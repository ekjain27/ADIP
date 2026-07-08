from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.ranking import RankedAlternative

from .models import Scenario


class ImpactAnalyzer:
    SEVERE_RISK_KEYWORDS = (
        "blocked",
        "critical",
        "severe",
        "illegal",
        "noncompliant",
        "failure",
        "high-impact",
        "cannot",
        "deadline",
    )

    def risk_impact(self, ranked_alternative: RankedAlternative) -> float:
        risks = ranked_alternative.evaluated_alternative.alternative.risks
        risk_count = len(risks)
        severe_count = self._severe_risk_count(risks)
        score = 1.0 - min(0.65, risk_count * 0.1) - min(0.5, severe_count * 0.2)
        return clamp_confidence(score)

    def confidence_impact(self, ranked_alternative: RankedAlternative, scenarios: tuple[Scenario, ...] = ()) -> float:
        base_confidence = ranked_alternative.evaluated_alternative.confidence
        if scenarios:
            scenario_confidence = sum(item.confidence * item.probability for item in scenarios)
            return clamp_confidence((base_confidence + scenario_confidence) / 2.0)
        return clamp_confidence(base_confidence)

    def _severe_risk_count(self, risks: tuple[str, ...]) -> int:
        text = " ".join(risks).lower()
        return sum(1 for keyword in self.SEVERE_RISK_KEYWORDS if keyword in text)
