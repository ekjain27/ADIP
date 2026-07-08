from __future__ import annotations

from decision_engine.evaluation import EvaluatedDecisionPackage

from .models import RankedAlternative, RankedDecisionPackage


class RankingValidator:
    VALID_SELECTION_STATUSES = {"selected", "shortlisted", "rejected"}

    def validate(
        self,
        package: RankedDecisionPackage,
        evaluated_package: EvaluatedDecisionPackage | None = None,
    ) -> None:
        if not isinstance(package, RankedDecisionPackage):
            raise ValueError("Expected RankedDecisionPackage")
        if package.total_ranked != len(package.ranked_alternatives):
            raise ValueError("total_ranked does not match ranked alternative count")
        if package.top_alternatives and len(package.top_alternatives) > package.total_ranked:
            raise ValueError("top_alternatives count cannot exceed total ranked alternatives")
        self._validate_ranks(package.ranked_alternatives)
        source_ids = {item.alternative.alternative_id for item in evaluated_package.evaluated_alternatives} if evaluated_package else set()
        for ranked in package.ranked_alternatives:
            self.validate_ranked_alternative(ranked, source_ids)
        if package.ranked_alternatives:
            if package.selected_alternative is None:
                raise ValueError("selected_alternative is required when ranked alternatives exist")
            if package.selected_alternative.rank != 1:
                raise ValueError("selected_alternative must be rank 1")
        elif package.selected_alternative is not None:
            raise ValueError("selected_alternative must be None when no alternatives exist")

    def validate_ranked_alternative(self, ranked: RankedAlternative, source_ids: set[str] | None = None) -> None:
        if ranked.rank < 1:
            raise ValueError("rank must be at least 1")
        if not 0.0 <= ranked.ranking_score <= 1.0:
            raise ValueError(f"ranking_score must be between 0 and 1 for {ranked.alternative_id}")
        if not 0.0 <= ranked.tie_breaker_score <= 1.0:
            raise ValueError(f"tie_breaker_score must be between 0 and 1 for {ranked.alternative_id}")
        if ranked.selection_status not in self.VALID_SELECTION_STATUSES:
            raise ValueError(f"Invalid selection_status: {ranked.selection_status}")
        if not ranked.evaluated_alternative:
            raise ValueError("RankedAlternative must link to an evaluated alternative")
        if ranked.alternative_id != ranked.evaluated_alternative.alternative.alternative_id:
            raise ValueError("RankedAlternative alternative_id does not match evaluated alternative")
        if source_ids is not None and source_ids and ranked.alternative_id not in source_ids:
            raise ValueError(f"Ranked alternative {ranked.alternative_id} is not in the source package")

    def _validate_ranks(self, ranked: tuple[RankedAlternative, ...]) -> None:
        ranks = [item.rank for item in ranked]
        duplicates = sorted({rank for rank in ranks if ranks.count(rank) > 1})
        if duplicates:
            raise ValueError(f"Duplicate ranks: {', '.join(str(rank) for rank in duplicates)}")
        expected = list(range(1, len(ranked) + 1))
        if ranks != expected:
            raise ValueError(f"Ranks must be sequential starting at 1; expected {expected}, got {ranks}")
