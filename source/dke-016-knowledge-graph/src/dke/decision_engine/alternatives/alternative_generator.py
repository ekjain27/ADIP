from __future__ import annotations

import logging
from typing import Any

from decision_engine.core import Constraint, DecisionState, Evidence, Goal
from decision_engine.core.models import clamp_confidence

from .alternative_builder import AlternativeBuilder
from .alternative_package import AlternativePackageBuilder
from .models import AlternativeDecisionPackage

logger = logging.getLogger(__name__)


class AlternativeGenerator:
    MIN_ALTERNATIVES = 3
    MAX_ALTERNATIVES = 7
    STRATEGY = "deterministic_rule_based"

    def __init__(
        self,
        builder: AlternativeBuilder | None = None,
        package_builder: AlternativePackageBuilder | None = None,
    ) -> None:
        self.builder = builder or AlternativeBuilder()
        self.package_builder = package_builder or AlternativePackageBuilder()

    def generate(self, decision_state: DecisionState) -> AlternativeDecisionPackage:
        if not isinstance(decision_state, DecisionState):
            raise ValueError("AlternativeGenerator.generate requires a DIE-001 DecisionState")

        logger.info("Generating alternatives from decision state")
        candidates = self._candidate_specs(decision_state)
        alternatives = []
        seen_descriptions: set[str] = set()
        for spec in candidates:
            description_key = spec["description"].strip().lower()
            if description_key in seen_descriptions:
                continue
            seen_descriptions.add(description_key)
            alternatives.append(self.builder.build(**spec))
            if len(alternatives) >= self.MAX_ALTERNATIVES:
                break

        if len(alternatives) < self.MIN_ALTERNATIVES:
            raise ValueError("Alternative generation produced fewer than 3 alternatives")

        return self.package_builder.build(
            tuple(alternatives),
            decision_state=decision_state,
            generation_strategy=self.STRATEGY,
            metadata={"decision_state_metadata": dict(decision_state.metadata)},
        )

    def _candidate_specs(self, decision_state: DecisionState) -> list[dict[str, Any]]:
        evidence = decision_state.evidence
        goals = decision_state.goals
        constraints = decision_state.constraints
        primary_goal = self._primary_goal(goals)
        confidence = self._base_confidence(decision_state)

        specs = [
            self._balanced_spec(primary_goal, evidence, goals, constraints, confidence, decision_state.assumptions),
            self._evidence_led_spec(primary_goal, evidence, goals, constraints, confidence),
            self._constraint_first_spec(primary_goal, evidence, goals, constraints, confidence),
            self._risk_reduction_spec(primary_goal, evidence, goals, constraints, confidence),
            self._phased_spec(primary_goal, evidence, goals, constraints, confidence),
            self._defer_spec(primary_goal, evidence, goals, constraints, confidence),
            self._minimal_change_spec(primary_goal, evidence, goals, constraints, confidence),
        ]
        return specs

    def _balanced_spec(
        self,
        primary_goal: str,
        evidence: tuple[Evidence, ...],
        goals: tuple[Goal, ...],
        constraints: tuple[Constraint, ...],
        confidence: float,
        assumptions: tuple[str, ...],
    ) -> dict[str, Any]:
        return {
            "title": "Balanced evidence-guided decision",
            "description": f"Pursue the option that best satisfies '{primary_goal}' while balancing available evidence and constraints.",
            "supporting_evidence": self._top_evidence(evidence),
            "supporting_goals": goals,
            "supporting_constraints": constraints,
            "assumptions": assumptions or ("Available evidence is representative enough for initial alternative generation.",),
            "confidence": confidence,
            "feasibility": confidence,
            "risks": self._constraint_risks(constraints) or ("May underweight unknown factors not present in the context.",),
            "advantages": ("Balances goals, evidence, and constraints.", "Provides a general-purpose baseline alternative."),
            "disadvantages": ("May be less decisive than a specialized strategy.",),
            "metadata": {"strategy": "balanced"},
        }

    def _evidence_led_spec(
        self,
        primary_goal: str,
        evidence: tuple[Evidence, ...],
        goals: tuple[Goal, ...],
        constraints: tuple[Constraint, ...],
        confidence: float,
    ) -> dict[str, Any]:
        return {
            "title": "Evidence-led decision",
            "description": f"Prioritize the decision path with the strongest evidence support for '{primary_goal}'.",
            "supporting_evidence": self._top_evidence(evidence, limit=3),
            "supporting_goals": goals[:2],
            "supporting_constraints": constraints[:2],
            "assumptions": ("Higher-confidence evidence should carry more weight than weak or missing signals.",),
            "confidence": self._adjust(confidence, 0.05),
            "feasibility": confidence,
            "risks": ("Could miss strategic factors that are not strongly evidenced yet.",),
            "advantages": ("Maximizes traceability to the context package.", "Works well when evidence quality is high."),
            "disadvantages": ("Sensitive to evidence gaps or biased retrieval results.",),
            "metadata": {"strategy": "evidence_led"},
        }

    def _constraint_first_spec(
        self,
        primary_goal: str,
        evidence: tuple[Evidence, ...],
        goals: tuple[Goal, ...],
        constraints: tuple[Constraint, ...],
        confidence: float,
    ) -> dict[str, Any]:
        return {
            "title": "Constraint-first decision",
            "description": f"Choose the feasible path for '{primary_goal}' that most strictly satisfies known constraints.",
            "supporting_evidence": self._top_evidence(evidence, limit=2),
            "supporting_goals": goals[:2],
            "supporting_constraints": constraints,
            "assumptions": ("Constraints represent hard boundaries unless later evaluation relaxes them.",),
            "confidence": self._adjust(confidence, -0.02),
            "feasibility": self._adjust(confidence, 0.08),
            "risks": self._constraint_risks(constraints) or ("May optimize for constraints at the expense of upside.",),
            "advantages": ("Reduces compliance, policy, and implementation surprises.",),
            "disadvantages": ("Can be conservative when constraints are only weak preferences.",),
            "metadata": {"strategy": "constraint_first"},
        }

    def _risk_reduction_spec(
        self,
        primary_goal: str,
        evidence: tuple[Evidence, ...],
        goals: tuple[Goal, ...],
        constraints: tuple[Constraint, ...],
        confidence: float,
    ) -> dict[str, Any]:
        return {
            "title": "Risk-reduction decision",
            "description": f"Select a lower-risk path for '{primary_goal}' and explicitly minimize reversible or high-impact failures.",
            "supporting_evidence": self._top_evidence(evidence, limit=2),
            "supporting_goals": goals,
            "supporting_constraints": constraints,
            "assumptions": ("Reducing downside exposure is preferable before optimizing for upside.",),
            "confidence": self._adjust(confidence, -0.04),
            "feasibility": self._adjust(confidence, 0.04),
            "risks": ("May delay aggressive value capture.", "May require additional validation before final selection."),
            "advantages": ("Improves resilience under uncertainty.", "Pairs naturally with later evaluation and audit stages."),
            "disadvantages": ("May be slower than direct execution.",),
            "metadata": {"strategy": "risk_reduction"},
        }

    def _phased_spec(
        self,
        primary_goal: str,
        evidence: tuple[Evidence, ...],
        goals: tuple[Goal, ...],
        constraints: tuple[Constraint, ...],
        confidence: float,
    ) -> dict[str, Any]:
        return {
            "title": "Phased pilot decision",
            "description": f"Run a limited pilot toward '{primary_goal}' before committing to the full decision.",
            "supporting_evidence": self._top_evidence(evidence, limit=2),
            "supporting_goals": goals[:2],
            "supporting_constraints": constraints[:3],
            "assumptions": ("A smaller reversible step can produce useful new evidence.",),
            "confidence": self._adjust(confidence, -0.01),
            "feasibility": self._adjust(confidence, 0.1),
            "risks": ("Pilot results may not fully represent production conditions.",),
            "advantages": ("Creates learning before full commitment.", "Limits downside if assumptions are wrong."),
            "disadvantages": ("Adds an intermediate step and may extend timeline.",),
            "metadata": {"strategy": "phased_pilot"},
        }

    def _defer_spec(
        self,
        primary_goal: str,
        evidence: tuple[Evidence, ...],
        goals: tuple[Goal, ...],
        constraints: tuple[Constraint, ...],
        confidence: float,
    ) -> dict[str, Any]:
        return {
            "title": "Defer for more evidence",
            "description": f"Delay the final decision on '{primary_goal}' until missing or weak evidence is strengthened.",
            "supporting_evidence": self._top_evidence(evidence, limit=1),
            "supporting_goals": goals[:1],
            "supporting_constraints": constraints,
            "assumptions": ("Current uncertainty is high enough that additional context may change the outcome.",),
            "confidence": self._adjust(1.0 - confidence, -0.1),
            "feasibility": 0.6,
            "risks": ("Decision latency may create opportunity cost.",),
            "advantages": ("Reduces chance of acting on incomplete context.",),
            "disadvantages": ("Does not immediately satisfy the decision objective.",),
            "metadata": {"strategy": "defer"},
        }

    def _minimal_change_spec(
        self,
        primary_goal: str,
        evidence: tuple[Evidence, ...],
        goals: tuple[Goal, ...],
        constraints: tuple[Constraint, ...],
        confidence: float,
    ) -> dict[str, Any]:
        return {
            "title": "Minimal-change decision",
            "description": f"Choose the lowest-disruption path that still advances '{primary_goal}'.",
            "supporting_evidence": self._top_evidence(evidence, limit=2),
            "supporting_goals": goals[:1],
            "supporting_constraints": constraints[:2],
            "assumptions": ("Operational continuity is valuable when context is incomplete.",),
            "confidence": self._adjust(confidence, -0.03),
            "feasibility": self._adjust(confidence, 0.12),
            "risks": ("Incremental progress may be insufficient for urgent objectives.",),
            "advantages": ("Low disruption and easy rollback.",),
            "disadvantages": ("May leave larger strategic improvements unrealized.",),
            "metadata": {"strategy": "minimal_change"},
        }

    def _primary_goal(self, goals: tuple[Goal, ...]) -> str:
        for goal in goals:
            if goal.priority == "primary":
                return goal.objective
        if goals:
            return goals[0].objective
        return "the decision objective"

    def _base_confidence(self, decision_state: DecisionState) -> float:
        if decision_state.confidence:
            return clamp_confidence(decision_state.confidence)
        if decision_state.evidence:
            return clamp_confidence(sum(item.confidence for item in decision_state.evidence) / len(decision_state.evidence))
        return 0.35

    def _top_evidence(self, evidence: tuple[Evidence, ...], limit: int = 2) -> tuple[Evidence, ...]:
        return tuple(sorted(evidence, key=lambda item: item.confidence, reverse=True)[:limit])

    def _constraint_risks(self, constraints: tuple[Constraint, ...]) -> tuple[str, ...]:
        return tuple(f"Must account for {constraint.type} constraint severity {constraint.severity}." for constraint in constraints[:3])

    def _adjust(self, confidence: float, delta: float) -> float:
        return clamp_confidence(confidence + delta)
