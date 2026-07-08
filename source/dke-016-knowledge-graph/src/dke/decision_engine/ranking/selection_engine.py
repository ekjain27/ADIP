from __future__ import annotations

from decision_engine.evaluation import EvaluatedAlternative

from .models import RankedAlternative
from .tie_breaker import TieBreaker


class SelectionEngine:
    DEFAULT_TOP_N = 3
    SELECTION_STRATEGY = "top_ranked_selection"

    def __init__(self, tie_breaker: TieBreaker | None = None) -> None:
        self.tie_breaker = tie_breaker or TieBreaker()

    def build_ranked(
        self,
        ordered: tuple[tuple[EvaluatedAlternative, float], ...],
        top_n: int = DEFAULT_TOP_N,
    ) -> tuple[RankedAlternative, ...]:
        if not ordered:
            return ()
        safe_top_n = max(0, top_n)
        ranked = []
        for index, (evaluated, ranking_score) in enumerate(ordered, start=1):
            status = self._status(index, safe_top_n)
            ranked.append(
                RankedAlternative(
                    rank=index,
                    evaluated_alternative=evaluated,
                    alternative_id=evaluated.alternative.alternative_id,
                    overall_score=evaluated.overall_score,
                    ranking_score=ranking_score,
                    selection_status=status,
                    tie_breaker_score=self.tie_breaker.tie_breaker_score(evaluated),
                    explanation=self._explanation(index, status, ranking_score),
                    metadata={"recommendation_level": evaluated.recommendation_level},
                )
            )
        return tuple(ranked)

    def selected(self, ranked: tuple[RankedAlternative, ...]) -> RankedAlternative | None:
        return ranked[0] if ranked else None

    def top(self, ranked: tuple[RankedAlternative, ...], top_n: int = DEFAULT_TOP_N) -> tuple[RankedAlternative, ...]:
        return ranked[: max(0, top_n)]

    def _status(self, rank: int, top_n: int) -> str:
        if rank == 1:
            return "selected"
        if rank <= top_n:
            return "shortlisted"
        return "rejected"

    def _explanation(self, rank: int, status: str, ranking_score: float) -> str:
        return f"Rank {rank} assigned with ranking score {ranking_score:.3f}; status is {status}."
