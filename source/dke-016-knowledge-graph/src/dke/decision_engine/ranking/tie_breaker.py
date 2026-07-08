from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.evaluation import EvaluatedAlternative


class TieBreaker:
    RECOMMENDATION_ORDER = {
        "strong": 3,
        "moderate": 2,
        "weak": 1,
        "not_recommended": 0,
    }

    def sort_key(self, item: tuple[EvaluatedAlternative, float]) -> tuple[float, float, float, int, int, str]:
        evaluated, ranking_score = item
        alternative = evaluated.alternative
        return (
            ranking_score,
            evaluated.overall_score,
            evaluated.confidence,
            self.RECOMMENDATION_ORDER.get(evaluated.recommendation_level, -1),
            len(alternative.supporting_evidence),
            self._lexicographic_inverse(alternative.alternative_id),
        )

    def ordered(self, scored: tuple[tuple[EvaluatedAlternative, float], ...]) -> tuple[tuple[EvaluatedAlternative, float], ...]:
        return tuple(sorted(scored, key=self.sort_key, reverse=True))

    def tie_breaker_score(self, evaluated: EvaluatedAlternative) -> float:
        alternative = evaluated.alternative
        score = (
            evaluated.overall_score * 0.35
            + evaluated.confidence * 0.25
            + (self.RECOMMENDATION_ORDER.get(evaluated.recommendation_level, 0) / 3.0) * 0.2
            + min(1.0, len(alternative.supporting_evidence) / 4.0) * 0.1
            + max(0.0, 1.0 - (len(alternative.risks) * 0.2)) * 0.1
        )
        return clamp_confidence(score)

    def _lexicographic_inverse(self, value: str) -> str:
        # Reverse sorting is used for numeric tie-breakers; invert text so lower IDs win deterministically.
        return "".join(chr(255 - ord(char)) for char in value)
