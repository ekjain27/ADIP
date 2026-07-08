from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.explanation import DecisionExplanation


class ConstraintOptimizer:
    CONSTRAINT_KEYWORDS = {
        "budget": ("budget", "cost", "spend"),
        "time": ("time", "deadline", "schedule", "speed"),
        "policy": ("policy", "compliance", "standard"),
        "technical": ("technical", "architecture", "integration"),
        "business": ("business", "value", "return"),
        "risk": ("risk", "failure", "uncertain"),
    }

    def optimize(self, explanation: DecisionExplanation) -> dict[str, object]:
        text = self._text(explanation)
        improvements = []
        violations = []
        matched = 0
        for constraint_type, keywords in self.CONSTRAINT_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                matched += 1
                improvements.append(f"Improve {constraint_type} handling through targeted validation and mitigation.")
                if constraint_type == "risk" and any(token in text for token in ("critical", "severe", "blocked")):
                    violations.append(f"Potential {constraint_type} constraint violation requires review.")
        satisfaction = clamp_confidence(0.55 + (matched * 0.06) - (len(violations) * 0.15))
        return {
            "improvements": tuple(improvements or ("No explicit constraint improvements were detected.",)),
            "violations": tuple(violations),
            "satisfaction_score": satisfaction,
        }

    def _text(self, explanation: DecisionExplanation) -> str:
        return " ".join(
            (
                explanation.summary,
                explanation.reasoning,
                explanation.risk_explanation,
                explanation.recommendation_explanation,
            )
        ).lower()
