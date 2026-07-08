from types import SimpleNamespace

from decision_engine.core import (
    ConstraintEngine,
    ContextLoader,
    DIECore,
    DecisionPackage,
    DecisionStateBuilder,
    EvidenceNormalizer,
    GoalExtractor,
)


def test_empty_context_does_not_crash():
    package = DIECore().process({})
    assert isinstance(package, DecisionPackage)
    assert package.goal_set
    assert package.confidence == 0.0
    assert package.decision_state.uncertainty == 1.0


def test_minimal_context_package_creates_decision_package():
    context = {"query": "Choose a vendor under budget", "confidence": 0.8}
    package = DIECore().process(context)
    assert package.goal_set[0].objective == "Choose a vendor under budget"
    assert package.processing_metadata["module"] == "DIE-001"


def test_evidence_is_normalized_and_deduplicated():
    loaded = ContextLoader().load(
        {
            "semantic_results": [
                {"text": "Vendor A has strong uptime.", "source": "search", "confidence": 0.9},
                {"text": "Vendor A has strong uptime.", "source": "search", "confidence": 0.7},
            ],
            "graph_results": [{"name": "Vendor B", "confidence": 75, "source": "graph"}],
        }
    )
    evidence = EvidenceNormalizer().normalize(loaded)
    assert len(evidence) == 2
    assert evidence[0].id
    assert evidence[0].confidence == 0.9
    assert evidence[1].confidence == 0.75


def test_goals_always_exist():
    goals = GoalExtractor().extract(ContextLoader().load({}))
    assert goals
    assert goals[0].priority == "primary"


def test_constraints_are_detected():
    loaded = ContextLoader().load({"query": "Pick an option with low legal risk and tight budget."})
    constraints = ConstraintEngine().extract(loaded)
    constraint_types = {constraint.type for constraint in constraints}
    assert {"legal", "risk", "budget"}.issubset(constraint_types)


def test_confidence_and_uncertainty_are_calculated():
    loaded = ContextLoader().load({"semantic_results": [{"text": "A", "confidence": 0.8}, {"text": "B", "confidence": 0.6}]})
    evidence = EvidenceNormalizer().normalize(loaded)
    goals = GoalExtractor().extract(loaded)
    state = DecisionStateBuilder().build(evidence, goals, (), loaded)
    assert state.confidence == 0.7
    assert state.uncertainty == 0.3
    assert state.metadata["evidence_count"] == 2


def test_process_works_end_to_end_with_object_context():
    context = SimpleNamespace(
        query=SimpleNamespace(text="Choose a compliant technical architecture within time constraints"),
        semantic_results=[SimpleNamespace(text="Architecture A integrates with current systems.", source="retriever", confidence=0.86)],
        graph_results=[{"fact": "Architecture A depends on service X", "source": "knowledge_graph", "confidence": 0.74}],
        metadata={"goals": ["Minimize implementation risk"], "constraints": [{"type": "policy", "severity": "high"}]},
        confidence_values={"retrieval": 0.8},
    )
    package = DIECore().process(context)
    assert isinstance(package, DecisionPackage)
    assert len(package.evidence_set) == 2
    assert package.goal_set
    assert package.constraint_set
    assert 0.0 <= package.confidence <= 1.0
