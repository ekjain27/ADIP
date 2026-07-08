from __future__ import annotations

import logging
from hashlib import sha256

from decision_engine.core.models import clamp_confidence
from decision_engine.simulation import SimulatedOutcome, SimulationDecisionPackage

from .evidence_explainer import EvidenceExplainer
from .explanation_package import ExplanationPackageBuilder
from .models import DecisionExplanation, ExplanationDecisionPackage, ExplanationSection
from .recommendation_explainer import RecommendationExplainer
from .risk_explainer import RiskExplainer
from .scenario_explainer import ScenarioExplainer

logger = logging.getLogger(__name__)


class ExplanationGenerator:
    STRATEGY = "deterministic_rule_based_explanation"

    def __init__(
        self,
        evidence_explainer: EvidenceExplainer | None = None,
        risk_explainer: RiskExplainer | None = None,
        scenario_explainer: ScenarioExplainer | None = None,
        recommendation_explainer: RecommendationExplainer | None = None,
        package_builder: ExplanationPackageBuilder | None = None,
    ) -> None:
        self.evidence_explainer = evidence_explainer or EvidenceExplainer()
        self.risk_explainer = risk_explainer or RiskExplainer()
        self.scenario_explainer = scenario_explainer or ScenarioExplainer()
        self.recommendation_explainer = recommendation_explainer or RecommendationExplainer()
        self.package_builder = package_builder or ExplanationPackageBuilder()

    def explain(self, simulation_package: SimulationDecisionPackage) -> ExplanationDecisionPackage:
        if not isinstance(simulation_package, SimulationDecisionPackage):
            raise ValueError("ExplanationGenerator.explain requires a SimulationDecisionPackage")
        logger.info("Generating decision explanations")
        explanations = tuple(
            self._explain_outcome(
                outcome,
                selected=self._is_selected(outcome, simulation_package.selected_outcome),
            )
            for outcome in simulation_package.simulated_outcomes
        )
        selected = self._selected_explanation(explanations, simulation_package.selected_outcome)
        return self.package_builder.build(
            explanations,
            selected,
            explanation_strategy=self.STRATEGY,
            metadata={"source_simulation_strategy": simulation_package.simulation_strategy},
        )

    def _explain_outcome(self, outcome: SimulatedOutcome, selected: bool = False) -> DecisionExplanation:
        evidence_text = self.evidence_explainer.explain(outcome)
        risk_text = self.risk_explainer.explain(outcome)
        scenario_text = self.scenario_explainer.explain(outcome)
        recommendation_text = self.recommendation_explainer.explain(outcome, selected=selected)
        confidence = self._confidence(outcome)
        summary = self._summary(outcome, selected)
        reasoning = self._reasoning(outcome)
        sections = (
            self._section("evidence", "Evidence", evidence_text, confidence, self.evidence_explainer.evidence_refs(outcome)),
            self._section("risk", "Risk", risk_text, outcome.risk_impact, risk_refs=self.risk_explainer.risk_refs(outcome)),
            self._section("scenario", "Scenarios", scenario_text, outcome.outcome_score, scenario_refs=self.scenario_explainer.scenario_refs(outcome)),
            self._section("recommendation", "Recommendation", recommendation_text, confidence),
        )
        return DecisionExplanation(
            alternative_id=outcome.alternative_id,
            summary=summary,
            reasoning=reasoning,
            evidence_explanation=evidence_text,
            risk_explanation=risk_text,
            scenario_explanation=scenario_text,
            recommendation_explanation=recommendation_text,
            assumptions=self._assumptions(outcome),
            confidence=confidence,
            sections=sections,
            metadata={
                "rank": outcome.ranked_alternative.rank,
                "selected": selected,
                "outcome_score": outcome.outcome_score,
            },
        )

    def _confidence(self, outcome: SimulatedOutcome) -> float:
        scenario_average = sum(scenario.confidence for scenario in outcome.scenarios) / len(outcome.scenarios)
        ranked_confidence = outcome.ranked_alternative.evaluated_alternative.confidence
        value = (outcome.outcome_score + outcome.confidence_impact + scenario_average + ranked_confidence) / 4.0
        return clamp_confidence(value)

    def _summary(self, outcome: SimulatedOutcome, selected: bool) -> str:
        prefix = "Recommended decision" if selected else "Alternative decision"
        return f"{prefix} {outcome.alternative_id} has simulated outcome score {outcome.outcome_score:.3f}."

    def _reasoning(self, outcome: SimulatedOutcome) -> str:
        ranked = outcome.ranked_alternative
        evaluated = ranked.evaluated_alternative
        return (
            f"It is ranked {ranked.rank} with ranking score {ranked.ranking_score:.3f}, "
            f"evaluation score {evaluated.overall_score:.3f}, and simulation score {outcome.outcome_score:.3f}."
        )

    def _assumptions(self, outcome: SimulatedOutcome) -> tuple[str, ...]:
        assumptions = []
        for scenario in outcome.scenarios:
            assumptions.extend(scenario.assumptions)
        return tuple(dict.fromkeys(assumptions))

    def _section(
        self,
        section_key: str,
        title: str,
        content: str,
        confidence: float,
        evidence_refs: tuple[str, ...] = (),
        risk_refs: tuple[str, ...] = (),
        scenario_refs: tuple[str, ...] = (),
    ) -> ExplanationSection:
        return ExplanationSection(
            section_id=self._stable_section_id(section_key, content),
            title=title,
            content=content,
            evidence_refs=evidence_refs,
            risk_refs=risk_refs,
            scenario_refs=scenario_refs,
            confidence=clamp_confidence(confidence),
            metadata={"section_type": section_key},
        )

    def _stable_section_id(self, section_key: str, content: str) -> str:
        digest = sha256(f"{section_key}|{content}".encode("utf-8")).hexdigest()[:16]
        return f"section-{digest}"

    def _is_selected(self, outcome: SimulatedOutcome, selected_outcome: SimulatedOutcome | None) -> bool:
        return selected_outcome is not None and outcome.alternative_id == selected_outcome.alternative_id

    def _selected_explanation(
        self,
        explanations: tuple[DecisionExplanation, ...],
        selected_outcome: SimulatedOutcome | None,
    ) -> DecisionExplanation | None:
        if not explanations:
            return None
        if selected_outcome is not None:
            for explanation in explanations:
                if explanation.alternative_id == selected_outcome.alternative_id:
                    return explanation
        return explanations[0]
