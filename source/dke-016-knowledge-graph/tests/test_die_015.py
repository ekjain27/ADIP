import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.governance import DecisionGovernanceEngine, GovernanceDecisionPackage, GovernanceMeshBuilder, PolicyRegistry
from decision_engine.learning import DecisionLearningEngine
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.provenance import DecisionProvenanceEngine
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import StrategicPlanningEngine
from decision_engine.temporal import (
    ChangeTracker,
    LineageLedger,
    RollbackManager,
    TemporalDecisionEngine,
    TemporalPackageBuilder,
    TemporalValidator,
    TimelineBuilder,
    VersionManager,
)
from decision_engine.uncertainty import UncertaintyEngine


def test_version_creation():
    versions = VersionManager().create_versions(_governance_package().selected_evaluation)
    assert len(versions) == 3
    assert versions[-1].status == "active"
    assert versions[1].parent_version == versions[0].version_id


def test_version_ordering():
    versions = VersionManager().create_versions(_governance_package().selected_evaluation)
    assert [version.version_number for version in versions] == [1, 2, 3]


def test_change_tracking():
    changes = ChangeTracker().track(_governance_package().selected_evaluation)
    assert {change.change_type for change in changes} >= {"governance_decision", "policy_update", "learning_update"}


def test_timeline_generation():
    evaluation = _governance_package().selected_evaluation
    versions = VersionManager().create_versions(evaluation)
    changes = ChangeTracker().track(evaluation)
    timeline = TimelineBuilder().build(versions, changes)
    assert timeline
    assert tuple(event.timestamp for event in timeline) == tuple(sorted(event.timestamp for event in timeline))


def test_rollback_point_generation():
    evaluation = _governance_package().selected_evaluation
    versions = VersionManager().create_versions(evaluation)
    rollback_points = RollbackManager().create_points(evaluation, versions)
    assert rollback_points
    assert RollbackManager().validate_target(rollback_points[0], versions)


def test_ledger_creation():
    ledger = LineageLedger().create(_governance_package().selected_evaluation)
    assert ledger.versions
    assert ledger.timeline
    assert ledger.active_version == ledger.versions[-1].version_id


def test_validator():
    ledger = LineageLedger().create(_governance_package().selected_evaluation)
    TemporalValidator().validate_ledger(ledger)


def test_empty_package():
    mesh = GovernanceMeshBuilder().build(PolicyRegistry().active_policies())
    empty = GovernanceDecisionPackage((), None, mesh, "empty")
    package = TemporalDecisionEngine().track(empty)
    assert package.temporal_results == ()
    assert package.selected_result is None


def test_invalid_ordering():
    ledger = LineageLedger().create(_governance_package().selected_evaluation)
    bad_versions = (ledger.versions[1], ledger.versions[0], *ledger.versions[2:])
    bad_ledger = type(ledger)(bad_versions, ledger.changes, ledger.timeline, ledger.rollback_points, ledger.active_version, ledger.metadata)
    with pytest.raises(ValueError, match="versions must be ordered"):
        TemporalValidator().validate_ledger(bad_ledger)


def test_full_integration_die_001_to_die_015():
    package = TemporalDecisionEngine().track(_governance_package())
    assert package.selected_result is not None
    assert package.selected_result.ledger.active_version
    assert package.metadata["module"] == "DIE-015"


def _governance_package():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    multi_objective_package = MultiObjectiveEngine().optimize(learning_package)
    strategic_package = StrategicPlanningEngine().plan(multi_objective_package)
    provenance_package = DecisionProvenanceEngine().build(strategic_package)
    return DecisionGovernanceEngine().evaluate(provenance_package)


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
