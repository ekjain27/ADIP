import pytest

from decision_engine.adaptive import (
    AdaptationRuleEngine,
    AdaptiveBehaviorModel,
    AdaptiveDecisionEngine,
    AdaptiveValidator,
    ObjectivePriorityAdapter,
    RiskToleranceAdapter,
    ThresholdAdapter,
)
from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.governance import DecisionGovernanceEngine
from decision_engine.learning import DecisionLearningEngine
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.provenance import DecisionProvenanceEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import StrategicPlanningEngine
from decision_engine.temporal import TemporalDecisionEngine, TemporalDecisionPackage
from decision_engine.uncertainty import UncertaintyEngine


def test_default_behavior_profile_creation():
    profile = AdaptiveBehaviorModel().default_profile()
    assert profile.confidence_threshold == 0.70
    assert profile.risk_tolerance == 0.50
    assert profile.governance_sensitivity == 0.70
    assert sum(profile.objective_priorities.values()) == pytest.approx(1.0)


def test_adaptation_rules_load():
    rules = AdaptationRuleEngine().default_rules()
    assert len(rules) == 6
    assert all(rule.enabled for rule in rules)


def test_threshold_adapter_normalizes_value():
    value, adjustment = ThresholdAdapter().adjust(1.2, 0.4, 0.4)
    assert 0.0 <= value <= 1.0
    assert value > 0.012


def test_risk_tolerance_adapter_normalizes_value():
    value, adjustment = RiskToleranceAdapter().adjust(-0.1, 0.4, "conditional", 0.8)
    assert 0.0 <= value <= 1.0
    assert value == 0.0


def test_objective_priorities_normalize_to_one():
    priorities = ObjectivePriorityAdapter().normalize({"risk": 2.0, "compliance": 1.0, "value": 1.0})
    assert sum(priorities.values()) == pytest.approx(1.0)


def test_adaptive_engine_handles_empty_package():
    package = AdaptiveDecisionEngine().adapt(TemporalDecisionPackage((), None, "empty"))
    assert package.adaptive_results == ()
    assert package.selected_adaptive_result is None


def test_adaptive_engine_creates_adaptive_results():
    package = AdaptiveDecisionEngine().adapt(_temporal_package())
    assert package.adaptive_results
    assert package.selected_adaptive_result is not None
    assert package.selected_adaptive_result.behavior_profile.adjustments


def test_validator_catches_invalid_threshold():
    profile = AdaptiveBehaviorModel().default_profile()
    bad = type(profile)(
        profile.profile_id,
        1.2,
        profile.risk_tolerance,
        profile.governance_sensitivity,
        profile.objective_priorities,
        profile.checkpoint_frequency,
        profile.recommendation_mode,
        profile.adjustments,
        profile.metadata,
    )
    with pytest.raises(ValueError, match="confidence threshold must be between 0 and 1"):
        AdaptiveValidator().validate_profile(bad)


def test_validator_catches_invalid_objective_weights():
    profile = AdaptiveBehaviorModel().default_profile()
    bad = type(profile)(
        profile.profile_id,
        profile.confidence_threshold,
        profile.risk_tolerance,
        profile.governance_sensitivity,
        {"risk": 0.8, "value": 0.8},
        profile.checkpoint_frequency,
        profile.recommendation_mode,
        profile.adjustments,
        profile.metadata,
    )
    with pytest.raises(ValueError, match="objective priorities must sum to 1.0"):
        AdaptiveValidator().validate_profile(bad)


def test_full_integration_die_001_to_die_016():
    package = AdaptiveDecisionEngine().adapt(_temporal_package())
    assert package.selected_adaptive_result is not None
    assert package.metadata["module"] == "DIE-016"
    assert package.selected_adaptive_result.confidence >= 0.0


def _temporal_package():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    multi_objective_package = MultiObjectiveEngine().optimize(learning_package)
    strategic_package = StrategicPlanningEngine().plan(multi_objective_package)
    provenance_package = DecisionProvenanceEngine().build(strategic_package)
    governance_package = DecisionGovernanceEngine().evaluate(provenance_package)
    return TemporalDecisionEngine().track(governance_package)


def _scenario_package():
    decision_package = DIECore().process(
        {
            "query": "Select a reliable technical vendor with low risk and policy alignment",
            "semantic_results": [
                {"id": "e1", "text": "Vendor A has strong reliability and measurable value.", "confidence": 0.9},
                {"id": "e2", "text": "Vendor B has compliance concerns and uncertain delivery.", "confidence": 0.65},
            ],
            "metadata": {"constraints": [{"type": "policy", "severity": "medium"}]},
        }
    )
    alternative_package = AlternativeGenerator().generate(decision_package.decision_state)
    evaluated_package = DecisionEvaluator().evaluate(alternative_package)
    ranked_package = DecisionRanker().rank(evaluated_package)
    simulation_package = DecisionSimulator().simulate(ranked_package)
    explanation_package = ExplanationGenerator().explain(simulation_package)
    optimized_package = OptimizationEngine().optimize(explanation_package)
    uncertainty_package = UncertaintyEngine().analyze(optimized_package)
    return DecisionScenarioEngine().analyze(uncertainty_package)
