from __future__ import annotations

from decision_engine.alternatives import AlternativeDecision
from decision_engine.core.models import clamp_confidence

from .criteria import default_criteria, validate_criteria_weights
from .models import EvaluationCriteria, EvaluationScore


class ScoringEngine:
    SEVERE_RISK_KEYWORDS = (
        "blocked",
        "critical",
        "severe",
        "illegal",
        "noncompliant",
        "failure",
        "high-impact",
        "cannot",
    )

    def __init__(self, criteria: tuple[EvaluationCriteria, ...] | None = None) -> None:
        self.criteria = criteria or default_criteria()
        validate_criteria_weights(self.criteria)

    def score(self, alternative: AlternativeDecision) -> tuple[EvaluationScore, ...]:
        if not isinstance(alternative, AlternativeDecision):
            raise ValueError("ScoringEngine.score requires an AlternativeDecision")
        return tuple(self._score_criterion(alternative, criterion) for criterion in self.criteria)

    def overall_score(self, scores: tuple[EvaluationScore, ...]) -> float:
        return clamp_confidence(sum(score.weighted_score for score in scores))

    def _score_criterion(self, alternative: AlternativeDecision, criterion: EvaluationCriteria) -> EvaluationScore:
        score, explanation = self._raw_score(alternative, criterion.name)
        normalized = clamp_confidence(score, default=0.5)
        weighted = round(normalized * criterion.weight, 6)
        return EvaluationScore(
            criterion=criterion.name,
            score=normalized,
            weight=criterion.weight,
            weighted_score=weighted,
            explanation=explanation,
            metadata={"description": criterion.description},
        )

    def _raw_score(self, alternative: AlternativeDecision, criterion: str) -> tuple[float, str]:
        if criterion == "feasibility":
            return self._score_feasibility(alternative)
        if criterion == "confidence":
            return clamp_confidence(alternative.confidence), "Uses the alternative confidence directly."
        if criterion == "goal_alignment":
            return self._score_goal_alignment(alternative)
        if criterion == "constraint_satisfaction":
            return self._score_constraint_satisfaction(alternative)
        if criterion == "evidence_support":
            return self._score_evidence_support(alternative)
        if criterion == "risk_balance":
            return self._score_risk_balance(alternative)
        if criterion == "advantage_balance":
            return self._score_advantage_balance(alternative)
        return 0.5, f"Unknown criterion {criterion}; using neutral default."

    def _score_feasibility(self, alternative: AlternativeDecision) -> tuple[float, str]:
        if isinstance(alternative.feasibility, (int, float)):
            return alternative.feasibility, "Uses the alternative feasibility directly."
        return alternative.confidence or 0.5, "Derived feasibility from confidence or neutral default."

    def _score_goal_alignment(self, alternative: AlternativeDecision) -> tuple[float, str]:
        count = len(alternative.supporting_goals)
        if count == 0:
            return 0.4, "No supporting goals were linked."
        return min(1.0, 0.55 + (count * 0.15)), f"{count} supporting goal(s) linked."

    def _score_constraint_satisfaction(self, alternative: AlternativeDecision) -> tuple[float, str]:
        count = len(alternative.supporting_constraints)
        severe_risks = self._severe_risk_count(alternative)
        if count == 0:
            base = 0.45
        else:
            base = min(0.95, 0.6 + (count * 0.1))
        penalty = min(0.5, severe_risks * 0.2)
        return base - penalty, f"{count} constraint(s) linked; {severe_risks} severe risk signal(s)."

    def _score_evidence_support(self, alternative: AlternativeDecision) -> tuple[float, str]:
        count = len(alternative.supporting_evidence)
        if count == 0:
            return 0.35, "No supporting evidence was linked."
        return min(1.0, 0.45 + (count * 0.18)), f"{count} supporting evidence item(s) linked."

    def _score_risk_balance(self, alternative: AlternativeDecision) -> tuple[float, str]:
        risk_count = len(alternative.risks)
        severe_risk_count = self._severe_risk_count(alternative)
        score = 1.0 - min(0.75, risk_count * 0.12) - min(0.5, severe_risk_count * 0.2)
        return score, f"{risk_count} risk(s), including {severe_risk_count} severe signal(s)."

    def _score_advantage_balance(self, alternative: AlternativeDecision) -> tuple[float, str]:
        advantages = len(alternative.advantages)
        disadvantages = len(alternative.disadvantages)
        if advantages == 0 and disadvantages == 0:
            return 0.5, "No advantages or disadvantages were listed."
        ratio = (advantages + 1) / (advantages + disadvantages + 2)
        return ratio, f"{advantages} advantage(s) and {disadvantages} disadvantage(s)."

    def _severe_risk_count(self, alternative: AlternativeDecision) -> int:
        risk_text = " ".join(alternative.risks).lower()
        return sum(1 for keyword in self.SEVERE_RISK_KEYWORDS if keyword in risk_text)
