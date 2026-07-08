from __future__ import annotations

import logging

from decision_engine.evaluation import EvaluatedDecisionPackage

from .models import RankedDecisionPackage
from .ranking_package import RankingPackageBuilder
from .ranking_strategy import RankingStrategy
from .selection_engine import SelectionEngine
from .tie_breaker import TieBreaker

logger = logging.getLogger(__name__)


class DecisionRanker:
    def __init__(
        self,
        ranking_strategy: RankingStrategy | None = None,
        tie_breaker: TieBreaker | None = None,
        selection_engine: SelectionEngine | None = None,
        package_builder: RankingPackageBuilder | None = None,
    ) -> None:
        self.ranking_strategy = ranking_strategy or RankingStrategy()
        self.tie_breaker = tie_breaker or TieBreaker()
        self.selection_engine = selection_engine or SelectionEngine(self.tie_breaker)
        self.package_builder = package_builder or RankingPackageBuilder()

    def rank(self, evaluated_package: EvaluatedDecisionPackage, top_n: int = 3) -> RankedDecisionPackage:
        if not isinstance(evaluated_package, EvaluatedDecisionPackage):
            raise ValueError("DecisionRanker.rank requires an EvaluatedDecisionPackage")
        logger.info("Ranking evaluated decision alternatives")
        scored = tuple(
            (evaluated, self.ranking_strategy.score(evaluated))
            for evaluated in evaluated_package.evaluated_alternatives
        )
        ordered = self.tie_breaker.ordered(scored)
        ranked = self.selection_engine.build_ranked(ordered, top_n=top_n)
        selected = self.selection_engine.selected(ranked)
        top = self.selection_engine.top(ranked, top_n=top_n)
        return self.package_builder.build(
            ranked,
            selected,
            top,
            evaluated_package=evaluated_package,
            ranking_strategy=self.ranking_strategy.STRATEGY_NAME,
            selection_strategy=self.selection_engine.SELECTION_STRATEGY,
            metadata={"source_evaluation_strategy": evaluated_package.evaluation_strategy},
        )
