from __future__ import annotations

from .models import ObjectiveScore, ParetoResult


class ParetoAnalyzer:
    def analyze(self, objective_scores: tuple[ObjectiveScore, ...]) -> tuple[ParetoResult, ...]:
        results: list[ParetoResult] = []
        for candidate in objective_scores:
            dominates = tuple(other.alternative_id for other in objective_scores if other != candidate and self._dominates(candidate, other))
            dominated_by = tuple(other.alternative_id for other in objective_scores if other != candidate and self._dominates(other, candidate))
            results.append(
                ParetoResult(
                    alternative_id=candidate.alternative_id,
                    dominates=dominates,
                    dominated_by=dominated_by,
                    is_pareto_optimal=not dominated_by,
                    pareto_rank=1 + len(dominated_by),
                    metadata={"dominance_count": len(dominates)},
                )
            )
        return tuple(results)

    def _dominates(self, left: ObjectiveScore, right: ObjectiveScore) -> bool:
        shared = tuple(name for name in left.scores if name in right.scores)
        if not shared:
            return False
        no_worse = all(left.scores[name] >= right.scores[name] for name in shared)
        strictly_better = any(left.scores[name] > right.scores[name] for name in shared)
        return no_worse and strictly_better
