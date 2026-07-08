from __future__ import annotations

from decision_engine.core.models import clamp_confidence

from .models import ScenarioComparison, ScenarioEvaluation


class ScenarioComparator:
    VALID_RECOMMENDATIONS = {"strong", "moderate", "weak", "unstable"}

    def compare(self, alternative_id: str, evaluations: tuple[ScenarioEvaluation, ...]) -> ScenarioComparison:
        if not evaluations:
            return ScenarioComparison(alternative_id, (), 0.0, 0.0, 0.0, 0.0, "unstable")
        scores = [evaluation.decision_score for evaluation in evaluations]
        average = clamp_confidence(sum(scores) / len(scores))
        best = max(scores)
        worst = min(scores)
        stability = clamp_confidence(1.0 - (best - worst))
        recommendation = self._recommendation(average, stability)
        return ScenarioComparison(
            alternative_id=alternative_id,
            evaluations=evaluations,
            average_score=average,
            best_score=best,
            worst_score=worst,
            stability_score=stability,
            recommendation=recommendation,
            metadata={
                "explanation": (
                    f"Average score {average:.3f}; best {best:.3f}; worst {worst:.3f}; "
                    f"stability {stability:.3f}; recommendation {recommendation}."
                )
            },
        )

    def _recommendation(self, average: float, stability: float) -> str:
        if stability < 0.45:
            return "unstable"
        if average >= 0.75 and stability >= 0.7:
            return "strong"
        if average >= 0.6 and stability >= 0.55:
            return "moderate"
        if average >= 0.45:
            return "weak"
        return "unstable"
