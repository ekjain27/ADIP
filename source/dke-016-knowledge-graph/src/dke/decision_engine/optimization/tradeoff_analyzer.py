from __future__ import annotations

from decision_engine.explanation import DecisionExplanation


class TradeoffAnalyzer:
    def analyze(self, explanation: DecisionExplanation) -> tuple[str, ...]:
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
        tradeoffs = []
        if "confidence" in text:
            tradeoffs.append("Higher confidence may require additional validation time or evidence collection.")
        if "risk" in text:
            tradeoffs.append("Lower risk may reduce upside or slow execution.")
        if "fast" in text or "speed" in text or "deadline" in text:
            tradeoffs.append("Higher speed can reduce accuracy if validation is compressed.")
        if "budget" in text or "cost" in text:
            tradeoffs.append("Lower cost may constrain implementation quality or optional safeguards.")
        return tuple(tradeoffs or ("No material optimization tradeoffs were detected from the explanation package.",))
