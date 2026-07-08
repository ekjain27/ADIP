from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.uncertainty import UncertaintyResult

from .models import ScenarioDefinition, ScenarioEvaluation


class ScenarioEvaluator:
    def evaluate(self, uncertainty_result: UncertaintyResult, scenario: ScenarioDefinition) -> ScenarioEvaluation:
        score_delta = float(scenario.metadata.get("score_delta", 0.0))
        risk_delta = float(scenario.metadata.get("risk_delta", 0.0))
        confidence_delta = float(scenario.metadata.get("confidence_delta", 0.0))
        robustness_delta = float(scenario.metadata.get("robustness_delta", 0.0))
        base_score = uncertainty_result.reliability_score
        risk_score = clamp_confidence(1.0 - uncertainty_result.uncertainty_score - risk_delta)
        confidence = clamp_confidence((uncertainty_result.confidence_interval[0] + uncertainty_result.confidence_interval[1]) / 2.0 + confidence_delta)
        robustness = clamp_confidence(uncertainty_result.robustness.robustness_score + robustness_delta)
        decision_score = clamp_confidence((base_score * 0.45) + (risk_score * 0.2) + (confidence * 0.2) + (robustness * 0.15) + score_delta)
        return ScenarioEvaluation(
            scenario=scenario,
            alternative_id=uncertainty_result.alternative_id,
            decision_score=decision_score,
            risk_score=risk_score,
            confidence=confidence,
            robustness=robustness,
            explanation=(
                f"{uncertainty_result.alternative_id} scores {decision_score:.3f} under {scenario.name} "
                f"with risk {risk_score:.3f}, confidence {confidence:.3f}, robustness {robustness:.3f}."
            ),
            metadata={"source_reliability": uncertainty_result.reliability_score},
        )
