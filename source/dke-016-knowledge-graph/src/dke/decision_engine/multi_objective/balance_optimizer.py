from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import BalancedResult, ObjectiveScore, ParetoResult, TradeoffMatrix


class BalanceOptimizer:
    def optimize(
        self,
        objective_scores: tuple[ObjectiveScore, ...],
        pareto_results: tuple[ParetoResult, ...],
        tradeoff_matrix: TradeoffMatrix,
    ) -> tuple[BalancedResult, ...]:
        pareto_by_id = {result.alternative_id: result for result in pareto_results}
        return tuple(
            self._balance(score, pareto_by_id[score.alternative_id], tradeoff_matrix)
            for score in objective_scores
            if score.alternative_id in pareto_by_id
        )

    def select(self, balanced_results: tuple[BalancedResult, ...]) -> BalancedResult | None:
        if not balanced_results:
            return None
        return max(
            balanced_results,
            key=lambda result: (
                result.balance_score,
                result.objective_score.weighted_score,
                -result.pareto_result.pareto_rank,
                result.alternative_id,
            ),
        )

    def _balance(
        self,
        score: ObjectiveScore,
        pareto: ParetoResult,
        tradeoff_matrix: TradeoffMatrix,
    ) -> BalancedResult:
        values = tuple(score.scores.values())
        spread_penalty = (max(values) - min(values)) if values else 0.0
        evenness = clamp_confidence(1.0 - spread_penalty)
        pareto_score = 1.0 if pareto.is_pareto_optimal else clamp_confidence(1.0 / pareto.pareto_rank)
        tradeoff_score = self._tradeoff_score(score.alternative_id, tradeoff_matrix)
        balance_score = clamp_confidence((score.weighted_score * 0.50) + (evenness * 0.25) + (pareto_score * 0.15) + (tradeoff_score * 0.10))
        reason = "Selected for highest weighted objective balance." if pareto.is_pareto_optimal else "Balanced despite Pareto dominance tradeoffs."
        return BalancedResult(
            alternative_id=score.alternative_id,
            objective_score=score,
            pareto_result=pareto,
            balance_score=balance_score,
            tradeoff_score=tradeoff_score,
            selected_reason=reason,
            metadata={"evenness": evenness, "pareto_score": pareto_score},
        )

    def _tradeoff_score(self, alternative_id: str, tradeoff_matrix: TradeoffMatrix) -> float:
        distances = tuple(tradeoff_matrix.pairwise_tradeoffs.get(alternative_id, {}).values())
        if not distances:
            return 1.0
        return clamp_confidence(1.0 - (sum(distances) / len(distances)))
