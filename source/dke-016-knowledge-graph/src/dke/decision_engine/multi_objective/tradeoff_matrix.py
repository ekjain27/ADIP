from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import ObjectiveScore, TradeoffMatrix


class TradeoffMatrixBuilder:
    def build(self, objective_scores: tuple[ObjectiveScore, ...]) -> TradeoffMatrix:
        alternatives = tuple(score.alternative_id for score in objective_scores)
        objectives = tuple(objective_scores[0].scores.keys()) if objective_scores else ()
        matrix = {
            score.alternative_id: {name: clamp_confidence(value) for name, value in score.scores.items()}
            for score in objective_scores
        }
        pairwise = {
            left.alternative_id: {
                right.alternative_id: self._distance(left, right, objectives)
                for right in objective_scores
                if right.alternative_id != left.alternative_id
            }
            for left in objective_scores
        }
        return TradeoffMatrix(
            alternatives=alternatives,
            objectives=objectives,
            matrix=matrix,
            pairwise_tradeoffs=pairwise,
            metadata={"alternative_count": len(alternatives), "objective_count": len(objectives)},
        )

    def _distance(self, left: ObjectiveScore, right: ObjectiveScore, objectives: tuple[str, ...]) -> float:
        if not objectives:
            return 0.0
        total = sum(abs(left.scores.get(name, 0.0) - right.scores.get(name, 0.0)) for name in objectives)
        return clamp_confidence(total / len(objectives))
