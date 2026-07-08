import pytest

from decision_engine.alternatives import (
    AlternativeDecision,
    AlternativeGenerator,
    AlternativePackageBuilder,
    AlternativeValidator,
)
from decision_engine.core import Constraint, DIECore, DecisionState, Evidence, Goal


def test_empty_decision_state_generates_package():
    package = AlternativeGenerator().generate(DecisionState())
    assert package.total_generated >= 3
    assert package.alternatives[0].supporting_evidence == ()


def test_minimal_decision_state_generates_alternatives():
    state = DecisionState(goals=(Goal("Choose a vendor"),), confidence=0.6)
    package = AlternativeGenerator().generate(state)
    assert package.alternatives
    assert package.generation_strategy == "deterministic_rule_based"


def test_generates_at_least_three_alternatives():
    package = AlternativeGenerator().generate(_rich_state())
    assert package.total_generated >= 3


def test_never_exceeds_seven_alternatives():
    package = AlternativeGenerator().generate(_rich_state())
    assert package.total_generated <= 7


def test_ids_are_unique():
    package = AlternativeGenerator().generate(_rich_state())
    ids = [alternative.alternative_id for alternative in package.alternatives]
    assert len(ids) == len(set(ids))


def test_confidence_is_normalized():
    state = DecisionState(
        evidence=(Evidence(id="e1", text="Strong evidence", confidence=90),),
        goals=(Goal("Choose architecture"),),
        confidence=85,
    )
    package = AlternativeGenerator().generate(state)
    assert all(0.0 <= alternative.confidence <= 1.0 for alternative in package.alternatives)
    assert package.alternatives[0].confidence == 0.85


def test_validator_catches_duplicate_ids():
    alternative = AlternativeDecision(
        alternative_id="duplicate",
        title="A",
        description="Description A",
        confidence=0.5,
        feasibility=0.5,
    )
    other = AlternativeDecision(
        alternative_id="duplicate",
        title="B",
        description="Description B",
        confidence=0.5,
        feasibility=0.5,
    )
    with pytest.raises(ValueError, match="Duplicate alternative IDs"):
        AlternativeValidator().validate((alternative, other), DecisionState())


def test_validator_catches_invalid_confidence():
    alternative = AlternativeDecision(
        alternative_id="alt-1",
        title="A",
        description="Description A",
        confidence=1.2,
        feasibility=0.5,
    )
    with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
        AlternativeValidator().validate((alternative,), DecisionState())


def test_package_builder_returns_correct_counts():
    state = _rich_state()
    package = AlternativeGenerator().generate(state)
    rebuilt = AlternativePackageBuilder().build(package.alternatives, decision_state=state)
    assert rebuilt.total_generated == len(package.alternatives)
    assert rebuilt.metadata["module"] == "DIE-002"


def test_end_to_end_integration_with_die_001():
    decision_package = DIECore().process(
        {
            "query": "Select a technical vendor within budget and policy limits",
            "semantic_results": [{"id": "e1", "text": "Vendor A has strong uptime.", "confidence": 0.9}],
            "metadata": {"constraints": [{"type": "policy", "severity": "high"}]},
        }
    )
    package = AlternativeGenerator().generate(decision_package.decision_state)
    assert package.total_generated >= 3
    assert package.alternatives[0].supporting_evidence


def _rich_state() -> DecisionState:
    return DecisionState(
        evidence=(
            Evidence(id="e1", text="Vendor A has strong reliability.", confidence=0.9),
            Evidence(id="e2", text="Vendor B has lower cost.", confidence=0.75),
        ),
        goals=(Goal("Choose the best vendor", priority="primary"), Goal("Reduce implementation risk", priority="secondary")),
        constraints=(Constraint(type="budget", severity="medium"), Constraint(type="policy", severity="high")),
        assumptions=("Demand remains stable.",),
        confidence=0.8,
    )
