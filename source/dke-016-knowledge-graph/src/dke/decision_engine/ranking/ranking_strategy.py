from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.evaluation import EvaluatedAlternative


class RankingStrategy:
    STRATEGY_NAME = "deterministic_weighted_rank"
    RECOMMENDATION_BOOSTS = {
        "strong": 0.05,
        "moderate": 0.025,
        "weak": 0.0,
        "not_recommended": -0.05,
    }

    def score(self, evaluated: EvaluatedAlternative) -> float:
        alternative = evaluated.alternative
        base = evaluated.overall_score * 0.72
        confidence_signal = evaluated.confidence * 0.12
        evidence_signal = min(1.0, len(alternative.supporting_evidence) / 4.0) * 0.06
        risk_signal = max(0.0, 1.0 - (len(alternative.risks) * 0.15)) * 0.05
        advantage_signal = self._advantage_balance(alternative.advantages, alternative.disadvantages) * 0.05
        boost = self.RECOMMENDATION_BOOSTS.get(evaluated.recommendation_level, -0.05)
        return clamp_confidence(base + confidence_signal + evidence_signal + risk_signal + advantage_signal + boost)

    def _advantage_balance(self, advantages: tuple[str, ...], disadvantages: tuple[str, ...]) -> float:
        if not advantages and not disadvantages:
            return 0.5
        return clamp_confidence((len(advantages) + 1) / (len(advantages) + len(disadvantages) + 2))
