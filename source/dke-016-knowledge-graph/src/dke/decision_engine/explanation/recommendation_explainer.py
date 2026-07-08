from __future__ import annotations

from decision_engine.simulation import SimulatedOutcome


class RecommendationExplainer:
    def explain(self, outcome: SimulatedOutcome, selected: bool = False) -> str:
        ranked = outcome.ranked_alternative
        evaluated = ranked.evaluated_alternative
        status = "selected" if selected else ranked.selection_status
        return (
            f"This alternative is {status} with rank {ranked.rank}, ranking score {ranked.ranking_score:.3f}, "
            f"evaluation score {evaluated.overall_score:.3f}, recommendation level '{evaluated.recommendation_level}', "
            f"and simulation outcome score {outcome.outcome_score:.3f}. "
            "The recommendation balances ranking strength, evaluation criteria, simulated outcomes, and known tradeoffs."
        )
