from __future__ import annotations

from decision_engine.simulation import SimulatedOutcome


class RiskExplainer:
    SEVERE_KEYWORDS = ("critical", "severe", "blocked", "failure", "noncompliant", "deadline")

    def explain(self, outcome: SimulatedOutcome) -> str:
        risks = outcome.ranked_alternative.evaluated_alternative.alternative.risks
        if not risks:
            return f"No explicit risks were listed; risk impact remains high at {outcome.risk_impact:.3f}."
        severe = self._severe_count(risks)
        severity = "elevated" if severe else "manageable"
        return (
            f"The alternative has {len(risks)} risk item(s), with {severe} severe signal(s). "
            f"Risk severity is {severity}; risk impact score is {outcome.risk_impact:.3f}. "
            "Mitigation should focus on validating the listed risks before commitment."
        )

    def risk_refs(self, outcome: SimulatedOutcome) -> tuple[str, ...]:
        return outcome.ranked_alternative.evaluated_alternative.alternative.risks

    def _severe_count(self, risks: tuple[str, ...]) -> int:
        text = " ".join(risks).lower()
        return sum(1 for keyword in self.SEVERE_KEYWORDS if keyword in text)
