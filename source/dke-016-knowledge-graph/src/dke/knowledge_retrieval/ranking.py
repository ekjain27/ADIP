from __future__ import annotations

from dataclasses import replace
from typing import Sequence

from .models import RetrievalResult, clamp_score


class WeightedRanker:
    def __init__(
        self,
        similarity_weight: float = 0.30,
        confidence_weight: float = 0.25,
        authority_weight: float = 0.15,
        freshness_weight: float = 0.10,
        connectivity_weight: float = 0.10,
        usage_weight: float = 0.10,
    ) -> None:
        self.weights = (
            similarity_weight,
            confidence_weight,
            authority_weight,
            freshness_weight,
            connectivity_weight,
            usage_weight,
        )

    def rank(self, results: Sequence[RetrievalResult]) -> Sequence[RetrievalResult]:
        ranked = []
        for result in results:
            weighted = (
                result.similarity * self.weights[0]
                + result.confidence * self.weights[1]
                + result.authority * self.weights[2]
                + result.freshness * self.weights[3]
                + result.connectivity * self.weights[4]
                + result.usage_frequency * self.weights[5]
            )
            ranked.append(replace(result, score=clamp_score(weighted)))
        return tuple(sorted(ranked, key=lambda item: (-item.score, item.node.id)))
